# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)
from pathlib import Path

from plopp.widgets import HBar, VBar


def fetch_data(name: str, quiet=True) -> str:
    """
    Fetch pre-prepared data from a remote source and return the path to the folder
    containing the extracted files.

    Parameters
    ----------
    name:
        Name of the dataset to fetch. This corresponds to the name of the zip file
        without the ".zip" extension.
    quiet:
        If True, suppresses logging output. Defaults to True.
    """
    import pooch

    logger = pooch.get_logger()
    logger.setLevel("ERROR" if quiet else "INFO")

    registry = pooch.create(
        path=pooch.os_cache('dmsc_school'),
        retry_if_failed=3,
        base_url="https://public.esss.dk/groups/scipp/dmsc-summer-school/2025",
        registry={
            f"{name}.zip": None,
        },
    )
    file_path = registry.fetch(f"{name}.zip", processor=pooch.Unzip())

    # With the Unzip processor, `retrieve` returns a list of files that were in the zip
    # archive.
    # If len=1, then there was only a single file, and we return the path to that file.
    # If there were more than one file, we return the path to the parent folder.
    if len(file_path) > 1:
        path = Path(file_path[0])
        return str(path.parent.absolute())
    else:
        return file_path[0]


def show_as_static_plot(fig) -> VBar:
    """
    Render an interactive Plopp figure statically.

    This is useful for showing interactive figures in the book.
    Interactive figures require the ``widgets`` backend for matplotlib.
    But this breaks the figures in the built book.

    With this function, you can render, e.g., a slicer plot using this sequence of cells:

    .. code-block:: python

        # %%  (remove-cell)
        %matplotlib widget

        # %%  (remove-output)
        fig = pp.slicer(...)
        fig

        # %%  (remove-input, dmsc-school-remove)
        from utils import show_as_static_plot
        show_as_static_plot(fig)

        # %%  (remove-cell)
        %matplotlib inline

    Here, ``# %% (tags)`` indicates the start of a notebook cell and the tags
    used in that cell.
    """
    return VBar(
        [
            fig.top_bar,
            HBar([fig.left_bar, fig.view.canvas.to_image(), fig.right_bar]),
            fig.bottom_bar,
        ]
    )
