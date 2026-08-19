# SPDX-License-Identifier: BSD-3-Clause

from typing import Tuple

import numpy as np
from plopp.widgets import HBar, VBar


def load(filename: str) -> Tuple[np.ndarray, ...]:
    """
    Load data from a file. Filter out any NaN values.
    """
    x, y, e = np.loadtxt(filename, unpack=True)
    sel = np.isfinite(y)
    return x[sel], y[sel], e[sel]


def fetch_data(name: str) -> str:
    """
    Fetch pre-prepared data from a remote source and return the path to the file.
    """
    import pooch

    registry = pooch.create(
        path=pooch.os_cache("dmsc_school"),
        retry_if_failed=3,
        base_url="https://public.esss.dk/groups/scipp/dmsc-summer-school/2026",
        registry={
            name: None,
        },
    )
    return registry.fetch(name)


def show_as_static_plot(fig, residuals=False) -> VBar:
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
    if residuals:
        res = fig.bottom_bar[0][0]

        bottom = VBar(
            [
                HBar([res.left_bar, res.view.canvas.to_image(), res.right_bar]),
                fig.bottom_bar[0][1],
            ]
        )
    else:
        bottom = fig.bottom_bar

    return VBar(
        [
            fig.top_bar,
            HBar([fig.left_bar, fig.view.canvas.to_image(), fig.right_bar]),
            bottom,
        ]
    )
