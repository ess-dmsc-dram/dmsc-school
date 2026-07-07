# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)
from collections.abc import Generator

import mcstastox
import scipp as sc
from load import load_nexus_many
from utils import fetch_data  # noqa: F401


def _load_analyzer_info(
    folder: str,
    analyzer_number: int,
    detector_position: sc.Variable,
    mcstas_sample_position: sc.Variable,
) -> dict[str, sc.Variable]:
    from scippneutron.conversion.beamline import two_theta

    analyzer_position = _load_position(
        folder, f"analyzer_{analyzer_number}", mcstas_sample_position
    )

    # Because the position is relative to the sample:
    sample_analyzer_vec = analyzer_position
    analyzer_detector_vec = detector_position - analyzer_position
    # The analyzer is tilted by this angle such that neutron are
    # reflected by `2*analyzer_angle` to the detector.
    # The minus is needed to get the smaller angle between the vectors.
    analyzer_angle = (
        two_theta(
            incident_beam=-sample_analyzer_vec,
            scattered_beam=analyzer_detector_vec,
        )
        / 2
    )

    # Si (111) as Miracles: Q = 2*pi/3.135
    analyzer_dspacing = sc.scalar(3.135, unit="angstrom")

    return {
        "analyzer_dspacing": analyzer_dspacing,
        "analyzer_position": analyzer_position,
        "analyzer_angle": analyzer_angle,
    }


def _load_position(
    folder: str, component_name: str, sample_position: sc.Variable
) -> sc.Variable:
    with mcstastox.Read(folder) as file:
        mcstas_positions = file.get_component_placement(component_name)[0]
    return sc.vector(mcstas_positions, unit="m") - sample_position


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
        detector_position = _load_position(
            path, f"signal_tof_event_{num}", mcstas_sample_position
        )

        del events['id']
        del events['n']

        weights = events.pop("p")
        weights.unit = "counts"
        weights *= float(meta["integration_time"])
        da = sc.DataArray(data=weights, coords=events)

        # Add variances
        # (See https://www.mcstas.org/documentation/manual/mcstas-3.5.27-manual.pdf,
        # section 2.2.1)
        da.variances = da.values**2

        # The event positions are in the detector coordinate system.
        # Translate by the detector offset to get the lab system.
        event_x = da.coords.pop("x").to(dtype=float)
        event_x.unit = "m"
        event_y = da.coords["y"].to(dtype=float)
        event_y.unit = "m"
        event_z = sc.zeros_like(event_y)
        event_pos = sc.spatial.as_vectors(event_x, event_y, event_z)
        pos = event_pos + detector_position
        da.coords["position"] = pos
        da.coords["y"] = pos.fields.y.copy()

        da.coords["tof"] = da.coords.pop("t")
        da.coords["tof"].unit = "s"
        da.coords["tof"] = correct_tof(da.coords["tof"].to(unit="ms"))

        da.coords["sample_position"] = sc.vector([0.0, 0.0, 0.0], unit="m")
        da.coords["source_position"] = -mcstas_sample_position

        da.coords["detector_number"] = sc.scalar(num).broadcast(
            dims=["event"], shape=[len(da)]
        )

        da.coords.update(
            {
                name: var.broadcast(dims=["event"], shape=[len(da)])
                for name, var in
                _load_analyzer_info(path, num, detector_position, mcstas_sample_position).items()
            }
        )

        data.append(da)

    return sc.concat(data, dim="event")
