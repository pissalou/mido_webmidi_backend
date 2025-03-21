import sys
import mido
from mido.ports import BaseInput, BaseOutput

if sys.platform != 'emscripten':
    raise OSError('This backend is only available in a browser')
try:
    import js
except ImportError as e:
    raise RuntimeError(e.msg if "pyodide" in sys.modules else "Pyodide not found in modules")

_midiaccess = None


async def init():
    def onmidiaccesssuccess(midiaccess):
        print(f'Received midi access {midiaccess}. It is available in JS via globalThis.__midiAccess and in Python via mido.backend.module._midiaccess')
        js.globalThis.__midiAccess = midiaccess
        global _midiaccess
        _midiaccess = midiaccess

    if js.navigator.requestMIDIAccess:
        print('Requesting MIDI access...')
        await js.navigator.requestMIDIAccess().then(onmidiaccesssuccess, lambda: print('MIDI support rejected, MIDI will not be available'))


class Input(BaseInput):
    def __init__(self, name, **kwargs):
        print(f'Opening input {name}({kwargs})...')
        self.name = name
        # we could also just store the portID, instead we keep a dict of all the available info from webmidi
        self._webmidi_portinfo = [device for device in get_devices() if device['name'] == name and device['is_input']][0]
        BaseInput.__init__(self, name, **kwargs)

    def onmidimessage(self, msg_bytes: [int]):
        print(f'Received MIDIMessageEvent {msg_bytes.data}...')
        # convert to mido.Message directly from bytes does not work because slice subscripting is not implemented
        # for typed arrays in pyodide yet. Hence, the little workaround below:

        def format_hex(dec):
            return '0' + hex(dec)[2:] if dec < 16 else hex(dec)[2:]
        hex_data = f'{format_hex(msg_bytes.data[0])} {format_hex(msg_bytes.data[1])} {format_hex(msg_bytes.data[2])}'
        print(hex_data)
        mido_msg = mido.Message.from_hex(hex_data)
        # mido_msg = mido.Message.from_bytes(data=msg_bytes.data)  # not possible yet
        print(mido_msg)  # TODO send mido_msg as arg to callback
        self._callback(msg_bytes)

    def _open(self, **kwargs):
        if kwargs.get('virtual'):
            raise ValueError('virtual ports are not supported')
        if kwargs.get('callback'):
            self._callback = kwargs['callback']
            if not callable(self._callback):
                raise ValueError('callback is not callable')
            global _midiaccess
            self._webmidi_port = _midiaccess.inputs.get(self._webmidi_portinfo['id'])
            self._webmidi_port.onmidimessage = self.onmidimessage
            self._webmidi_port.open()
            self.closed = False
        else:
            raise ValueError('callback is mandatory')
            # we could also offer a default callback
            # self._callback = lambda msg: print(f'Received {msg}')

    def _receive(self, block=True):
        raise OSError('Only callback is supported')

    def _close(self):
        self._webmidi_port.close()


class Output(BaseOutput):
    def __init__(self, name, **kwargs):
        BaseOutput.__init__(self, name, **kwargs)
        print(f'Opening output {name}({kwargs})...')
        self._webmidi_portinfo = [device for device in get_devices() if device['name'] == name and device['is_output']][0]
        global _midiaccess
        self.name = name
        self._webmidi_port = _midiaccess.inputs.get(self._webmidi_portinfo['id'])

    def _open(self, **kwargs):
        print(f'Opening output {self.name}({kwargs})...')
        self._webmidi_port.open()

    def _send(self, msg):
        self._webmidi_port.send(msg)

    def _close(self):
        print(f'Closing output {self.name}...')
        self._webmidi_port.close()


def get_devices(**kwargs):
    """Return a list of devices as dictionaries."""
    while not js.globalThis.hasOwnProperty('__midiAccess'):
        print('Wait for MIDI access...')
        init()
    if js.globalThis.hasOwnProperty('__midiAccess'):
        _midiaccess = js.globalThis.__midiAccess
        inputs = [{'id': port.id, 'name': port.name, 'manufacturer': port.manufacturer, 'state': port.state,
                   'connection': port.connection, 'is_input': True, 'is_output': False} for port in _midiaccess.inputs.values()]
        outputs = [{'id': port.id, 'name': port.name, 'manufacturer': port.manufacturer, 'state': port.state,
                    'connection': port.connection, 'is_input': False, 'is_output': True} for port in _midiaccess.outputs.values()]
        results = inputs
        results.extend(outputs)
        # print(f'Devices found: {results}')
        return results
    print('No MIDI access. Returning empty device list')
    return []
    # minimal working example result
    # return [{
    #    'name': 'Some MIDI Input Port',
    #    'is_input': True,
    #    'is_output': False,
    # }]


# import * is broken unless we explicitly define `__all__`
#  __all__ = ['get_devices', 'Input', 'Output']
