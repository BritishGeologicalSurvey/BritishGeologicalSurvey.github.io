from itertools import count, islice, repeat
import logging
import multiprocessing
import os
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo")


def plot_figs(data, output_dir):
    """
    Save figures in output_dir for each 2D slice through data
    """
    # Prepare args for plot function calls
    # args is a tuple of generators
    args = zip(
        data,
        (f"level_{i:03d}" for i in count()),
        repeat(output_dir)
        )

    logger.info("Plotting %s figures", data.shape[0])
    with multiprocessing.get_context('spawn').Pool() as pool:
        pool.starmap(plot_single_figure, args)


def plot_single_figure(data_slice, title, output_dir):
    """
    Create figure for 2D data array and save in output_dir
    """
    filename = output_dir / f"{title}.png"
    logger.info("Plotting %s with PID %s", filename, os.getpid())

    fig = draw_plot(data_slice)
    plt.title(title)
    fig.savefig(filename)
    plt.close(fig)


def draw_plot(data_slice):
    """
    Draw the main plot
    """
    fig = plt.figure()
    plt.imshow(data_slice)
    return fig


if __name__ == '__main__':
    # Set up plotting
    data = np.random.rand(10, 1000, 1000)
    output_dir = Path('/tmp') / 'figs'
    if not output_dir.is_dir():
        output_dir.mkdir()

    # Plot
    plot_figs(data, output_dir)
