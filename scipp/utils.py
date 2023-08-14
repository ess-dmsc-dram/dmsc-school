# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import scipp as sc
import scippnexus.v2 as sx
import warnings


def load_nexus(fname: str, factor=1.0) -> sc.DataArray:
    """
    Load a nexus file and return a scipp DataArray with the data.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = sx.File(fname)
        dg = f[...]
        f.close()
    events = sc.collapse(
        dg["entry1"]["data"]["detector_signal_event_dat"].data, keep="dim_0"
    )
    params = dg["entry1"]["simulation"]["Param"]
    columns = ["p", "x", "y", "n", "id", "t"]
    events = {c: v.copy() for c, v in zip(columns, events.values())}
    weights = events.pop("p")
    weights.unit = "counts"
    da = sc.DataArray(data=weights * factor, coords=events)

    da.coords["y"].unit = "m"
    da.coords["y"] += 0.25 * sc.units.m
    da.coords["x"].unit = "m"
    z = sc.full_like(da.coords["y"], float(params["detector_distance"]))
    da.coords["position"] = sc.spatial.as_vectors(da.coords["x"], da.coords["y"], z)
    da.coords["tof"] = da.coords.pop("t")
    da.coords["tof"].unit = "s"
    da.coords["tof"] = da.coords["tof"].to(unit="ms")

    da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
    da.coords["source_position"] = sc.vector(
        [0.0, 0.0, -float(params["sample_distance"])], unit="m"
    )
    for c in ["n", "id"]:
        del da.coords[c]
    return da


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
    binned.bins.coords['tof'] -= offsets
    out =  binned.bins.constituents['data']
    for c in ('sample_position', 'source_position'):
        out.coords[c] = data.coords[c]
    return out