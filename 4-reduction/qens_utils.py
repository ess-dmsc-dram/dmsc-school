# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)
import os
import re
from collections.abc import Generator

import scipp as sc
import scippnexus as sx
from load import load_nexus_many, open_nexus_file
from utils import fetch_data  # noqa: F401

DETECTOR_OFFSET = 0.25 * sc.units.m


def _analyzer_info(folder: str, sample_position: sc.Variable) -> dict[str, sc.Variable]:
    analyzer_position = _load_analyzer_positions(folder, sample_position)

    # The analyzer is tilted by this angle such that neutron are
    # reflected by `2*analyzer_angle` to the detector.
    analyzer_distance = sc.norm(analyzer_position)
    analyzer_angle = sc.atan2(y=DETECTOR_OFFSET, x=analyzer_distance) / 2

    # Si (111) as Miracles: Q = 2*pi/3.135
    analyzer_dspacing = sc.array(
        dims=["detector_number"],
        values=[3.135] * len(analyzer_position),
        unit="angstrom",
    )

    return {
        "analyzer_dspacing": analyzer_dspacing,
        "analyzer_position": analyzer_position,
        "analyzer_angle": analyzer_angle,
    }


ANALYZER_POSITION_PATTERN = re.compile(r"\d+_analyzer_(\d)_pos")


def _load_analyzer_positions(folder: str, sample_position: sc.Variable) -> sc.Variable:
    fname = os.path.join(folder, "mccode.h5")
    with open_nexus_file(fname) as f:
        components = f["entry1"]["instrument"]["components"]
        mcstas_positions = sorted(
            (
                (int(i), sc.vector(pos_group["Position"][()].values, unit="m"))
                for i, pos_group in _analyzer_pos_components(components)
            ),
            key=lambda t: t[0],
        )
        positions = [pos - sample_position for _, pos in mcstas_positions]

    return sc.concat(positions, dim="detector_number")


def _analyzer_pos_components(
    group: sx.Group,
) -> Generator[tuple[int, sx.Group], None, None]:
    for name in group.keys():
        if (match := ANALYZER_POSITION_PATTERN.match(name)) is not None:
            yield int(match[1]), group[name]


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
    all_events, meta = load_nexus_many(
        path, [f"detector_signal_event_{i}_dat" for i in range(5)]
    )
    mcstas_sample_position = sc.vector([0, 0, float(meta["sample_distance"])], unit="m")

    data = []

    for num, events in enumerate(all_events):
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
        da.coords["source_position"] = -mcstas_sample_position

        da.coords["detector_number"] = sc.index(num).broadcast(
            dims=["event"], shape=[len(da)]
        )

        data.append(da)

    return (
        sc.concat(data, dim="event")
        .group("detector_number")
        .assign_coords(_analyzer_info(path, mcstas_sample_position))
    )
