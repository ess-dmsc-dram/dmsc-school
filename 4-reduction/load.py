# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import pandas as pd
import scipp as sc
import scippnexus.v2 as sx
from typing import Tuple
import warnings


def load_nexus(path: str) -> sc.DataArray:
    """
    Load a SANS nexus file and return a scipp DataArray with the data.
    """
    fname = os.path.join(path, "mccode.h5")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with sx.File(fname) as f:
            dg = f[...]
    events = sc.collapse(
        dg["entry1"]["data"]["detector_signal_event_dat"].data, keep="dim_0"
    )
    meta = dg["entry1"]["simulation"]["Param"]
    columns = ["p", "x", "y", "n", "id", "t"]
    events = {c: v.rename_dims(dim_0="event") for c, v in zip(columns, events.values())}
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


def load_ascii(
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
    events = {key: c.data.rename_dims(row="event") for key, c in ds.items()}
    return events, meta
