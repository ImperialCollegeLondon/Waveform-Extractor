'''
History:
    Date            Programmer      Description
    ----------      ----------      ----------------------------
    03/04/2024      B LI            create files
    05/04/2024      B LI            return row_idx in generte_entries and generate_checkbuttons
    20/04/2024      B LI            geenrate_checkbuttons add entry paddings
'''
import tkinter as tk


def generte_entries(root, fields, row_start=1):
    # fields: dictionary of field names and units
    entries = [];
    row_idx = row_start;
    for field in fields:
        tk.Label(root, text=field).grid(row=row_idx, column=0);
        entries.append(tk.Entry(root));
        entries[-1].grid(row=row_idx, column=1);
        tk.Label(root, text=fields[field]).grid(row=row_idx, column=2, padx=10, pady=3, sticky='w');
        row_idx += 1;
    return entries, row_idx;

def generate_checkbuttons(root, fields, row_start=1):
    # fields: list of field names
    checkbuttons = [];
    row_idx = row_start;
    for field in fields:
        checkbuttons.append(tk.IntVar());
        tk.Checkbutton(root, text=field, variable=checkbuttons[-1]).grid(row=row_idx, column=3);
        row_idx += 1;
    return checkbuttons, row_idx;

def get_params(entries):
    '''
    parse entries to get user input, param is a 1d array of floats
    '''
    
    params = [];
    for entry in entries:
        for data in entry:
            params.append(float(data.get()));
    return params;