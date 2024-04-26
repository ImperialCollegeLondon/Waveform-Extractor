# Waveform Extractor
## About
Waveform Extractor is a light-weight toolbox allowing you to extract any waveform $Q$ (preferably, periodic) from a raster figure and reconstruct into 21 Fourier terms (surely the code is scalable for any 2D regression method upon request),

$$Q_{\mathrm{recon}}(t) = \frac{1}{2} a_0 + \sum_{n=1}^{N/2} a_n \cos \left( n \cdot \frac{2 \pi}{T} \cdot t \right) + b_n \sin \left( n \cdot \frac{2 \pi}{T} \cdot t \right).$$

The code is inspired by Dr. Zhuo Cheng's in-house `MATLAB` code initially developed in 2007. The new version  
- incoporates a simple `tkinter`-based user interface for i/o path selection and data input,
- incoporates a data point removal feature (right mouse button) allows users to revoke any wrongly labelled points on the current canvas, and
- fixed an inherited hidden bug in the original `MATLAB` code, which would result in unreasonable $y$-shifting under the presence of negative-valued data.

## To Use
The directory `/asset` provides three figures for the rapid testing purposes. 

Waveform Extractor v1.0.3 is also compiled with PyInstaller and ready for the *Windows* distribution. The package is downloadble at https://imperialcollegelondon.box.com/s/ncbg6oxqfu43raw4aez47hc9921adwde.

Note: the pre-compiled package disabled the debug mode for users' access to more detailed backend info. To enable the debug mode, simply execute the code 
```
python WaveformExtractor.py --debug
```
or
```
python WaveformExtractor.py -d
```
The debug script `debug_fourier.py` (to upload) allows you to visualise the reconstructed waveform against the original waveform.

last update: 26/04/2024
