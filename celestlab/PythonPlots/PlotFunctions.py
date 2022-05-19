import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from PIL import Image
from math import prod
import os


# Function to prepare output folder and return path
def get_plot_path(target_folder):
    path = os.path.dirname(os.path.realpath(__file__)).replace("PythonPlots", target_folder)
    os.makedirs(os.path.dirname(os.path.realpath(__file__)) + "/" + target_folder, exist_ok=True)
    return path


# Function to open csv file and convert data to float array
def open_csv(path, target_file, is_string=False):
    tmp = []
    with open(path + "\\" + target_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if is_string:
                tmp.append(','.join(row))
            else:
                if len(row) == 1:
                    tmp.append(float(row[0]))
                else:
                    tmp.append([float(ii) for ii in row])
    if is_string:
        return tmp
    else:
        return np.array(tmp)


# Functions for figures
def dark_figure(subplots=(1, 1), figsize=(7, 5.2)):
    fig = plt.figure(facecolor='#0D1117', figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor='#0D1117'))
        axes[ii].tick_params(axis='x', colors='white', which='both')
        axes[ii].tick_params(axis='y', colors='white', which='both')
        axes[ii].yaxis.label.set_color('white')
        axes[ii].xaxis.label.set_color('white')
        axes[ii].title.set_color('white')
        axes[ii].grid(color='#161C22', linewidth=0.5)
        for i in axes[ii].spines:
            axes[ii].spines[i].set_color('white')
    return fig, axes


def light_figure(subplots=(1, 1), figsize=(7, 5.2)):
    fig = plt.figure(facecolor='white', figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor='white'))
        axes[ii].tick_params(axis='x', colors='black', which='both')
        axes[ii].tick_params(axis='y', colors='black', which='both')
        axes[ii].yaxis.label.set_color('black')
        axes[ii].xaxis.label.set_color('black')
        axes[ii].title.set_color('black')
        axes[ii].grid(color='lightgrey', linewidth=0.5)
        for i in axes[ii].spines:
            axes[ii].spines[i].set_color('black')
    return fig, axes


def finish_dark_figure(fig, path, show=True):
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.20)
    fig_axes1 = fig.add_axes([0.772, 0.01, 0.22, 0.3], anchor='SE', zorder=1)
    Badge_TOLOSAT_dark = Image.open('assets/TOLOSAT_dark.png')
    fig_axes1.imshow(Badge_TOLOSAT_dark)
    Badge_TOLOSAT_dark.close()
    fig_axes1.axis('off')
    fig_axes2 = fig.add_axes([0.02, 0.02, 1, 1], anchor='SW', zorder=1)
    fig_axes2.text(0, 0, datetime.now(timezone.utc).strftime("Plot generated on %Y/%m/%d at %H:%M:%S UTC."),
                   color='dimgray')
    fig_axes2.axis('off')
    plt.savefig(path, transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def finish_light_figure(fig, path, show=True):
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.20)
    fig_axes1 = fig.add_axes([0.772, 0.01, 0.22, 0.3], anchor='SE', zorder=1)
    Badge_TOLOSAT_light = Image.open('assets/TOLOSAT_light.png')
    fig_axes1.imshow(Badge_TOLOSAT_light)
    Badge_TOLOSAT_light.close()
    fig_axes1.axis('off')
    fig_axes2 = fig.add_axes([0.02, 0.02, 1, 1], anchor='SW', zorder=1)
    fig_axes2.text(0, 0, datetime.now(timezone.utc).strftime("Plot generated on %Y/%m/%d at %H:%M:%S UTC."),
                   color='silver')
    fig_axes2.axis('off')
    plt.savefig(path, transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def flip_legend(ncol, reverse=False, handles_in=None, labels_in=None):
    if handles_in is None and labels_in is None:
        handles_, labels_ = plt.gca().get_legend_handles_labels()
    else:
        handles_ = handles_in
        labels_ = labels_in
    handles_ = [k for j in [handles_[i::ncol] for i in range(ncol)] for k in j]
    labels_ = [k for j in [labels_[i::ncol] for i in range(ncol)] for k in j]
    if reverse:
        return handles_[::-1], labels_[::-1]
    else:
        return handles_, labels_


def flatten(list_of_lists):
    flattened_list = []
    for i in list_of_lists:
        if isinstance(i, list):
            flattened_list += i
        else:
            flattened_list.append(i)
    return flattened_list
