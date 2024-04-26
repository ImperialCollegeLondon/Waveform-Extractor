import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# end point of x-axis in the figure
x_end_fig = 0.8;

# .npy files are saved in the output folder under debug mode
fourier_coeff = np.load('./output/fourier_coeff.npy');
scaled_points = np.load('./output/scaled_coords.npy');

n_coeff = fourier_coeff.shape[0];
yy = fourier_coeff[0][0]/2;
tt = np.linspace(0, x_end_fig, 1000);
for i in range(1, n_coeff):
    yy += (fourier_coeff[i][0] * np.cos(2 * (np.pi/tt[-1]) * i * tt) + fourier_coeff[i][1] * 
                        np.sin(2 * (np.pi/tt[-1]) * i * tt));

plt.figure(figsize=(5, 2.5));
plt.plot(tt, yy, color="b", lw=2, label="fittted curve");
plt.scatter(scaled_points[:,0], scaled_points[:,1], c='orange', s=20, alpha=0.5, label="points taken");
plt.legend(); plt.grid();
plt.show();