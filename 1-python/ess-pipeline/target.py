import numpy as np


def make_neutrons(protons: dict, probability: float = 0.1) -> dict:
    """Convert some protons into neutrons."""

    n = len(protons["x"])

    x = []
    y = []
    z = []
    vx = []
    vy = []
    vz = []
    energy = []
    time = []

    for i in range(n):
        p = np.random.random() < probability
        if p:
            x.append(protons["x"][i])
            y.append(protons["y"][i])
            z.append(protons["z"][i])
            e = np.random.uniform(1, 100)  # what is the unit?
            energy.append(e)
            v_x = np.random.uniform(-1, 1)
            v_y = np.random.uniform(-1, 1)
            v_z = np.random.uniform(-1, 1)
            norm = np.sqrt(v_x**2 + v_y**2 + v_z**2)
            vx.append(v_x / norm)
            vy.append(v_y / norm)
            vz.append(v_z / norm)
            time.append(protons["time"][i])

    # TODO 1: make neutron energy depend on proton energy
    # TODO 2: is there room for optimization here? (e.g. using numpy arrays instead of lists)
    # TODO 3: is there a better way to sample the neutron velocity direction than uniform in a cube?

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


def target(protons: dict) -> dict:
    """Simulate neutron production in the target."""

    neutrons = make_neutrons(protons)
    neutrons["message"] = (
        f"Target: {len(neutrons['x'])} neutrons produced from {len(protons['x'])} protons."
    )

    return neutrons
