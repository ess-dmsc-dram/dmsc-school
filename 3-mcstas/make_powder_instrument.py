import mcstasscript as ms


def make(**kwargs):
    instrument = ms.McStas_instr("powder", **kwargs)

    return instrument
