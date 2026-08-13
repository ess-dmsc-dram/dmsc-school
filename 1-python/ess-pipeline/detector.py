import numpy as np
import matplotlib.pyplot as plt


def record_events(neutrons: dict, nx=100, ny=100, bins=50) -> np.ndarray:
    """Turn neutron positions into detector pixels.
    Also make a histogram of the neutron energies/wavelengths.
    """

    detector_width = 10.0  # what is the unit?
    detector_height = 10.0

    image = np.zeros((nx, ny))
    spectrum = np.zeros(bins)

    for x, y in zip(neutrons["x"], neutrons["y"]):
        # Convert x/y coordinates into pixel indices.
        x_pixel = int((x + detector_width / 2) / detector_width * nx)
        y_pixel = int((y + detector_height / 2) / detector_height * ny)

        # Keep only events that hit the detector.
        if 0 <= x_pixel < nx and 0 <= y_pixel < ny:
            image[x_pixel, y_pixel] += 1

    # TODO 1: Can the performance be improved by using numpy?
    # TODO 2: Implement the wavelength/energy spectrum calculation.
    # TODO 3: Can we think about resolution effects?

    return image, spectrum


def plot(image: np.ndarray, spectrum: np.ndarray) -> plt.Figure:
    """Plot the detector image and energy spectrum."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # TODO: Plot the detector image

    # TODO: Plot the energy spectrum

    return fig


def detector(neutrons: dict) -> dict:

    image, spectrum = record_events(neutrons)
    fig = plot(image, spectrum)

    results = {
        "image": image,
        "spectrum": spectrum,
        "plot": fig,
    }

    results["message"] = (
        f"Detector: {len(neutrons['x'])} neutrons detected. "
        f"Image shape: {image.shape}. "
        f"Spectrum bins: {len(spectrum)}."
    )

    return results
