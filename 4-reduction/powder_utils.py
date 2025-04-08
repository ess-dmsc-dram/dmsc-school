# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import os
import scipp as sc

from load import load_ascii, load_nexus


def load_powder(
    path: str,
) -> sc.DataArray:
    """
    Load powder simulation results and return a scipp DataArray with the data.

    Parameters
    ----------
    path:
        Path to the directory containing the simulation results.
    """
    raise NotImplementedError()
