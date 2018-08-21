#!/usr/bin/python3
import os
from csv import DictReader
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog

import numpy as np
import matplotlib
from matplotlib.dates import date2num, num2date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2TkAgg)

#Write a function that accepts a beginning date and time
# and an ending date and time. Inclusive of those dates
# and times, return the coefficient of the slope of the
# barometric pressure.

class WeatherStatistics:
    def __init__(self, master):
        self.datetime_list, self.barpress_list = [], []
        self.barpress_array = []
        self.datetime_array = []
        self.start_idx = 0
        self.end_idx = 0

        # Build the GUI
        master.title('Weather Statistics')
        master.resizable(True, True)
        master.state('zoomed')

        # Menu Bar
        menubar = Menu(master)
        master.config(menu=menubar)
        file = Menu(menubar)
        help_ = Menu(menubar)
        menubar.add_cascade(menu=file, label='File')
        menubar.add_cascade(menu=help_, label='Help')
        file.add_command(label='Load', command=self.load_data)

        # Frame to collect the data
        self.frame_data = ttk.Frame(master)
        self.frame_data.pack()

        ttk.Label(self.frame_data, text='(YYYY-MM-DD HH:MM:SS)', font='Courier 12').grid(row=0, column=1, padx=50, sticky='s')
        ttk.Label(self.frame_data, text='(YYYY-MM-DD HH:MM:SS)', font='Courier 12').grid(row=0, column=3, padx=50, sticky='s')

        ttk.Label(self.frame_data, text='Start:').grid(row=1, column=0, padx=5)
        self.entry_start = StringVar()
        ttk.Entry(self.frame_data, width=19, textvariable=self.entry_start).grid(row=1, column=1)

        ttk.Label(self.frame_data, text='End:').grid(row=1, column=2, padx=5)
        self.entry_end = StringVar()
        ttk.Entry(self.frame_data, width=19, textvariable=self.entry_end).grid(row=1, column=3)

        ttk.Button(self.frame_data, text='Calculate', command=self.calculate).grid(row=3, column=0, columnspan=4, pady=10)

        # Frame to print the results
        self.frame_graphic = ttk.Frame(master)
        self.frame_graphic.pack()

        # Canvas
        matplotlib.rc('font', size=18)
        f = Figure()
        f.set_facecolor((0,0,0,0))
        self.a = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f,self.frame_graphic)
        self.canvas.draw()
        toolbar_frame = ttk.Frame(self.frame_graphic)  # needed to put navbar above plot
        toolbar = NavigationToolbar2TkAgg(self.canvas, toolbar_frame)
        toolbar.update()
        toolbar_frame.pack(side=TOP, fill=X, expand=0)
        self.canvas._tkcanvas.pack(fill=BOTH, expand=1)


    def load_data(self):
        data_path = filedialog.askdirectory()
        file_list = os.listdir(data_path)
        for file in file_list:
            datetime_re = re.compile(r'[\d]{2,4}')  # regex to get datetime info
            print('Loading {} file'.format(file) )
            with open(data_path + '/' + file, 'r') as file_obj:
                for row in DictReader(file_obj, delimiter='\t'):
                    self.barpress_list.append(float(row['Barometric_Press']))
                    self.datetime_list.append(
                        date2num(datetime(*list(map(int, datetime_re.findall(row['date       time    ']))))))

        self.datetime_array = np.array(self.datetime_list)
        self.barpress_array = np.array(self.barpress_list)
        self.entry_start.set(str(num2date(self.datetime_array[0]))[0:19])
        self.entry_end.set(str(num2date(self.datetime_array[-1]))[0:19])

        self.calculate()

    def calculate(self):
        # get user input
        try:
            start_num = date2num(datetime(*list(map(int, re.findall(r'[\d]{1,4}', self.entry_start.get())))))
            end_num = date2num(datetime(*list(map(int, re.findall(r'[\d]{1,4}', self.entry_end.get())))))
        except Exception as e:
            messagebox.showerror(title='Invalid Date Values', message=e)
            return

        self.start_idx = np.searchsorted(self.datetime_array, start_num)
        self.end_idx = np.searchsorted(self.datetime_array, end_num)

        if self.end_idx <= self.start_idx:
            messagebox.showerror(title='Invalid Input Values',
                                 message='End Date must be after Start Date')
            return

        dy = self.barpress_array[self.end_idx] - self.barpress_array[self.start_idx]
        dt = self.datetime_array[self.end_idx] - self.datetime_array[self.start_idx]

        slope = dy / dt

        # plot data & slope line
        self.a.clear()
        self.a.plot_date(self.datetime_array[self.start_idx:self.end_idx],
                         self.barpress_array[self.start_idx:self.end_idx], linewidth=2)
        self.a.plot([self.datetime_array[self.start_idx], self.datetime_array[self.end_idx]],
                    [self.barpress_array[self.start_idx], self.barpress_array[self.end_idx]],
                    color='k', linestyle='-', linewidth=2)
        self.a.set_ylabel('Barometric Pressure (inHg)')
        self.a.set_xlabel('Date')

        # add colored slope value to figure
        color = 'green' if (slope >= 0) else 'red'
        text_x = self.datetime_array[self.start_idx] + (self.datetime_array[self.end_idx] - self.datetime_array[self.start_idx])/2
        text_y = self.barpress_array[self.start_idx] + (self.barpress_array[self.end_idx] - self.barpress_array[self.start_idx])/2
        self.a.text(text_x, text_y, '{0:.6f} inHg/day'.format(slope),
                    fontsize=16, horizontalalignment='center',
                    bbox=dict(facecolor=color))

        self.canvas.draw()

def main():
    root = Tk()
    app = WeatherStatistics(root)
    root.mainloop()

if __name__ == "__main__": main()
