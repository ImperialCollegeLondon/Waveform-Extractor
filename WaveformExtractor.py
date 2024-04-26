'''
History:
    Date            Programmer      Description
    ----------      ----------      ----------------------------
    03/04/2024      B LI            create
    06/04/2024      B LI            create WaveformExtractor
    14/04/2024      B LI            add undo function to _take_points
    15/04/2024      B LI            v1.0.0 add loggers, clean the code
    16/04/2024      B LI            v1.0.1 debug _fcalc fix bugs in plotting
    17/04/2024      B LI            v1.0.2 debug _fcalc, test fitting, add argparse
    18/04/2024      B LI            v1.0.3 format output, debug build errors
'''
__version__ = "1.0.3";
__release__ = "18/04/2024";

import logging
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backend_bases import MouseButton
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from utils.tkutils import generte_entries, generate_checkbuttons

class WaveformExtractor:
    
    def __init__(self, debug=False):
        Path("./output").mkdir(parents=True, exist_ok=True)
        logging.info("THIS IS WAVEFORM EXTRATOR {}, release {}".format(__version__, __release__));
        self.root = tk.Tk();
        self.root.title("Waveform Fourier User Input");
        self.filename = None;
        self.debug = debug;
        
    def set_main_window(self):
        self.row_idx = 2;
        # entries
        entry_lst = {
            "x start": "[AU]",
            "x end": "[AU]",
            "y start": "[AU]",
            "y end": "[AU]"};
        self.entries, self.row_idx = generte_entries(self.root, entry_lst, 2);

        # Create a file label
        self.label_file= tk.Label(self.root, 
                                    text = "Open a figure",
                                    width = 60, height = 2,
                                    fg = "blue");
        self.label_file.grid(row = self.row_idx+1, columnspan = 4);
    
        button_explore = tk.Button(self.root, 
                                text = "Browse Files",
                                command = (lambda: self._browse_files()));
        button_explore.grid(row = self.row_idx+2);

        # calculate, diaabled until file is selected
        self.calc = tk.Button(self.root, text="Fit!", command=(lambda: self._sequential()));
        self.calc.grid(row=self.row_idx+2, column=1);
        self.calc["state"] = tk.DISABLED;
        
        # preview
        self.preview = tk.Button(self.root, text="preview", command=(lambda: self._preview_image()));
        self.preview.grid(row=self.row_idx+2, column=2);
        self.preview["state"] = tk.DISABLED;
        
        # cancel button
        cancel = tk.Button(self.root, text="cancel", command=self.root.destroy)
        cancel.grid(row=self.row_idx+2, column=3);
        
        # if file is selected, update label and buttons
        if self.filename is not None:
            self.label_file.configure(text=self.filename);
            self.calc["state"] = tk.NORMAL;
            self.preview["state"] = tk.NORMAL;
        
    def _browse_files(self):
        self.filename = filedialog.askopenfilename(initialdir = "./",
                                          title = "Select a File to open",
                                          filetypes = (("PNG files", "*.png*"),
                                                        ("JPEG files", "*.jpg*"),
                                                       ("all files", "*.*")));
        # callback and update
        self.set_main_window();

    def _preview_image(self):
        try:
            self.img = np.asarray(Image.open(self.filename));
            logging.info("file opened successfully");
        except:
            logging.error("Could not open file");
            tk.messagebox.showerror("Error", "Could not open file");
            self.filename = None;
            self.set_main_window();
            return;
        plt.figure();
        plt.title("Preview of the selected image\n close to continue");
        plt.imshow(self.img);
        plt.axis('off');
        plt.show();
        
    def _mandatory_fields(self):
        '''
        check if all fields are filled
        '''
        self.reset = False;
        params = [];
        
        for entry in self.entries:
            if entry.get():
                params.append(entry.get());
            else:
                logging.error("All fields are mandatory");
                tk.messagebox.showerror("Error", "All fields are mandatory");
                self.reset = True;
                break;
            
        if self.reset:
        # clear all entries but keep the files selected
            self.set_main_window();
        else:
            self.params = params; 
    
    def _sequential(self):
        self._mandatory_fields();
        if not self.reset:
            self.root.quit();
            self._take_points();
            if self.scaled_points is not None:
                self._fcalc();
                if self.fourier_coeff is not None:
                    self._save_to_file();
    
    def _take_points(self):
        logging.info("taking in graphical input");

        x_start_real = float(self.params[0]);
        x_end_real = float(self.params[1]);
        y_start_real = float(self.params[2]);
        y_end_real = float(self.params[3]);
        
        # should load the image again regardless of preview
        try:
            img = np.asarray(Image.open(self.filename));
        except:
            tk.messagebox.showerror("Error", "Could not open file");
            self.filename = None;
            self.set_main_window();
            return;
        
        x_range_real = x_end_real - x_start_real;
        y_range_real = y_end_real - y_start_real;

        logging.debug("real x range: {}\n real y range: {}".format(x_range_real, y_range_real));

        #===============================================================================
        # STEP 1 - select x_start, x_end, y_start, y_end
        #===============================================================================
        def _undo(event):
            '''
            this function is solely used by plt button_press_event, 
            to remove the last point and its corresponding h/v lines from the figure, 
            and performs iteration decrement. Do not modify the argument.
            '''
            nonlocal xy, hlines, vlines, i, dots;
            
            # click the right button to undo
            if event.button is MouseButton.RIGHT:
                
                # check if there is anything to undo
                if (len(xy) > 0):

                    xy.pop(-1);
                    dots.pop().remove();
                    hlines.pop().remove();
                    vlines.pop().remove();
                    plt.draw();
                    i -= 1;
                                        
                    # update title
                    title = "click on the AXIS where " + cues[i];
                    plt.title(title, color=cscheme[i]);
                    plt.draw();

                    logging.debug("current step is {}\n lenth of xy: {}\n length of hlines, vlines: {}, {}\n"
                                  .format(i, len(xy), len(hlines), len(vlines)));
                else:
                    print("Nothing to undo");
        #===============================================================================
        # load figure, begin taking points	
        f = plt.figure();

        cues    = ["x = x_start", "x = x_end", 
                   "y = y_start", "y = y_end"];
        cscheme = ["blue", "red", "green", "purple"];

        plt.imshow(img);
        plt.axis('off');

        xy      = [];
        hlines  = [];
        vlines  = [];
        dots    = [];

        # connect to the plt event function
        cid = plt.connect('button_press_event', _undo);

        i = 0;
        while i < 4:
            logging.debug("current step is {}\n lenth of xy: {}\n length of hlines, vlines: {}, {}\n"
                          .format(i, len(xy), len(hlines), len(vlines)));
            
            # update title
            title = "click on the AXIS where " + cues[i];
            plt.title(title, color=cscheme[i]);
            plt.draw();
            
            # take in points
            p = plt.ginput(1, show_clicks=True, timeout=0, mouse_add=MouseButton.LEFT, mouse_pop=None, mouse_stop=None);
            
            xy.append([p[0][0], p[0][1]]);
            
            # add scatters and lines
            dots.append(plt.scatter(p[0][0], p[0][1], c=cscheme[i], s=40, alpha=0.5));
            hlines.append(plt.axhline(y=p[0][1], color=cscheme[i], linestyle='--'));
            vlines.append(plt.axvline(x=p[0][0], color=cscheme[i], linestyle='--'));
            plt.draw();
            
            i += 1;
            
        plt.draw();
        plt.disconnect(cid);

        x_range_fig = np.abs(xy[1][0] - xy[0][0]);
        y_range_fig = np.abs(xy[3][1] - xy[2][1]);

        if self.debug:
            np.save('./output/xy.npy', np.array(xy));

        #===============================================================================
        # STEP 2 - take m points
        #===============================================================================
        def _undo1(event):
            '''
            this function is solely used by plt button_press_event, 
            to remove the last point from the figure, reset the assistive line,
            and performs iteration decrement. Do not modify the argument.
            '''
            nonlocal points, points_plot, line_curr, i;
            
            # click the right button to undo
            if event.button is MouseButton.RIGHT:
                
                # check if there is anything to undo
                if (len(points) > 0):
                    
                    # remove the last point from the list
                    points.pop(-1);
                    
                    # counter decrement
                    i -= 1;

                    # remove the last point from the plot,
                    # recover the prev. vertical assistive line
                    points_plot.pop().remove();
                    line_curr.remove();
                    line_curr = plt.axvline(x=(xy[0][0] + x_step * i), color='red', linestyle='--', linewidth=1);                 
                                        
                    # update title
                    header = "click on the intersect between the vertical line and the figure,\n You have {terms} terms left".format(terms=(nterms+1-i));
                    plt.title(header, color='black');
                    plt.draw();

                    logging.debug("current step is {}\n size of the points is {}".format(i, len(points)));
                else:
                    print("Nothing to undo");
        #==============================================================================
        # clear vertical lines
        for i in range(4):
            hlines.pop().remove();
            vlines.pop().remove();

        # connect to the plt event function
        cid = plt.connect('button_press_event', _undo1);
        
        # add vertical assistive lines, mind the Nyquist rate
        nterms      = 49;
        x_step      = x_range_fig / nterms;

        # take user inputs
        points      = [];
        points_plot = [];

        i = 0;
        line_curr = plt.axvline(x=(xy[0][0] + x_step * 0), color='red', linestyle='--', linewidth=0.5);
        while i < (nterms + 1):
            
            logging.debug("current step is {}\n size of the points is {}".format(i, len(points)));

            # update title
            header = "click on the intersect between the vertical line and the figure,\n You have {terms} terms left".format(terms=(nterms+1-i));
            plt.title(header, color='black');
            plt.draw();
            
            # take in points and add scatters
            p = plt.ginput(1, show_clicks=True, timeout=0, mouse_add=MouseButton.LEFT, mouse_pop=None, mouse_stop=None);
            points.append([p[0][0], p[0][1]]);
            points_plot.append(plt.scatter(p[0][0], p[0][1], c='orange', s=20, marker='+'));

            i += 1;

            # advance the vertical assistive line
            line_curr.remove();
            line_curr = plt.axvline(x=(xy[0][0] + x_step * i), color='red', linestyle='--', linewidth=1);
        
        plt.disconnect(cid);
        plt.title("point selection is now complete \n close the window to proceed", color='black');
        plt.draw();
        plt.show();
        #===============================================================================
        # STEP 3 - shifting and scaling
        #===============================================================================
        x_SF = x_range_real / x_range_fig;
        y_SF = y_range_real / y_range_fig;

        points = np.array(points);
        scaled_points = np.zeros((points.shape[0], points.shape[1]));

        # shift and scale x points
        scaled_points[:, 0] = points[:, 0] - xy[2][0];
        scaled_points[:, 0] = (scaled_points[:, 0] - scaled_points[0][0]) * x_SF;

        # shift and scale y points
        scaled_points[:, 1] = (xy[2][1] - points[:, 1]) * y_SF + y_start_real;

        self.unscaled_points = points;
        self.scaled_points = scaled_points;
        
    def _fcalc(self, n_coeff=21):
        '''
        code partially taken and modified from: https://stackoverflow.com/questions/64165282/determining-fourier-coefficients-from-time-series-data
        '''
        logging.info("calculating fourier coefficients");

        def create_fourier_series(x, coefficients):
            fourier_series = coefficients[0][0] / 2;
            for n in range(1, n_coeff):
                fourier_series += (fourier_coeff[n][0] * np.cos(2 * np.pi/x[-1] * n * x) + fourier_coeff[n][1] * np.sin(2 * np.pi/x[-1] * n * x));
            return fourier_series

        # Set the number of Fourier coefficients to use.
        n_bins = self.scaled_points[:,1].shape[0];
        yy = self.scaled_points[:,1].reshape(n_bins);
        tt = self.scaled_points[:,0].reshape(n_bins);

        # Determine the fast Fourier transform for this test data.
        fast_fourier_transform = np.fft.fft(yy);

        # Loop through the FFT and pick out the a and b coefficients, which are the real and imaginary parts of the coefficients calculated by the FFT.
        fourier_coeff = [];
        for n in range(0, n_coeff):
            a = 2 * fast_fourier_transform[n].real / n_bins;
            b = -2 * fast_fourier_transform[n].imag / n_bins;
            fourier_coeff.append([a, b]);
        self.fourier_coeff = fourier_coeff;
        
        # Create the Fourier series approximating this data.
        fourier_series = create_fourier_series(tt, fourier_coeff);
        
        # Create a figure to view the data.
        fig, ax = plt.subplots(1, 1, figsize=(6, 6));
        ax.scatter(tt, yy, color="k", s=1);
        ax.plot(tt, fourier_series, color="b", lw=0.5);
        
        logging.info("Fourier coefficients calculated successfully, saved to file.");
        tk.messagebox.showinfo("Success", "Fourier coefficients calculated successfully, saved to file.");
        plt.show();
        
    def _save_to_file(self):
        logging.info("saving coefficients to file");
        with open("./output/fourier_params.txt", "w") as f:
            f.write("Fourier Coefficients: \n");
            for i in range (len(self.fourier_coeff)):
                f.write("a{:02d}in= {}\nb{:02d}in= {}\n".format(i, self.fourier_coeff[i][0], i, self.fourier_coeff[i][1]));
        
        if self.debug:
            logging.debug("saving Fourier coefficeints to fourier.npy:\n");
            np.save('./output/fourier_coeff.npy', self.fourier_coeff);
            logging.debug("saving coordinates taken to unscaled_coords.npy:\n");
            np.save('./output/unscaled_coords.npy', np.array(self.unscaled_points));
            logging.debug("saving coordinates taken to scaled_coords.npy:\n");
            np.save('./output/scaled_coords.npy', self.scaled_points);
        
        logging.info("file(s) saved successfully");
        tk.messagebox.showinfo("Success", "File(s) saved successfully");
    
    def run(self):
        self.root.mainloop();

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Waveform Fourier User Input");
    parser.add_argument("-d", "--debug", action="store_true", help="set debug mode");
    args = parser.parse_args();
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG, 
            format="%(levelname)s | %(asctime)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S");
    else:
        logging.basicConfig(
            level=logging.INFO, 
            format="%(levelname)s | %(asctime)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S");
    
    a = WaveformExtractor(debug=args.debug);
    a.set_main_window();
    a.run();