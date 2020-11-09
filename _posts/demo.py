from multiprocessing import Pool
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np


def plot_figs(data, output_dir):
    """
    Save figures in output_dir for each 2D slice through data
    """
    pass


def plot_single_figure(data_slice, filename):
    """
    Draw figure for 2D data array and save as filename
    """
    pass


if __name__ == '__main__':
    data = np.random.rand(10, 10, 10)
    output_dir = Path('/tmp') / 'figs'
    if not output_dir.is_dir():
        output_dir.mkdir()

    plot_figs(data, output_dir)
