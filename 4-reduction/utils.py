# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import scipp as sc
import scippnexus as sx
import warnings

from powder_utils import load_powder
from qens_utils import load_qens
from sans_utils import load_sans


def add_variances(*inputs: sc.DataArray):
    """
    Add variances to the data, using the data counts (the standard deviation is the
    square root of the variance).
    """
    for da in inputs:
        da.variances = da.values


def fold_pulses(data, tof_edges, offsets):
    """
    Fold the data into a single pulse.

    Parameters
    ----------
    data
        Data to fold.
    tof_edges
        Edges of the time-of-flight bins.
    offsets
        Time offset to apply to each of the time-of-flight bins.
    """
    binned = data.bin(tof=tof_edges)
    binned.bins.coords["tof"] -= offsets
    out = binned.bins.constituents["data"]
    for name, coord in data.coords.items():
        if name not in out.coords:
            out.coords[name] = coord
    return out
