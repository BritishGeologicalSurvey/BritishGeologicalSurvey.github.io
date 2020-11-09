import logging
from multiprocessing import Pool
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np

logger = logging.getLogger("demo")


def plot_figs(data, output_dir):
    """
    Save figures in output_dir for each 2D slice through data
    """
    logger.info("Plotting %s figures", data.shape[0])
    for i, data_slice in enumerate(data):
        title = f"level_{i:03d}"
        plot_single_figure(data_slice, title, output_dir)


def plot_single_figure(data_slice, title, output_dir):
    """
    Draw figure for 2D data array and save in output_dir
    """
    filename = output_dir / f"{title}.png"
    logger.info("Plotting %s", filename)

    fig, ax = plt.subplots()
    ax.imshow(data_slice)
    ax.set_title(title)
    fig.savefig(filename)
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
