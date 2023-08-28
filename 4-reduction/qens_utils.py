# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import scipp as sc
import scippnexus.v2 as snx
import warnings


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

    return sc.DataGroup({
        # Si (111) as Miracles: Q = 2*pi/3.135
        "analyzer_dspacing": sc.scalar(3.135, unit="angstrom"),
        "analyzer_position": analyzer_position,
        "analyzer_angle": analyzer_angle,
    })


def load_qens(fname: str) -> sc.DataArray:
    """
    Load a QENS nexus file for the summer school QENS experiment.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with snx.File(fname) as f:
            dg = f[...]

    params = dg["entry1"]["simulation"]["Param"]
    events = sc.collapse(
        dg["entry1"]["data"]["detector_signal_event_dat"].data, keep="dim_0"
    )
    columns = ["p", "x", "y", "n", "id", "t"]
    events = {c: v.copy() for c, v in zip(columns, events.values())}
    weights = events.pop("p")
    weights.unit = "counts"
    da = sc.DataArray(data=weights, coords=events)

    # TODO
    da *= 100

    da = da.rename_dims(dim_0="event")

    da.coords["y"].unit = "m"
    # The event positions are in the detector coordiante system.
    # Translate by the detector offset to get the lab system.
    da.coords["y"] += DETECTOR_OFFSET
    da.coords["x"].unit = "m"
    z = sc.zeros_like(da.coords["y"])
    da.coords["position"] = sc.spatial.as_vectors(da.coords["x"], da.coords["y"], z)
    da.coords["tof"] = da.coords.pop("t")
    da.coords["tof"].unit = "s"
    da.coords["tof"] = da.coords["tof"].to(unit="ms")

    da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
    da.coords["source_position"] = sc.vector(
        [0.0, 0.0, -float(params["sample_distance"])], unit="m"
    )

    da.coords.update(analyzer_info(params))
    
    return da
