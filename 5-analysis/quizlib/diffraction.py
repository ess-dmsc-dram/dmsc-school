q1 = [
    {
        'question': 'What could be the reason for the misfit?',
        'type': 'multiple_choice',
        'answers': [
            {
                'answer': 'The conversion parameters from TOF to d-spacing are not correct.',
                'correct': False,
                'feedback': 'The conversion parameters from TOF to d-spacing were set based on the data reduction step. '
                'While they are specific to each dataset and thus differ from those used for the Si data, the '
                'full reduction workflow has already been validated with the Si fit. Therefore, they are not '
                'the cause of the misfit in this case.',
            },
            {
                'answer': 'The lattice parameters of the LBCO phase are not correct.',
                'correct': True,
                'feedback': 'The lattice parameters of the LBCO phase were set based on the CIF data, which is a good '
                'starting point, but they are not necessarily as accurate as needed for the fit. '
                'The lattice parameters may need to be refined.',
            },
            {
                'answer': 'The peak profile parameters are not correct.',
                'correct': False,
                'feedback': 'The peak profile parameters do not change the position of the peaks, but rather their shape.',
            },
            {
                'answer': 'The background points are not correct.',
                'correct': False,
                'feedback': 'The background points affect the background level, but not the peak positions.',
            },
        ],
    }
]

q2 = [
    {
        'question': 'Which potential cause best explains the misfit?',
        'type': 'multiple_choice',
        'answers': [
            {
                'answer': 'The LBCO phase is not correctly modeled.',
                'correct': False,
                'feedback': 'In principle, this could be the case, as sometimes the presence of extra peaks in the '
                'diffraction pattern can indicate lower symmetry than the one used in the model, or that '
                'the model is not complete. However, in this case, the LBCO phase is correctly modeled based '
                'on the CIF data.',
            },
            {
                'answer': 'The LBCO phase is not the only phase present in the sample.',
                'correct': True,
                'feedback': 'The unexplained peaks are due to the presence of an impurity phase in the sample, which is '
                'not included in the current model.',
            },
            {
                'answer': 'The data reduction process introduced artifacts.',
                'correct': False,
                'feedback': 'The data reduction process is not likely to introduce such specific peaks, as it is tested '
                'and verified in the previous part of the notebook.',
            },
            {
                'answer': 'The studied sample is not LBCO, but rather a different phase.',
                'correct': False,
                'feedback': 'This could also be the case in real experiments, but in this case, we know that the sample '
                'is LBCO, as it was simulated based on the CIF data.',
            },
        ],
    }
]
