# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from dataclasses import dataclass
from jupyterquiz import display_quiz
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc


questions = {
    "zslice": {
        "question": "I want to get the first `z` slice... which one is it?",
        "type": "multiple_choice",
        "answers": [
            {"code": "a[:, :, :, 0]", "correct": False},
            {"code": "a[0, :, :, :]", "correct": False},
            {"code": "a[:, :, 0, :]", "correct": True},
        ],
    },
    "time_range": {
        "question": "I want to get the first `z` slice:",
        "type": "multiple_choice",
        "answers": [
            {"code": "var[:, :, 0, :]", "correct": False},
            {"code": "var['z', 0]", "correct": True},
            {"code": "var['x', 0]", "correct": False},
            {"code": "var['y', 0]", "correct": False},
        ],
    },
}


class QuizLib:
    def __init__(self, questions):
        self._questions = {}
        for i, question in enumerate(questions.values()):
            self._questions[i + 1] = [question]

    def __call__(self, ind):
        display_quiz(self._questions[ind])


quiz = QuizLib(questions)


def plot(*x):
    """
    Useful plot function for 1d and 2d data
    """
    fig, ax = plt.subplots()
    for a in x:
        if a.ndim == 1:
            ax.plot(np.arange(len(a)), a)
        elif a.ndim == 2:
            ax.imshow(a, origin="lower")


def scatter(x, y, get_ax=False):
    """
    Simple scatter plot
    """
    fig, ax = plt.subplots()
    ax.scatter(x, y, marker=".", s=1)
    ax.set_aspect("equal")
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    if get_ax:
        return ax


def _heart_y(param_t: np.ndarray) -> np.ndarray:
    """x = 16sin^3(t)"""
    return 16*np.sin(param_t)**3


def _heart_x(param_t: np.ndarray) -> np.ndarray:
    """y = 13cos(t) - 5cos(2t) - cos(4t)"""
    return 13*np.cos(param_t) - 5*np.cos(2*param_t) - np.cos(4*param_t)


def apply_random_noise(arr: np.ndarray,
                       noise_scale: float = 1.0, *,
                       rng: np.random.Generator) -> np.ndarray:
    return arr + (rng.random(size=arr.size)*noise_scale - noise_scale/2)


def _heart_signal(rng: np.random.Generator) -> sc.DataArray:
    size = 200_000
    param_t = rng.random(size=size)*2*np.pi - np.pi

    raw_x, raw_y = _heart_x(param_t), _heart_y(param_t)
    noise_x, noise_y = (apply_random_noise(coord, noise_scale=4, rng=rng) for coord in (raw_x, raw_y))
    scaled_x, scaled_y = (coord for coord in (noise_x, noise_y))

    x = sc.array(dims=['row'], values = scaled_x, unit='cm')
    y = sc.array(dims=['row'], values = scaled_y, unit='cm')

    return sc.DataArray(data=sc.ones(sizes=x.sizes, unit='counts'),
                        coords={'x': x, 'y': y})


@dataclass
class CircleSpec:
    r: float = 1
    cx: float = 0
    cy: float = 0
    start: float = 0
    stop: float = 2*np.pi


def circle(
        rng: np.random.Generator, size: int, c_spec: CircleSpec
    ) -> tuple[np.ndarray, np.ndarray]:
    width = c_spec.stop - c_spec.start
    param_t = c_spec.start + rng.random(size=size)*width - width/2
    return np.cos(param_t)*c_spec.r + c_spec.cx, np.sin(param_t)*c_spec.r + c_spec.cy


def tear_drop(rng: np.random.Generator, size: int, eye_spec: CircleSpec) -> tuple[np.ndarray, np.ndarray]:
    width = eye_spec.r/20
    height = width*2
    cx = eye_spec.cx
    cy = eye_spec.cy + eye_spec.r

    param_t = rng.random(size=size) * 2*np.pi - np.pi
    x = height*np.sin(param_t) + cx - height
    y = width*np.cos(param_t) - width*0.5*np.sin(2*param_t)  + cy
    return x, y


def test_plot_tear_drop(rng: np.random.Generator) -> None:
    eye_spec = CircleSpec(r=0.01)
    tear_x, tear_y = tear_drop(rng, size=300, eye_spec=eye_spec)

    x = sc.array(dims=['row'], values = tear_x, unit='cm')
    y = sc.array(dims=['row'], values = tear_y, unit='cm')

    sc.DataArray(data=sc.ones(sizes=x.sizes, unit='counts'),
                 coords={'x': x, 'y': y}).hist(x=50, y=50).plot()


def _smiley_signal(rng: np.random.Generator) -> sc.DataArray:
    face_spec = CircleSpec(r=0.1)
    leye_spec = CircleSpec(r=0.02, cx=0.02, cy=-0.04, stop=np.pi)
    reye_spec = CircleSpec(r=0.02, cx=0.02, cy=0.04, stop=np.pi)
    mouth_spec = CircleSpec(r=0.04, cx=-0.02, start=np.pi)

    part_spec_sizes = ((face_spec, 2000),
                       (leye_spec, 400),
                       (reye_spec, 400),
                       (mouth_spec, 800))
    parts = tuple(circle(rng, size=part_size, c_spec=part_spec)
             for part_spec, part_size in part_spec_sizes)
    part_x = tuple(part[0] for part in parts)
    part_y = tuple(part[1] for part in parts)
    tear_x, tear_y = tear_drop(rng, size=100, eye_spec=reye_spec)

    smiley_x = np.concatenate((*part_x, tear_x))
    smiley_y = np.concatenate((*part_y, tear_y))

    x = sc.array(dims=['row'], values = smiley_x, unit='cm')
    y = sc.array(dims=['row'], values = smiley_y, unit='cm')

    return sc.DataArray(data=sc.ones(sizes=x.sizes, unit='counts'),
                        coords={'x': x, 'y': y})


def load_signal_to_histogram(rng: np.random.Generator) -> sc.DataArray:
    heart = _heart_signal(rng)
    smiley = _smiley_signal(rng)
    return sc.concat((heart, smiley), dim='row')
