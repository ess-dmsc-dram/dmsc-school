import numpy as np


def transport(neutrons: dict) -> dict:
    """Transport neutrons through the neutron guide."""

    n = len(neutrons["x"])

    transmission = 0.8  # Just a plain transmission fraction

    x = []
    y = []
    z = []
    vx = []
    vy = []
    vz = []
    energy = []
    time = []

    for i in range(n):
        survives = np.random.random() < transmission
        if survives:
            x.append(neutrons["x"][i])
            y.append(neutrons["y"][i])
            z.append(neutrons["z"][i])
            energy.append(neutrons["energy"][i])
            vx.append(neutrons["vx"][i])
            vy.append(neutrons["vy"][i])
            vz.append(neutrons["vz"][i])
            time.append(neutrons["time"][i])

    # TODO 1: some variables could be updated during transport (e.g. position, time, energy, etc.)
    # TODO 2: how could the transmission be made more realistic? (e.g. energy-dependent, angle-dependent, etc.)
    # TODO 3: is there room for optimization here? (e.g. using numpy arrays instead of lists)

    return {
        "x": np.array(x),
        "y": np.array(y),
        "z": np.array(z),
        "vx": np.array(vx),
        "vy": np.array(vy),
        "vz": np.array(vz),
        "energy": np.array(energy),
        "time": np.array(time),
    }


def neutron_guide(neutrons: dict) -> dict:
    """Simulate transport through a neutron guide."""

    to_sample = transport(neutrons)

    to_sample["message"] = (
        f"Neutron guide: {len(to_sample['x'])} neutrons survived transport."
    )

    return to_sample
