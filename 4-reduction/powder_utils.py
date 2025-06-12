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

        detector_name_1 = "Banana_large"
        detector_name_2 = "Banana_small"
        variables_1 = file.get_component_variables(detector_name_1)
        variables_2 = file.get_component_variables(detector_name_2)

        var_names = ["L", "v", "U1"]

        all_metadata_1 = all(item in variables_1 for item in var_names)
        all_metadata_2 = all(item in variables_2 for item in var_names)
        all_metadata = all_metadata_1 and all_metadata_2

        if all_metadata:
            raw_event_data_1 = file.get_event_data(
                variables=var_names, component_name=detector_name_1
            )
            raw_event_data_2 = file.get_event_data(
                variables=var_names, component_name=detector_name_2
            )

            full_L = np.concatenate((raw_event_data_1["L"], raw_event_data_2["L"]))
            events.coords["sim_wavelength"] = sc.array(
                dims=["events"], values=full_L, unit="Å"
            )

            full_source_time = np.concatenate(
                (raw_event_data_1["U1"], raw_event_data_2["U1"])
            )
            events.coords["sim_source_time"] = sc.array(
                dims=["events"], values=full_source_time, unit="s"
            )

            full_speed = np.concatenate((raw_event_data_1["v"], raw_event_data_2["v"]))
            events.coords["sim_speed"] = sc.array(
                dims=["events"], values=full_speed, unit="m/s"
            )

    events.coords["x"] = sc.array(
        dims=["events"], values=events.coords["position"].fields.x.values, unit="m"
    )
    events.coords["y"] = sc.array(
        dims=["events"], values=events.coords["position"].fields.y.values, unit="m"
    )
    events.coords["z"] = sc.array(
        dims=["events"], values=events.coords["position"].fields.z.values, unit="m"
    )
    # Rename 't' to 'toa'
    events.coords["toa"] = events.coords.pop("t")
    events.coords["time_origin"] = sc.scalar(0.0, unit=events.coords["toa"].unit)

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
