# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from jupyterquiz import display_quiz

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
