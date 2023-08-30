# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import pandas as pd
import scipp as sc
import scippnexus.v2 as sx
from typing import Tuple
import warnings


def _load_nexus(fname: str) -> sc.DataArray:
    """
    Load a SANS nexus file and return a scipp DataArray with the data.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = sx.File(fname)
        dg = f[...]
        f.close()
    events = sc.collapse(
        dg["entry1"]["data"]["detector_signal_event_dat"].data, keep="dim_0"
    )
    meta = dg["entry1"]["simulation"]["Param"]
    columns = ["p", "x", "y", "n", "id", "t"]
    events = {c: v.rename_dims(dim_0="row") for c, v in zip(columns, events.values())}
    return events, meta


def _load_header(fname: str, comment: str = "#") -> dict:
    lines = []
    maxlines = 100
    with open(fname, "r") as f:
        for _ in range(maxlines):
            line = f.readline()
            if line.startswith(comment):
                lines.append(line.lstrip(f" {comment}").strip())
            else:
                break
    header = {}
    for l in lines:
        if l.startswith("Param"):
            key, value = l.split(":")[1].split("=")
            header[key.strip()] = value.strip()
        else:
            pieces = l.split(":")
            if len(pieces) == 2:
                value = pieces[1].strip()
            else:
                value = pieces[1:]
            header[pieces[0].strip()] = value
    return header


def _load_ascii(
    filename: str,
) -> Tuple[sc.DataArray, dict]:
    meta = _load_header(fname=filename)

    ds = sc.compat.from_pandas(
        pd.read_csv(
            filename,
            delimiter=" ",
            comment="#",
            names=["p", "x", "y", "n", "id", "t"],
            index_col=False,
        )
    )
    events = {key: c.data for key, c in ds.items()}
    return events, meta


def load_sans(
    path: str,
) -> sc.DataArray:
    """
    Load SANS simulation results and return a scipp DataArray with the data.

    Parameters
    ----------
    path
        Path to the directory containing the simulation results.
    events_file
        Name of the file containing the events.
    """
    ascii_file = os.path.join(path, "detector_signal_event.dat")
    if os.path.exists(ascii_file):
        events, meta = _load_ascii(filename=ascii_file)
    else:
        events, meta = _load_nexus(path=path)

    # coords = {key: c.data for key, c in ds.items()}
    weights = events.pop("p") * float(meta["integration_time"])
    weights.unit = "counts"
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
