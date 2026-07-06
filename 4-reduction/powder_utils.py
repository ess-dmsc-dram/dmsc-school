# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

from typing import NewType, TypeVar

import numpy as np
import sciline as sl
import scipp as sc

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from utils import fetch_data  # noqa: F401


def load_powder(
    path: str, source_name="Source", sample_name="sample_position"
) -> sc.DataArray:
    """
    Load powder simulation results and return a scipp DataArray with the data.

    Parameters
    ----------
    path:
        Path to the directory containing the simulation results.
    """
    import mcstastox

    with mcstastox.Read(path) as file:
        events = file.export_scipp_simple(source_name, sample_name)

        detector_names = ["Banana_large_0", "Banana_large_1"]
        var_names = {
            "sim_wavelength": {"key": "L", "unit": "Å"},
            "sim_speed": {"key": "v", "unit": "m/s"},
            "sim_source_time": {"key": "U1", "unit": "s"},
        }

        raw_event_data = [
            file.get_event_data(
                variables=[v["key"] for v in var_names.values()], component_name=det
            )
            for det in detector_names
        ]

        for var_name, var_info in var_names.items():
            full_data = np.concatenate(
                [raw_event[var_info["key"]] for raw_event in raw_event_data]
            )
            events.coords[var_name] = sc.array(
                dims=["events"], values=full_data, unit=var_info["unit"]
            )

    # Add "xyz" coordinates from "position"
    for c in "xyz":
        events.coords[c] = getattr(events.coords["position"].fields, c).copy()

    # Rename 't' to 'toa'
    events.coords["toa"] = events.coords.pop("t")
    events.coords["time_origin"] = sc.scalar(0.0, unit=events.coords["toa"].unit)

    # Add variances
    # (See https://www.mcstas.org/documentation/manual/mcstas-3.5.27-manual.pdf,
    # section 2.2.1)
    events.variances = events.values**2

    return events


def time_distance_diagram(events: sc.DataArray):
    _, ax = plt.subplots()

    inds = np.random.choice(
        np.arange(events.sizes["events"]),
        size=min(5000, events.sizes["events"]),
        replace=False,
    )

    x = (
        np.stack(
            [
                events.coords["sim_source_time"].values[inds],
                events.coords["toa"].values[inds],
            ],
            axis=1,
        )
        * 1000.0
    )
    y = np.stack(
        [
            np.zeros_like(events.coords["sim_source_time"].values[inds]),
            events.coords["Ltotal"].values[inds],
        ],
        axis=1,
    )

    coll = LineCollection(np.stack((x, y), axis=2))
    coll.set_cmap("gist_rainbow")
    coll.set_array(events.coords["toa"].values[inds])
    coll.set_norm(plt.Normalize())
    ax.add_collection(coll)
    ax.plot(0, 0, "o", color="black")
    ax.text(0, 0, "current origin", ha="left", va="top")
    ax.set(xlabel="Time [ms]", ylabel="Distance [m]")
    ax.autoscale()
    ax.grid()


def save_xye(
    filename: str,
    *,
    event_data: sc.DataArray,
    normalized_histogram: sc.DataArray,
) -> None:
    """
    Save normalized histogram data to an XYE file.

    Parameters
    ----------
    filename:
        The name of the output file.
    event_data:
        The event data containing the coordinates for Ltotal and two_theta.
    normalized_histogram:
        The normalized histogram data to be saved.
    """
    average_l = event_data.coords["Ltotal"].mean()
    average_two_theta = event_data.coords["two_theta"].mean()
    difc = sc.to_unit(
        2
        * sc.constants.m_n
        / sc.constants.h
        * average_l
        * sc.sin(0.5 * average_two_theta),
        unit="us / angstrom",
    )

    from scippneutron.io import save_xye

    result = normalized_histogram.copy(deep=False)
    result.coords["tof"] = (sc.midpoints(result.coords["dspacing"]) * difc).to(
        unit="us"
    )

    save_xye(
        filename,
        result.rename_dims(dspacing="tof"),
        header=f"DIFC = {difc.to(unit='us/angstrom').value} [µ/Å] L = {average_l.value} [m] two_theta = {sc.to_unit(average_two_theta, 'deg').value} [deg]\ntof [µs]               Y [counts]               E [counts]",
    )


RunType = TypeVar("RunType")


SampleRun = NewType("SampleRun", int)
"""Sample run; a run with a sample in the beam."""

VanadiumRun = NewType("VanadiumRun", int)
"""Vanadium run; a run with a vanadium sample (almost perfect scatterer) in the beam."""

CoordTransformGraph = NewType("CoordTransformGraph", dict)
"""Graph describing coordinate transformations."""

SourcePosition = NewType("SourcePosition", sc.Variable)
"""Position of the source."""

TimeOrigin = NewType("TimeOrigin", sc.Variable)
"""Time origin of the source."""


class Foldername(sl.Scope[RunType, str], str):
    """Folder name for a specific run."""


class RawData(sl.Scope[RunType, sc.DataArray], sc.DataArray):
    """Raw loaded data."""


class CorrectedData(sl.Scope[RunType, sc.DataArray], sc.DataArray):
    """Data with corrected source position and time origin."""


class DspacingData(sl.Scope[RunType, sc.DataArray], sc.DataArray):
    """Data with d-spacing coordinate."""


TwoThetaBins = NewType("TwoThetaBins", sc.Variable)
"""Bins for two-theta coordinate."""

DspacingBins = NewType("DspacingBins", sc.Variable)
"""Bins for d-spacing coordinate."""


class HistogramTwothetaDspacing(sl.Scope[RunType, sc.DataArray], sc.DataArray):
    """Data histogrammed in two-theta and d-spacing bins."""


GaussianSmoothingSigma = NewType("GaussianSmoothingSigma", sc.Variable)
"""Sigma for Gaussian smoothing kernel."""


SmoothedVanadium = NewType("SmoothedVanadium", sc.DataArray)
"""Smoothed vanadium data."""


SampleDspacing = NewType("SampleDspacing", sc.DataArray)
"""Sample data summed over two-theta, leaving only d-spacing coordinate."""


NormalizedDspacing = NewType("NormalizedDspacing", sc.DataArray)
"""Normalized sample data in d-spacing."""


__all__ = [
    "RunType",
    "SampleRun",
    "VanadiumRun",
    "CoordTransformGraph",
    "Foldername",
    "RawData",
    "CorrectedData",
    "DspacingData",
    "TwoThetaBins",
    "DspacingBins",
    "HistogramTwothetaDspacing",
    "GaussianSmoothingSigma",
    "SmoothedVanadium",
    "SampleDspacing",
    "NormalizedDspacing",
    "SourcePosition",
    "TimeOrigin",
]
