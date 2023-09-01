# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import scipp as sc

from load import load_ascii, load_nexus


def load_sans(
    path: str,
) -> sc.DataArray:
    """
    Load SANS simulation results and return a scipp DataArray with the data.

    Parameters
    ----------
    path
        Path to the directory containing the simulation results.
    """
    ascii_file = os.path.join(path, "detector_signal_event.dat")
    if os.path.exists(ascii_file):
        events, meta = load_ascii(filename=ascii_file)
    else:
        events, meta = load_nexus(path=path)

    weights = events.pop("p")
    weights.unit = "counts"
    weights *= float(meta["integration_time"])
    da = sc.DataArray(data=weights, coords=events)

    da.coords["y"].unit = "m"
    da.coords["y"] += 0.25 * sc.units.m
    da.coords["x"].unit = "m"
    z = sc.full_like(da.coords["y"], float(meta["detector_distance"]))
    da.coords["position"] = sc.spatial.as_vectors(
        da.coords["x"].to(dtype=float), da.coords["y"], z
    )
    da.coords["tof"] = da.coords.pop("t")
    da.coords["tof"].unit = "s"
    da.coords["tof"] = da.coords["tof"].to(unit="ms")

    da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
    da.coords["source_position"] = sc.vector(
        [0.0, 0.0, -float(meta["sample_distance"])], unit="m"
    )
    for c in ["n", "id"]:
        del da.coords[c]
    return da
