# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)


from powder_utils import load_powder
from qens_utils import load_qens
from sans_utils import load_sans


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


__all__ = [
    "fold_pulses",
    "load_powder",
    "load_qens",
    "load_sans",
]
