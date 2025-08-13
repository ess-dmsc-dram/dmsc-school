# SPDX-License-Identifier: BSD-3-Clause

from typing import Tuple
import numpy as np


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

    return pooch.retrieve(
        url=f"https://public.esss.dk/groups/scipp/dmsc-summer-school/2025/{name}",
        known_hash=None,
    )
