import logging
import multiprocessing
import os
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np

logger = logging.getLogger("demo")


def plot_figs(data, output_dir):
    """
    Save figures in output_dir for each 2D slice through data
    """
    # Prepare args for plot function calls
    args = []
    for i, data_slice in enumerate(data):
        title = f"level_{i:03d}"
        args.append((data_slice, title, output_dir))

    logger.info("Plotting %s figures", data.shape[0])
    with multiprocessing.Pool() as pool:
        pool.starmap(plot_single_figure, args)


def plot_single_figure(data_slice, title, output_dir):
    """
    Draw figure for 2D data array and save in output_dir
    """
    filename = output_dir / f"{title}.png"
    logger.info("Plotting %s with PID %s", filename, os.getpid())

    plt.imshow(data_slice)
    plt.title(title)
    plt.savefig(filename)
    plt.close()


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Set up plotting
    data = np.random.rand(10, 1000, 1000)
    output_dir = Path('/tmp') / 'figs'
    if not output_dir.is_dir():
        output_dir.mkdir()

    # Plot
    plot_figs(data, output_dir)
