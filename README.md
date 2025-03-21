# mido_webmidi_backend
A Web MIDI backend for Mido -  MIDI Objects for Python

This is a snippet showing how to load the package and list ports on pyodide:
```html
    <script type="text/javascript">
      async function main() {
        // bootstrap pyodide
        let pyodide = await loadPyodide();
        await pyodide.loadPackage('micropip');
        const micropip = pyodide.pyimport('micropip');
        await micropip.install('mido');
        await micropip.install(window.location.origin + '/mido_webmidi_backend-0.0.5-py3-none-any.whl');
        // bootstrap end
        console.log(pyodide.runPythonAsync(`
            import sys
            import mido
            import mido_webmidi_backend
            mido.set_backend('mido_webmidi_backend')
            await mido_webmidi_backend.init()
            print(f'Using backend module {mido.backend.module}')
            print(f'MIDI Inputs: {mido.get_input_names()}')
            print(f'MIDI Outputs: {mido.get_output_names()}')
        `));
      }
      main();
    </script>
```

## How to build package
```shell
pip install wheel && python setup.py bdist_wheel
```