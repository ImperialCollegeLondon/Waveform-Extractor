Waveform Extractor v1.0.3 is compiled with PyInstaller and ready for Windows distribution. The package is downloadble at https://imperialcollegelondon.box.com/s/ncbg6oxqfu43raw4aez47hc9921adwde

The pre-compiled package disabled the debug mode for users' access to more detailed backend info. To enable the debug mode, simply execute the code 
```
python WaveformExtractor.py --debug
```
or
```
python WaveformExtractor.py -d
```
The debug script `debug_fourier.py` (to upload) allows you to visualise the reconstructed waveform against the original waveform.
