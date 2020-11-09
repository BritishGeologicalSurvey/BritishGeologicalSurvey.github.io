import numpy as np

from demo import plot_figs


def test_plot_figs_produces_files(tmp_path):
    # Arrange
    test_data = np.random.rand(2, 2, 2)
    expected_files = {'level_000.png', 'level_001.png'}

    # Act
    plot_figs(test_data, tmp_path)

    # Assert
    output_files = [p.name for p in tmp_path.iterdir()]
    assert set(output_files) == expected_files
