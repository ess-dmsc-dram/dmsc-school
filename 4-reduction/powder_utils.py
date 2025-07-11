# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

import numpy as np
import mcstastox
import scipp as sc

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


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
