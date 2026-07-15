# SPDX-License-Identifier: BSD-3-Clause

from collections.abc import Iterable
from typing import Tuple

from easyscience import Parameter
import numpy as np
import pandas as pd

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
        path=pooch.os_cache('dmsc_school'),
        retry_if_failed=3,
        base_url=f"https://public.esss.dk/groups/scipp/dmsc-summer-school/2025",
        registry={
            name: None,
        },
    )
    return registry.fetch(name)
