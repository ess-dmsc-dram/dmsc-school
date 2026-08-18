# Quiz questions for the Bayesian QENS notebook (9b-bayesian-qens.ipynb).
# Questions are numbered in the order they appear in the notebook.

q1 = [
    {
        "question": "`suggest_bounds()` proposes a range many orders of magnitude wider than the fitted "
        "value of a parameter. What is the most likely explanation?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "The fit returned a huge uncertainty for that parameter, usually because it is "
                "degenerate with another one.",
                "correct": True,
                "feedback": "Correct. The suggestion is built from the fitted uncertainty, so an enormous range "
                "is a symptom, not the disease. If the data only constrain a combination of two "
                "parameters, each one individually can run away. Fix the model (fix or constrain a "
                "parameter) rather than sampling the degeneracy.",
            },
            {
                "answer": "The parameter is very well determined, so the sampler can afford a wide range.",
                "correct": False,
                "feedback": "It is the other way around: the range is derived from the uncertainty, so a wide "
                "suggestion means a poorly determined parameter.",
            },
            {
                "answer": "The units of the parameter are inconvenient.",
                "correct": False,
                "feedback": "The suggestion is relative to the parameter's own value and uncertainty, so it is "
                "unaffected by the choice of units.",
            },
            {
                "answer": "The data set is too small.",
                "correct": False,
                "feedback": "Poor statistics do widen uncertainties, but not usually by many orders of magnitude. "
                "That much is the signature of a parameter the data barely constrain at all.",
            },
        ],
    }
]

q2 = [
    {
        "question": "What are you looking for in the trace plot?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "A noisy but flat, stationary band — the same average and the same spread at the "
                "start of the trace as at the end.",
                "correct": True,
                "feedback": "Correct — the 'hairy caterpillar'. It means the chains have forgotten where they "
                "started and are now sampling the posterior itself.",
            },
            {
                "answer": "A curve that settles down and becomes smooth towards the end.",
                "correct": False,
                "feedback": "A trace that stops fluctuating is a bad sign: the chain has stopped exploring. The "
                "noise is the point — each step is meant to be a new draw from the posterior.",
            },
            {
                "answer": "A steady decrease, showing that the fit is still improving.",
                "correct": False,
                "feedback": "That would be the picture for an optimiser walking downhill. A sampler is not "
                "minimising anything; a systematic drift means the burn-in was too short and the "
                "chain has not yet reached the bulk of the posterior.",
            },
            {
                "answer": "All chains sitting on exactly the same value.",
                "correct": False,
                "feedback": "That would mean the chains are stuck, and the 'posterior' you get out would just be "
                "that one point.",
            },
        ],
    }
]

q3 = [
    {
        "question": "The summary reports a median and a 68% credible interval instead of a single "
        "symmetric error bar. What does that buy us?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "The interval can be asymmetric, which shows when a parameter is much better "
                "constrained on one side than on the other.",
                "correct": True,
                "feedback": "Correct. A least-squares fit approximates the posterior by a Gaussian around the "
                "minimum and reports a single number for its width, so any asymmetry is thrown "
                "away. For the well-determined parameters here the two sides come out almost "
                "equal, which is itself worth knowing: it tells you the Gaussian approximation is "
                "a fair one in this case. The asymmetry grows for parameters that are poorly "
                "constrained or pushed up against a physical limit such as zero.",
            },
            {
                "answer": "It is always narrower than the least-squares error bar, so the result is more "
                "precise.",
                "correct": False,
                "feedback": "It is not a precision trick. The credible interval is usually comparable to the "
                "least-squares error bar for a well-behaved parameter, and it can be considerably "
                "wider when the parameter is correlated with others.",
            },
            {
                "answer": "It does not depend on the model, only on the data.",
                "correct": False,
                "feedback": "The posterior depends on the model just as much as a fit does. Bayesian analysis "
                "characterises the uncertainty better; it does not remove the model dependence.",
            },
            {
                "answer": "It removes the need to check the fit quality.",
                "correct": False,
                "feedback": "The posterior tells you which parameters are consistent with the data *given the "
                "model*. If the model is wrong, the posterior is confidently wrong — so you still "
                "have to look at the data, the fit and the residuals.",
            },
        ],
    }
]

q4 = [
    {
        "question": "The resolution fit at this Q has three free parameters: the area and the width of "
        "the Gaussian, and the energy offset. Which pairs do you expect to be correlated?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "Essentially none of them: an isolated, well-measured peak determines its position, "
                "its width and its area more or less independently.",
                "correct": True,
                "feedback": "Correct — the corner plot shows round blobs. The offset only moves the peak "
                "sideways, which no change of area or width can imitate, so it decouples by "
                "symmetry. Area and width are also close to independent here: making the peak "
                "broader and more intense would fit the wings better but the top worse, and with "
                "counting statistics the data see the difference.",
            },
            {
                "answer": "Area and width strongly correlated, because both control the height of the peak.",
                "correct": False,
                "feedback": "A tempting argument, and it is what you would find if you only measured the peak "
                "height. But you measure the whole line shape: broadening the peak and adding area "
                "to keep the height fixed changes the wings, and the data are precise enough to "
                "notice. The blob is round.",
            },
            {
                "answer": "The offset correlated with the width, because a shifted peak looks broader.",
                "correct": False,
                "feedback": "That happens when you *average* several shifted spectra — but here we fit a single "
                "spectrum at a single Q, where a shift and a broadening look nothing alike.",
            },
            {
                "answer": "All three strongly correlated, since they all describe the same peak.",
                "correct": False,
                "feedback": "Describing the same feature does not make parameters correlated. What matters is "
                "whether a change in one can be compensated by a change in another while leaving "
                "the predicted curve the same — and here it cannot.",
            },
        ],
    }
]

q5 = [
    {
        "question": "The 68% credible band is so narrow that it is barely visible — much thinner than "
        "the error bars on the individual data points. Is something wrong?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "No — the band shows the uncertainty of the model curve, not the spread expected "
                "for individual measured points, which also contains the counting noise.",
                "correct": True,
                "feedback": "Correct. Every data point carries its own Poisson error, but the model is "
                "constrained by all of them at once, so the curve is pinned down far better than any "
                "single point. Roughly, with N points the curve is about √N times better determined.",
            },
            {
                "answer": "Yes — the band should contain about 68% of the data points, so the sampling has "
                "not converged.",
                "correct": False,
                "feedback": "That would be the criterion for a band that includes the measurement noise. This "
                "band is the credible interval of the model itself, and it is expected to be much "
                "narrower.",
            },
            {
                "answer": "Yes — the bounds were too narrow, so the posterior is truncated.",
                "correct": False,
                "feedback": "Truncated bounds do shrink the band, but that is not needed to explain what you see: "
                "a model band narrower than the data scatter is entirely normal. Check for truncation "
                "in the trace and corner plots instead.",
            },
            {
                "answer": "Yes — the number of drawn models (`n_draws`) is too small.",
                "correct": False,
                "feedback": "More draws make the band smoother, but not wider: they sample the same posterior "
                "more densely.",
            },
        ],
    }
]

q6 = [
    {
        "question": "The quasi-elastic model at each Q has a delta function area, a Lorentzian area, a "
        "Lorentzian width and an energy offset. Which correlations do you expect now?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "The two areas and the Lorentzian width are all correlated with one another, "
                "while the energy offset stays independent.",
                "correct": True,
                "feedback": "Correct: the corner plot shows clear tilted ridges between the three intensity "
                "and shape parameters. Both components put intensity near zero energy transfer, so "
                "the two areas trade against each other (raise one, lower the other, and the "
                "spectrum barely changes). The delta area is tied to the Lorentzian *width* the "
                "other way round: a broader Lorentzian spreads its intensity out and leaves a dip "
                "at the centre, which the delta function then has to fill. The offset only shifts "
                "the spectrum sideways, which nothing else can imitate, so it decouples.",
            },
            {
                "answer": "None: the delta function and the Lorentzian have very different widths, so they "
                "are independent.",
                "correct": False,
                "feedback": "They differ in the *wings*, which is what makes the fit possible at all. But near "
                "zero energy transfer they overlap heavily, and that overlap is exactly what "
                "correlates them.",
            },
            {
                "answer": "Only the energy offset is correlated with everything else, since it shifts the "
                "whole model.",
                "correct": False,
                "feedback": "The offset is the one parameter that stays fairly independent: shifting the "
                "spectrum sideways is something no combination of areas and widths can imitate.",
            },
            {
                "answer": "The same as for the resolution fit: round blobs everywhere.",
                "correct": False,
                "feedback": "The resolution fit had a single peak, so nothing could trade against anything. Here "
                "two components describe overlapping intensity in the same energy range, which is "
                "precisely the situation that produces correlations.",
            },
        ],
    }
]

q7 = [
    {
        "question": "In the exercise above we freed the background coefficient, which we had kept fixed "
        "at zero. What happens to the posterior?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "A new correlation appears between the background and the Lorentzian width, and "
                "the fitted width shifts.",
                "correct": True,
                "feedback": "Correct. Over a finite energy window the tails of a broad Lorentzian are almost "
                "flat, so background and Lorentzian tail are partly interchangeable: a little more "
                "background can be traded for a slightly narrower Lorentzian. The background even "
                "comes out slightly *negative*, which is unphysical and is your clue that the data "
                "cannot cleanly separate the two.",
            },
            {
                "answer": "Nothing: the background really is zero in this simulated data, so adding a "
                "parameter for it makes no difference.",
                "correct": False,
                "feedback": "The fitted level does come out close to zero, but the *structure* of the posterior "
                "changes: the background is correlated with the Lorentzian width, and the width "
                "itself moves. The fit no longer knows the background is zero, and it shows.",
            },
            {
                "answer": "The correlation between the two areas disappears, because the background absorbs "
                "the shared intensity.",
                "correct": False,
                "feedback": "That correlation comes from the two components overlapping near zero energy "
                "transfer, which a flat background cannot mimic. It survives essentially unchanged.",
            },
            {
                "answer": "The sampling fails, because the model becomes degenerate.",
                "correct": False,
                "feedback": "Strongly correlated is not the same as degenerate. The sampler copes fine — it "
                "simply shows you a tilted ridge instead of a round blob. A true degeneracy would "
                "show up as a posterior that runs off to the bounds.",
            },
        ],
    }
]

q8 = [
    {
        "question": "In the jump-diffusion model Γ(Q) = ħDQ²/(1 + DτQ²), fitted to the widths and areas. "
        "Do you expect D and τ to be correlated?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "Yes: the low-Q slope fixes D and the high-Q plateau fixes ħ/τ, but in between the "
                "two act against each other, so an increase in D can be partly compensated by an "
                "increase in τ.",
                "correct": True,
                "feedback": "Correct. D appears in both the numerator and the denominator, so raising D steepens "
                "the low-Q rise but also brings the bend forward; raising τ pushes the plateau down "
                "again. Only if you have data well into both limits are the two cleanly separated — "
                "and the corner plot tells you at a glance how well you did.",
            },
            {
                "answer": "No: D is determined only at low Q and τ only at high Q, so they are independent by "
                "construction.",
                "correct": False,
                "feedback": "That is the ideal case, and it is why measuring a wide Q range matters. In practice "
                "most of your points lie in the crossover region, where the curve depends on both, "
                "and the two become correlated.",
            },
            {
                "answer": "No: they have different units, so they cannot be correlated.",
                "correct": False,
                "feedback": "Correlation is about whether a change in one can be compensated by a change in the "
                "other. Units have nothing to do with it — the correlation coefficient is "
                "dimensionless.",
            },
            {
                "answer": "Yes, and the scale parameter is equally strongly correlated with both.",
                "correct": False,
                "feedback": "The scale is bound to the *areas*, while D and τ set the *widths*. It is therefore "
                "constrained by largely separate information and stays much more independent.",
            },
        ],
    }
]

q9 = [
    {
        "question": "Why is sampling the global (simultaneous) fit so much slower than sampling one Q at "
        "a time?",
        "type": "multiple_choice",
        "answers": [
            {
                "answer": "Both because each model evaluation covers all Q, and because the posterior has "
                "many more dimensions, which needs far more samples to explore.",
                "correct": True,
                "feedback": "Correct, and the second reason is the more serious one. A per-Q model has a handful "
                "of parameters; the global model keeps a few shared ones plus a whole set per Q. "
                "The cost of a fit grows mildly with the number of parameters, but the cost of "
                "*mapping out* a posterior grows much faster.",
            },
            {
                "answer": "Only because there are eight times as many data points.",
                "correct": False,
                "feedback": "That accounts for the cost of a single likelihood evaluation, which is roughly a "
                "factor of eight. The observed slowdown is far larger than that, because the "
                "posterior is also much higher-dimensional.",
            },
            {
                "answer": "Because the global fit needs a much longer burn-in to find the minimum, but the "
                "same number of samples afterwards.",
                "correct": False,
                "feedback": "The burn-in does get longer, but the number of samples needed to characterise the "
                "posterior grows too — with more parameters there is much more volume to cover.",
            },
            {
                "answer": "Because simultaneous fitting is done analytically and analytic derivatives are "
                "expensive.",
                "correct": False,
                "feedback": "DREAM does not use derivatives at all: it only evaluates the model. The cost is the "
                "number of evaluations needed, which is set by the dimension of the parameter space.",
            },
        ],
    }
]
