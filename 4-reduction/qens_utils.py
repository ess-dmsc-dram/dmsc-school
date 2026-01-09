# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
from typing import NewType
import scipp as sc

from load import load_ascii, load_nexus
from utils import fetch_data  # noqa: F401


DETECTOR_OFFSET = 0.25 * sc.units.m


def analyzer_info(params: sc.DataGroup) -> sc.DataGroup:
    # This assumes that the analyzer is in the source-sample plane,
    # rotated by `angle` about the y-axis around the sample
    # and at `distance` from the sample.
    angle = sc.scalar(30.0, unit="deg")
    distance = sc.scalar(float(params["analyzer_distance"]), unit="m")
    analyzer_position = sc.spatial.as_vectors(
        sc.sin(angle) * distance,
        sc.scalar(0.0, unit="m"),
        sc.cos(angle) * distance,
    )

    # The analyzer is tilted by this angle such that neutron are
    # reflected by `2*analyzer_angle` to the detector.
    analyzer_angle = sc.atan2(y=DETECTOR_OFFSET, x=distance) / 2

    return sc.DataGroup(
        {
            # Si (111) as Miracles: Q = 2*pi/3.135
            "analyzer_dspacing": sc.scalar(3.135, unit="angstrom"),
            "analyzer_position": analyzer_position,
            "analyzer_angle": analyzer_angle,
        }
    )


def correct_tof(tof):
    # The instrument focuses on the center of the pulse at 2.86/2 ms.
    # Shift the time such that tof is the time since the neutron were emitted.
    return tof - sc.scalar(0.5 * 2.86, unit="ms")


def load_qens(path: str) -> sc.DataArray:
    """
    Load a QENS nexus file for the summer school QENS experiment.

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

    # Add variances
    # (See https://www.mcstas.org/documentation/manual/mcstas-3.5.27-manual.pdf,
    # section 2.2.1)
    da.variances = da.values**2

    da.coords["y"].unit = "m"
    # The event positions are in the detector coordinate system.
    # Translate by the detector offset to get the lab system.
    da.coords["y"] += DETECTOR_OFFSET
    da.coords["x"].unit = "m"
    z = sc.zeros_like(da.coords["y"])
    da.coords["position"] = sc.spatial.as_vectors(
        da.coords["x"].to(dtype=float), da.coords["y"], z
    )
    da.coords["tof"] = da.coords.pop("t")
    da.coords["tof"].unit = "s"
    da.coords["tof"] = correct_tof(da.coords["tof"].to(unit="ms"))

    da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
    da.coords["source_position"] = sc.vector(
        [0.0, 0.0, -float(meta["sample_distance"])], unit="m"
    )

    da.coords.update(analyzer_info(meta))

    return da


CoordTransformGraph = NewType("CoordTransformGraph", dict)
"""Graph describing coordinate transformations."""


Foldername = NewType("Foldername", str)
"""Folder name from which to load data."""


RawData = NewType("RawData", sc.DataArray)
"""Raw loaded data."""


MaskedRange = NewType("MaskedRange", tuple[float, float])
"""A range of values to mask, given as a (min, max) tuple."""


MaskedData = NewType("MaskedData", sc.DataArray)
"""Data with masked regions."""


EnergyTransferData = NewType("EnergyTransferData", sc.DataArray)
"""Data with energy transfer coordinate."""


BinWidth = NewType("BinWidth", sc.Variable)
"""Width of energy transfer bins."""


EnergyTransferHistogram = NewType("EnergyTransferHistogram", sc.DataArray)
"""Data histogrammed in energy transfer bins."""

__all__ = [
    "CoordTransformGraph",
    "Foldername",
    "RawData",
    "MaskedRange",
    "MaskedData",
    "EnergyTransferData",
    "BinWidth",
    "EnergyTransferHistogram",
]
