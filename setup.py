from setuptools import setup, find_packages

# how to use:
# pip install wheel && python setup_backend.py bdist_wheel && cp dist/mido_webmidi_backend-*.whl ../jambuddy-browser/
#
setup(
    name='mido_webmidi_backend',
    version='0.0.1',
    url='https://github.com/pissalou/mido_webmidi_backend.git',
    author='Pascal Mazars',
    author_email='pascal.mazars@gmail.com',
    description='Web MIDI backend for Mido - MIDO Objects for Python (tested with pyodide 0.27.3)',
    packages=find_packages(),
    install_requires=['mido'],
)