import numpy as np


def interact_with_sample(neutrons: dict) -> dict:
    """Decide what happens to each neutron."""

    n = len(neutrons["x"])

    random_numbers = np.random.random(n)

    transmitted = random_numbers > 0.2

    out = {}
    for key in ("x", "y", "z", "vx", "vy", "vz", "energy", "time"):
        # Select only the neutrons that pass through by indexing with the boolean array `transmitted`
        out[key] = neutrons[key][transmitted]

    # TODO 1: add other interactions (e.g. scattering, inelastic process, etc.)
    # TODO 2: make the probabilities depend on neutron energy, angle, etc.
    # TODO 3: make the transmission/scattering pattern interesting to look at for the detector team

    return out


def sample(neutrons: dict) -> dict:

    after_sample = interact_with_sample(neutrons)

    after_sample["message"] = (
        f"Sample interaction: {len(after_sample['x'])} neutrons survived."
    )
    return after_sample
