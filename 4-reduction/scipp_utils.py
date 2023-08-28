# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from jupyterquiz import display_quiz
import matplotlib.pyplot as plt
import numpy as np


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
