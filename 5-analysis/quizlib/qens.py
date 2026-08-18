# Quiz questions for the QENS analysis notebook (6b-analysis-qens.ipynb).
# Questions are numbered in the order they appear in the notebook.

q1 = [
    {
        "question": "Looking at the elastic data: why is the elastic peak not exactly at zero energy transfer?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "The instrument calibration is not perfect, giving a small systematic energy offset.",
                "correct": True,
                "feedback": "Correct. Small misalignments of the instrument and imperfections in the reduction "
                "(e.g. the conversion from time-of-flight to energy) shift the whole spectrum slightly. "
                "This is why the InstrumentModel contains a fittable energy offset.",
            },
            {
                "answer": "The elastic sample changes the energy of the neutrons slightly.",
                "correct": False,
                "feedback": "By definition, elastic scattering does not change the neutron energy — that is exactly "
                "why we use this sample to measure the resolution.",
            },
            {
                "answer": "It is a random statistical fluctuation.",
                "correct": False,
                "feedback": "Statistical noise would scatter the peak position randomly from Q to Q. Here the offset "
                "is systematic: it is the same for all Q values.",
            },
            {
                "answer": "The resolution function is asymmetric, which pulls the peak to one side.",
                "correct": False,
                "feedback": "An asymmetric resolution can shift the apparent peak position in general, but here the "
                "resolution is symmetric to a good approximation. The offset comes from the calibration.",
            },
        ],
    }
]

q2 = [
    {
        "question": "Which function should we use to model the measured resolution peak?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "A Gaussian.",
                "correct": True,
                "feedback": "Correct. The measured elastic line is well described by a Gaussian, so we use one (or, "
                "for a real instrument, possibly a sum of several Gaussians or other shapes) as an "
                "empirical model of the resolution.",
            },
            {
                "answer": "A delta function.",
                "correct": False,
                "feedback": "The *true* scattering function of the elastic sample is a delta function, but the "
                "*measured* peak has a finite width — that width IS the instrument resolution. A delta "
                "function has zero width and therefore cannot describe the measured peak.",
            },
            {
                "answer": "A Lorentzian.",
                "correct": False,
                "feedback": "A Lorentzian has much heavier tails than the measured elastic line. Some resolution functions have Lorentzian tails, but not this one.",
            },
            {
                "answer": "A polynomial.",
                "correct": False,
                "feedback": "A polynomial is useful for describing a slowly varying background, not a peak.",
            },
        ],
    }
]

q3 = [
    {
        "question": "Looking at the data far away from the elastic peak: how should we model the background?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "It is essentially zero and should be left out.",
                "correct": True,
                "feedback": "Correct. The absence of background is an artefact of the McStas simulation, but can also occur in real data, e.g. if a background measurement has been subtracted",
            },
            {
                "answer": "A flat, non-zero level from sample-environment scattering and detector noise.",
                "correct": False,
                "feedback": "That is what you would expect in a real experiment — there is always some background "
                "from the sample environment, electronic noise, and stray neutrons. But our data are "
                "simulated, and the simulation includes none of these sources.",
            },
            {
                "answer": "A background that grows with energy transfer, due to phonon scattering.",
                "correct": False,
                "feedback": "Inelastic (e.g. phonon) scattering can contribute a slowly varying background in real "
                "measurements, but no such processes are included in this simulation.",
            },
            {
                "answer": "It is impossible to say without fitting the data.",
                "correct": False,
                "feedback": "You can estimate the background level directly by looking at the data far from the "
                "elastic peak, where the peaks contribute essentially nothing.",
            },
        ],
    }
]

q4 = [
    {
        "question": "The area of the fitted resolution Gaussian varies with Q. "
        "How can we deal with this? (select all that apply)",
        "type": "many_choice",
        "answers": [
            {
                "answer": "Normalise the quasi-elastic data by the fitted resolution area at each Q, "
                "as one would normalise to a vanadium measurement.",
                "correct": True,
                "feedback": "Correct. The variation reflects properties of the instrument — detector size and "
                "efficiency, analyzer reflectivity and solid-angle coverage — not the sample, and the "
                "same variation is present in the quasi-elastic data. Dividing it out makes the "
                "intensities at different Q comparable. This is what we will do below.",
            },
            {
                "answer": "Skip the normalisation of the resolution function to unit area, so that its "
                "fitted area at each Q scales the model instead.",
                "correct": True,
                "feedback": "Correct. By default the resolution is normalised to area 1 when it is used in the "
                "InstrumentModel. If it kept its fitted area instead, the model would be multiplied by "
                "the same per-Q efficiency factor — equivalent to normalising the data. In this "
                "notebook we normalise the data instead.",
            },
            {
                "answer": "Improve the statistics of the elastic measurement — the variation is just noise.",
                "correct": False,
                "feedback": "The uncertainties on the fitted areas are much smaller than the variation from Q to "
                "Q, and the trend is smooth, so the variation is systematic, not statistical. More "
                "counting time would not remove it.",
            },
            {
                "answer": "Constrain the fit so that the resolution Gaussian has the same area at all Q.",
                "correct": False,
                "feedback": "That would force the resolution model to disagree with the measured elastic data. "
                "The area variation is real — it comes from the instrument — so the resolution model "
                "should describe it, and we correct for it in the data or in the model scaling instead.",
            },
        ],
    }
]

q5 = [
    {
        "question": "Looking at the quasi-elastic data: how does the width of the sharp peak compare "
        "to the width of the resolution?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "It has essentially the same width as the resolution.",
                "correct": True,
                "feedback": "Correct. The sharp peak comes from immobile (elastic) scatterers, i.e. a delta function "
                "in energy. Convolved with the resolution, a delta function reproduces the resolution "
                "shape exactly — the peak is resolution-limited.",
            },
            {
                "answer": "It is much narrower than the resolution.",
                "correct": False,
                "feedback": "No measured feature can be narrower than the instrument resolution: everything we "
                "measure is convolved with it.",
            },
            {
                "answer": "It is much broader than the resolution.",
                "correct": False,
                "feedback": "The clearly broader component is the second, wider peak. The sharp peak matches the "
                "resolution width.",
            },
            {
                "answer": "They cannot be compared, since they come from different samples.",
                "correct": False,
                "feedback": "They can! Both are measured on the same instrument with the same settings, so the "
                "resolution measured with the elastic sample applies to the quasi-elastic sample too.",
            },
        ],
    }
]

q6 = [
    {
        "question": "And how does the width of the wider peak compare to the resolution?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "It is clearly broader than the resolution.",
                "correct": True,
                "feedback": "Correct. This extra broadening cannot come from the instrument — it is genuine "
                "quasi-elastic broadening caused by the motion of the scatterers, and it is what "
                "we want to quantify.",
            },
            {
                "answer": "It has the same width as the resolution.",
                "correct": False,
                "feedback": "If it had the same width as the resolution it would just be elastic scattering. The "
                "wider peak is significantly broader, which is the signature of dynamics in the sample.",
            },
            {
                "answer": "It is narrower than the resolution.",
                "correct": False,
                "feedback": "No measured feature can be narrower than the resolution.",
            },
            {
                "answer": "It only looks broader because of poor statistics.",
                "correct": False,
                "feedback": "The broadening is far larger than the statistical uncertainty, and it is systematic "
                "across all Q values. It is a real physical effect.",
            },
        ],
    }
]

q7 = [
    {
        "question": "How does the fitted width of the Lorentzian depend on Q?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "It grows roughly like Q² at low Q, then levels off towards a plateau at high Q.",
                "correct": True,
                "feedback": "Correct. The initial Q² rise looks like ordinary diffusion, but the width saturates "
                "at high Q instead of growing indefinitely.",
            },
            {
                "answer": "It is constant, independent of Q.",
                "correct": False,
                "feedback": "Look at the low-Q part of the plot: the width clearly increases with Q before "
                "flattening out.",
            },
            {
                "answer": "It grows like Q² over the whole measured range.",
                "correct": False,
                "feedback": "A pure Q² law would keep growing steeply. Instead, the width bends over and "
                "approaches a plateau at high Q.",
            },
            {
                "answer": "It decreases with increasing Q.",
                "correct": False,
                "feedback": "The width increases with Q — motion appears faster when probed on shorter "
                "length scales (larger Q).",
            },
        ],
    }
]

q8 = [
    {
        "question": "Which diffusion model should we use to describe this Q dependence of the width?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "Jump diffusion: Γ(Q) = ħDQ² / (1 + DτQ²).",
                "correct": True,
                "feedback": "Correct. Jump diffusion gives the observed behaviour: an ordinary-diffusion Q² rise at "
                "low Q, saturating at a plateau ħ/τ at high Q, where τ is the residence time between jumps.",
            },
            {
                "answer": "Brownian (continuous) diffusion: Γ(Q) = ħDQ².",
                "correct": False,
                "feedback": "Brownian diffusion predicts a width that grows like Q² without limit. Our width "
                "saturates at high Q, so simple Brownian diffusion cannot describe it.",
            },
            {
                "answer": "Isotropic rotational diffusion: Γ = 2ħD_r, independent of Q.",
                "correct": False,
                "feedback": "For rotational diffusion the quasi-elastic signal is a sum of Lorentzians with widths "
                "Γ_l = l(l+1)ħD_r, dominated by the l=1 term Γ = 2ħD_r. These widths are set by the "
                "rotational diffusion constant D_r and are independent of Q — only the relative "
                "intensities of the elastic and quasi-elastic parts change with Q. Our width clearly "
                "grows with Q at low Q.",
            },
            {
                "answer": "Diffusion in confinement (e.g. the Volino–Dianoux model): "
                "Γ(Q) ≈ 4.33 ħD/R² at low Q, approaching ħDQ² at high Q.",
                "correct": False,
                "feedback": "Confined diffusion produces the opposite low-Q behaviour: below Q ≈ π/R (with R the "
                "radius of the confining sphere) the width flattens to the constant 4.33 ħD/R² instead "
                "of going to zero like Q². Our data show a clean Q² rise at low Q and a plateau at "
                "high Q.",
            },
        ],
    }
]

q9 = [
    {
        "question": "Why does fitting all Q values simultaneously give smaller uncertainties than the "
        "two-step approach?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "The few global parameters (D, τ, scale) are constrained directly by every data point "
                "at every Q.",
                "correct": True,
                "feedback": "Correct. In the two-step approach, information is compressed into one width and one "
                "area per Q (with their uncertainties) before the diffusion model ever sees it. The "
                "simultaneous fit lets all the raw data points constrain the small number of physical "
                "parameters directly.",
            },
            {
                "answer": "The simultaneous fit has more free parameters, so it fits the data better.",
                "correct": False,
                "feedback": "It is the other way around: the simultaneous fit has *fewer* free parameters than the "
                "per-Q fits, because one global D and τ replace an independent width at every Q.",
            },
            {
                "answer": "The two-step approach is statistically invalid.",
                "correct": False,
                "feedback": "The two-step approach is perfectly valid and is a good way to discover which model to "
                "use. It just loses some information by summarising each Q as a width and an area "
                "before fitting the model.",
            },
            {
                "answer": "A simultaneous fit always gives smaller uncertainties, whatever the model.",
                "correct": False,
                "feedback": "Only if the global model actually describes the data well. If the model were wrong, "
                "forcing it on all Q values simultaneously would give biased parameters with "
                "misleadingly small uncertainties.",
            },
        ],
    }
]

q10 = [
    {
        "question": "The fitted values deviate somewhat from the true ones. What is the most promising "
        "way to improve the result?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "Better counting statistics: measure for longer (or simulate more neutrons).",
                "correct": True,
                "feedback": "Correct. The remaining deviation is consistent with the noise level in the data. "
                "More counts shrink the uncertainty of every data point, and with it the scatter of "
                "the fitted parameters. In a real experiment this means counting for longer; in our "
                "virtual experiment it means a larger ncount in the McStas simulation.",
            },
            {
                "answer": "Add more free parameters to the model.",
                "correct": False,
                "feedback": "The model already describes the physics that is in the data (a delta function plus "
                "jump diffusion, convolved with the resolution). Extra parameters would mostly fit "
                "noise and would increase the uncertainties on the physical parameters.",
            },
            {
                "answer": "Use finer energy bins in the reduction.",
                "correct": False,
                "feedback": "Rebinning the same events does not add information — the total number of counts is "
                "unchanged. Much finer bins would just leave many nearly-empty bins.",
            },
            {
                "answer": "Discard the Q values where the fit looks worst.",
                "correct": False,
                "feedback": "Throwing away data reduces the information in the fit and risks biasing the result. "
                "It is better to understand why those points deviate — and to collect more statistics.",
            },
        ],
    }
]
