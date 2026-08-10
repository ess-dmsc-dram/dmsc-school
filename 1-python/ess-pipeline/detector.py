import numpy as np
import matplotlib.pyplot as plt


def make_image(neutrons: dict, nx=100, ny=100) -> np.ndarray:
    """Turn neutron positions into detector pixels."""

    detector_width = 10.0  # cm
    detector_height = 10.0  # cm

    image = np.zeros((nx, ny))

    for x, y in zip(neutrons["x"], neutrons["y"]):
        # Convert x/y coordinates into pixel indices.
        x_pixel = int((x + detector_width / 2) / detector_width * nx)
        y_pixel = int((y + detector_height / 2) / detector_height * ny)

        # Keep only events that hit the detector.
        if 0 <= x_pixel < nx and 0 <= y_pixel < ny:
            image[x_pixel, y_pixel] += 1

    return image


def make_spectrum(neutrons: dict, bins=50) -> tuple[np.ndarray, np.ndarray]:
    """Make a spectrum (energy, wavelength, etc.)."""

    spectrum, bin_edges = np.histogram(neutrons["energy"], bins=bins)

    return spectrum, bin_edges


def plot(
    image: np.ndarray, spectrum: np.ndarray, energy_bins: np.ndarray
) -> plt.Figure:
    """Plot the detector image and energy spectrum."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot the detector image

    # Plot the energy spectrum

    return fig


def detector(neutrons: dict) -> dict:

    image = make_image(neutrons)
    spectrum, energy_bins = make_spectrum(neutrons)
    fig = plot(image, spectrum, energy_bins)

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
