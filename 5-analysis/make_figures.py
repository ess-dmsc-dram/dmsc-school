# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, norm, uniform

plt.ioff()

_x = np.linspace(-2, 12, 1000)
fig, ax = plt.subplots(figsize=(5, 3))
u = uniform(loc=0, scale=10)
ax.plot(_x, u.pdf(_x))
ax.set_ylim(0, None)
ax.set_xlim(_x.min(), _x.max())
ax.set_xlabel("$b$")
ax.set_ylabel("$p(b)$")
fig.savefig("uniform.png", dpi=300, bbox_inches="tight")

np.random.seed(1)
mu = 10.4
sigma = 1.6
n = norm(mu, sigma)
x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
fig0, ax0 = plt.subplots(figsize=(5, 3))
ax0.plot(x, n.pdf(x))
ax0.set_ylim(0, None)
ax0.set_xlim(x.min(), x.max())
ax0.set_xlabel("$x$")
ax0.set_ylabel("$p(x)$")
fig0.savefig("normal_fig.png", dpi=300, bbox_inches="tight")

x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
fig1, ax1 = plt.subplots(figsize=(5, 3))
ax1.plot(x, n.pdf(x))
ax1.plot(3.22490293**2, n.pdf(3.22490293**2), "ro")
ax1.set_ylim(0, None)
ax1.set_xlim(x.min(), x.max())
ax1.set_xlabel("$x$")
ax1.set_ylabel("$p(x)$")
fig1.savefig("normal_fit_fig.png", dpi=300, bbox_inches="tight")

x = np.linspace(1, 10, 5)
y = 4.1 * x + 2.3
y_noise = np.random.randn(x.size) * 2
y += y_noise
dy = np.abs(np.random.randn() * 2)

fig2, ax2 = plt.subplots(1, 2, figsize=(10, 3))
ax2[0].errorbar(x, y, dy, marker=".", ls="")
ax2[0].set_ylim(0, None)
ax2[0].set_xlabel("$x$")
ax2[0].set_ylabel("$y$")
y_range = np.arange(-5, 60, 0.1)
for i, yy in enumerate(y):
    ax2[1].fill_between(
        y_range, norm(yy, dy).pdf(y_range), color="b", alpha=0.08 * (i + 1), lw=0
    )
ax2[1].set_xlim(y_range.min(), y_range.max())
ax2[1].set_ylim(0, None)
ax2[1].set_xlabel("$y$")
ax2[1].set_ylabel("$p(y)$")
fig2.savefig("multid_fig.png", dpi=300, bbox_inches="tight")


result = linregress(x, y)

fig3, ax3 = plt.subplots(1, 2, figsize=(10, 3))
ax3[0].errorbar(x, y, dy, marker=".", ls="")
ax3[0].plot(x, x * result.slope + result.intercept, "g-")
ax3[0].set_ylim(0, None)
ax3[0].set_xlabel("$x$")
ax3[0].set_ylabel("$y$")

y_range = np.arange(-5, 60, 0.1)
for i, yy in enumerate(y):
    ax3[1].fill_between(
        y_range, norm(yy, dy).pdf(y_range), color="b", alpha=0.08 * (i + 1), lw=0
    )
    ax3[1].plot(
        x[i] * result.slope + result.intercept,
        norm(yy, dy).pdf(x[i] * result.slope + result.intercept),
        "go",
    )
ax3[1].set_xlim(y_range.min(), y_range.max())
ax3[1].set_ylim(0, None)
ax3[1].set_xlabel("$y$")
ax3[1].set_ylabel("$p(y)$")
fig3.savefig("multid_fit_fig.png", dpi=300, bbox_inches="tight")

plt.ion()
