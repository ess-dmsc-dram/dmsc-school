import numpy as np


def make_protons(n_protons: int = 100) -> dict:
    """Create a bunch of protons at the source."""

    initial_energy = 1.0  # what is the unit?
    v = np.sqrt(2 * initial_energy)

    protons = {
        "x": np.random.normal(0, 1, n_protons),  # X is transverse to the beam direction
        "y": np.random.normal(0, 1, n_protons),  # Y is up, opposite to gravity
        "z": np.zeros(n_protons),  # Z is along the beam direction
        "vx": np.zeros(n_protons),  # Velocity in X direction
        "vy": np.zeros(n_protons),  # Velocity in Y direction
        "vz": np.full(n_protons, fill_value=v),  # Velocity in Z direction
        "energy": np.full(n_protons, fill_value=initial_energy),
        "time": np.zeros(n_protons),
    }

    return protons


def accelerate(protons: dict) -> dict:
    """Accelerate the proton beam."""

    # TODO:
    # Increase the proton energy.
    #
    # For the simple version, every proton can have
    # the same final energy.

    protons["energy"] = np.full_like(protons["energy"], fill_value=1000.0)

    return protons


def source_and_accelerator():
    protons = make_protons(n_protons=10_000)
    protons = accelerate(protons)
    protons["message"] = (
        f"Produced {len(protons['x'])} protons with energy {protons['energy'][0]}."
    )

    return protons
