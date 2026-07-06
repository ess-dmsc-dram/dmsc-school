# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import os
from contextlib import contextmanager
import warnings
from collections.abc import Generator, Iterable
from typing import Any

import pandas as pd
import scipp as sc
import scippnexus as sx


def load_nexus(path: str) -> tuple[dict[str, sc.Variable], sc.DataGroup[Any]]:
    """
    Load a McStas NeXus file and return the event data and metadata.
    """
    [events], meta = load_nexus_many(path, ["detector_signal_event_dat"])
    return events, meta


def load_nexus_many(
    path: str, event_names: Iterable[str]
) -> tuple[list[dict[str, sc.Variable]], sc.DataGroup[Any]]:
    """
    Load multiple event data fields and metadata from a McStas NeXus file.
    """
    fname = os.path.join(path, "mccode.h5")
    with open_nexus_file(fname) as f:
        dg = f[...]

    events = []
    for name in event_names:
        ev = sc.collapse(dg["entry1"]["data"][name].data, keep="dim_0")
        columns = ["p", "x", "y", "n", "id", "t"]
        events.append(
            {
                c: v.rename_dims(dim_0="event").copy()
                for c, v in zip(columns, ev.values())
            }
        )

    meta = dg["entry1"]["simulation"]["Param"]
    return events, meta


@contextmanager
def open_nexus_file(path: str) -> Generator[sx.Group, None, None]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with sx.File(path) as f:
            yield f


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
) -> tuple[sc.DataArray, dict]:
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
