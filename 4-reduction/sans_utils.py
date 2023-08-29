# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pandas as pd
import scipp as sc
import os


# def load_sans(fname: str, factor=1.0) -> sc.DataArray:
#     """
#     Load a SANS nexus file and return a scipp DataArray with the data.
#     """
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#         f = sx.File(fname)
#         dg = f[...]
#         f.close()
#     events = sc.collapse(
#         dg["entry1"]["data"]["detector_signal_event_dat"].data, keep="dim_0"
#     )
#     params = dg["entry1"]["simulation"]["Param"]
#     columns = ["p", "x", "y", "n", "id", "t"]
#     events = {c: v.copy() for c, v in zip(columns, events.values())}
#     weights = events.pop("p")
#     weights.unit = "counts"
#     da = sc.DataArray(data=weights * factor, coords=events)

#     da.coords["y"].unit = "m"
#     da.coords["y"] += 0.25 * sc.units.m
#     da.coords["x"].unit = "m"
#     z = sc.full_like(da.coords["y"], float(params["detector_distance"]))
#     da.coords["position"] = sc.spatial.as_vectors(da.coords["x"], da.coords["y"], z)
#     da.coords["tof"] = da.coords.pop("t")
#     da.coords["tof"].unit = "s"
#     da.coords["tof"] = da.coords["tof"].to(unit="ms")

#     da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
#     da.coords["source_position"] = sc.vector(
#         [0.0, 0.0, -float(params["sample_distance"])], unit="m"
#     )
#     for c in ["n", "id"]:
#         del da.coords[c]
#     return da


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


def load_sans(
    path: str, events_file: str = "detector_signal_event.dat"
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
    fname = os.path.join(path, events_file)
    header = _load_header(fname=fname)
    ds = sc.compat.from_pandas(
        pd.read_csv(
            fname,
            delimiter=" ",
            comment="#",
            names=["p", "x", "y", "n", "id", "t"],
            index_col=False,
        )
    )
    coords = {key: c.data for key, c in ds.items()}
    weights = coords.pop("p") * float(header["integration_time"])
    weights.unit = "counts"
    da = sc.DataArray(data=weights, coords=coords)

    da.coords["y"].unit = "m"
    da.coords["y"] += 0.25 * sc.units.m
    da.coords["x"].unit = "m"
    z = sc.full_like(da.coords["y"], float(header["detector_distance"]))
    da.coords["position"] = sc.spatial.as_vectors(
        da.coords["x"].to(dtype=float), da.coords["y"], z
    )
    da.coords["tof"] = da.coords.pop("t")
    da.coords["tof"].unit = "s"
    da.coords["tof"] = da.coords["tof"].to(unit="ms")

    da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
    da.coords["source_position"] = sc.vector(
        [0.0, 0.0, -float(header["sample_distance"])], unit="m"
    )
    for c in ["n", "id"]:
        del da.coords[c]
    return da
