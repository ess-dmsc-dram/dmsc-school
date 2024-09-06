import mcstasscript as ms


def make(**kwargs):
    instrument = ms.McStas_instr("SANS", **kwargs)

    # Value used when reading data to multiply all weights in order to units from intensity to counts, set this to the time span of the experiment.
    instrument.add_parameter(
        "double", "integration_time", value=1, comment="[s] Time span of experiment"
    )

    instrument.add_component(
        "init", "Union_init"
    )  # Necessary for current version of Union in McStas 3.X

    src = instrument.add_component("source", "ESS_butterfly")
    src.yheight = 0.03
    src.focus_xw = 0.02
    src.focus_yh = 0.02
    src.cold_frac = 0.95
    src.dist = "sample_distance + detector_distance"
    instrument.add_parameter(
        "double", "wavelength", value=6.0, comment="[AA]  Mean wavelength of neutrons"
    )
    instrument.add_parameter(
        "double",
        "d_wavelength",
        value=3.0,
        comment="[AA]  Wavelength spread of neutrons",
    )
    src.Lmin = "wavelength - 0.5*d_wavelength"
    src.Lmax = "wavelength + 0.5*d_wavelength"
    instrument.add_parameter(
        "double", "n_pulses", value=1.0, comment="[1] Number of pulses from source"
    )
    src.n_pulses = "n_pulses"
    src.acc_power = "2*(n_pulses/14)"
    src.append_EXTEND("// Compensate for lack of guide with weight increase")
    src.append_EXTEND("p*=3;")

    sample_dist = instrument.add_parameter(
        "double", "sample_distance", value=8.0, comment="[m] Source Sample distance"
    )
    sample_position = instrument.add_component("sample_position", "Arm")
    sample_position.set_AT([0, 0, "sample_distance"], RELATIVE=src)

    beam_window = instrument.add_component("beam_window", "Incoherent")
    beam_window.set_AT(-0.05, sample_position)
    beam_window.set_parameters(
        xwidth=0.05,
        yheight=0.05,
        zdepth=0.008,
        target_z="detector_distance",
        target_y=0.25,
        focus_xw=0.06,
        focus_yh=0.55,
        p_interact="0.1 + enable_sample*0.4",
        sigma_abs=4 * 0.231,
        sigma_inc=11,
        Vc=66.4,
    )

    enable_sample = instrument.add_parameter(
        "double",
        "enable_sample",
        value=0,
        comment="[1] 0 for nothing, 1 for SANS sample",
    )
    enable_sample.add_option(0, options_are_legal=True)
    enable_sample.add_option(1, options_are_legal=True)

    sample_conventional = instrument.add_component(
        "sample", "SANS_spheres2"
    )
    sample_conventional.xwidth = 0.02
    sample_conventional.yheight = 0.02
    sample_conventional.zthick = 0.0015
    sample_conventional.sc_aim = 0.95
    sample_conventional.sans_aim = 0.95
    sample_conventional.phi = 0.004
    sample_conventional.dsdw_inc = 0.08
    sample_conventional.Qmaxd = "1.5*2.0*2.0*PI/(wavelength-0.5*d_wavelength)*sin(0.5*atan(0.5/detector_distance))"
    # sample_conventional.dsdw_inc = 0.0000008
    sample_conventional.R = 90
    sample_conventional.set_WHEN("enable_sample == 1")
    sample_conventional.set_AT(0, RELATIVE="sample_position")

    dist = instrument.add_parameter(
        "double", "detector_distance", value=2.0, comment="[m] Sample_detector_distance"
    )
    detector_position = instrument.add_component("detector_position", "Arm")
    detector_position.set_AT([0, 0, dist], RELATIVE=sample_position)

    """
    tof_wave = instrument.add_component("tof_wave", "TOFLambda_monitor")
    tof_wave.set_parameters(nL=500, nt=500, tmin="1E6*t_min", tmax="1E6*t_max",
                            xwidth=1.0, yheight=1.0,
                            Lmin="wavelength - 0.5*d_wavelength",
                            Lmax="wavelength + 0.5*d_wavelength",
                            filename='"tof_wave.dat"', restore_neutron=1)
    tof_wave.set_AT(0, RELATIVE=detector_position)

    tof_wave_pulses = instrument.add_component("tof_wave_pulses", "TOFLambda_monitor")
    tof_wave_pulses.set_parameters(nL=500, nt=500, tmin="1E6*t_min", tmax="1E6*t_max_pulses",
                            xwidth=1.0, yheight=1.0,
                            Lmin="wavelength - 0.5*d_wavelength",
                            Lmax="wavelength + 0.5*d_wavelength",
                            filename='"tof_wave_pulses.dat"', restore_neutron=1)
    tof_wave_pulses.set_AT(0, RELATIVE=detector_position)
    """

    """
    enable_beamstop = instrument.add_parameter("double", "enable_beamstop", value=0,
                                               comment="[1] 0 for nothing, 1 for beamstop")
    enable_beamstop.add_option(0, options_are_legal=True)
    enable_beamstop.add_option(1, options_are_legal=True)

    mon = instrument.add_component("monitor", "PSD_monitor")
    mon.nx = 100
    mon.ny = 100
    mon.filename = '"psd.dat"'
    mon.xwidth = 0.08
    mon.yheight = 0.08
    mon.restore_neutron = 1
    mon.set_AT(-0.04, detector_position)

    beamstop = instrument.add_component("beamstop", "Beamstop")
    beamstop.set_AT(-0.035, detector_position)
    beamstop.set_WHEN("enable_beamstop == 1")
    beamstop.set_parameters(xwidth=0.25, yheight=0.0215)

    mon = instrument.add_component("monitor_after", "PSD_monitor")
    mon.nx = 100
    mon.ny = 100
    mon.filename = '"psd_after.dat"'
    mon.xwidth = 0.08
    mon.yheight = 0.08
    mon.restore_neutron = 1
    mon.set_AT(0.04, detector_position)
    """

    # Set up Al material with incoherent and powder
    Al_incoherent = instrument.add_component("Al_incoherent", "Incoherent_process")
    Al_incoherent.sigma = "4*0.0082"
    Al_incoherent.packing_factor = 1
    Al_incoherent.unit_cell_volume = 66.4

    Al_powder = instrument.add_component("Al_powder", "Powder_process")
    Al_powder.reflections = '"Al.laz"'

    Al = instrument.add_component("Al", "Union_make_material")
    Al.process_string = '"Al_incoherent,Al_powder"'
    Al.my_absorption = "100*4*0.231/66.4"

    # Set up He3 material with incoherent scattering
    def mu_gas(sigma, bars, temperature_C):
        pressure_Pa = bars * 1e5
        number_density_mol_per_m3 = pressure_Pa / (8.3145 * (temperature_C + 273.15))
        number_density_per_m3 = number_density_mol_per_m3 * 6.022e23
        number_density_per_A3 = number_density_per_m3 / 1e30
        return sigma * number_density_per_A3 * 100

    He3_pressure_bars = 3
    He3_temperature_C = 25

    He3_inc = instrument.add_component("He3_inc", "Incoherent_process")
    He3_inc.sigma = mu_gas(1.6, bars=He3_pressure_bars, temperature_C=He3_temperature_C)
    He3_inc.unit_cell_volume = 100

    He3 = instrument.add_component("He3", "Union_make_material")
    He3.process_string = '"He3_inc"'
    He3.my_absorption = mu_gas(
        5333, bars=He3_pressure_bars, temperature_C=He3_temperature_C
    )

    # Create detector casing with gas volume inside
    casing = instrument.add_component("Al_container", "Union_cylinder")
    casing.set_parameters(
        yheight=0.55, radius=0.03, p_interact=0.3, material_string='"Al"', priority=300
    )
    casing.set_AT([0, 0.25, 0], detector_position)

    He3_gas = instrument.add_component("He3_gas", "Union_cylinder")
    He3_gas.set_AT_RELATIVE(casing)
    He3_gas.set_parameters(
        yheight=0.47, radius=casing.radius - 4e-3, material_string='"He3"', priority=310
    )

    buble = instrument.add_component("gas_buble1", "Union_sphere")
    buble.set_parameters(
        radius=0.99 * He3_gas.radius, material_string='"Vacuum"', priority=500
    )
    buble.set_AT([0, -0.347 * He3_gas.yheight, 0], RELATIVE=He3_gas)

    """
    buble_1 = instrument.add_component("gas_buble1", "Union_sphere")
    buble_1.set_parameters(radius=0.85*He3_gas.radius,
                           material_string='"Vacuum"', priority=400)
    buble_1.set_AT([0.02*He3_gas.radius, -0.347*He3_gas.yheight, 0.14*He3_gas.radius], RELATIVE=He3_gas)

    buble_2 = instrument.add_component("gas_buble2", "Union_sphere")
    buble_2.set_parameters(radius=0.8*He3_gas.radius,
                           material_string='"Vacuum"', priority=401)
    buble_2.set_AT([-0.16*He3_gas.radius, -0.35*He3_gas.yheight, -0.095*He3_gas.radius], RELATIVE=He3_gas)

    buble_3 = instrument.add_component("gas_buble3", "Union_sphere")
    buble_3.set_parameters(radius=0.7*He3_gas.radius,
                           material_string='"Vacuum"', priority=402)
    buble_3.set_AT([0.15*He3_gas.radius, -0.345*He3_gas.yheight, -0.25*He3_gas.radius], RELATIVE=He3_gas)
    """

    # Reference detectors
    """
    ref = instrument.add_component("reference", "PSDlin_monitor", after=beamstop)
    ref.set_parameters(xwidth=2*He3_gas.radius, yheight=He3_gas.yheight, vertical=1,
                       nbins=300, filename='"reference.dat"', restore_neutron=1)
    ref.set_AT([0, 0.5*casing.yheight, 0], RELATIVE=detector_position)
    """

    # Parameters for time of flight limits
    instrument.add_declare_var("double", "t_min")
    instrument.add_declare_var("double", "t_max")
    instrument.add_declare_var("double", "t_max_pulses")

    instrument.append_initialize(
        "t_min = (wavelength - d_wavelength)*(sample_distance - 0.02 + detector_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = (wavelength + d_wavelength)*(sample_distance + 0.2 + detector_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = t_max + 3.0E-3; // Account for ESS pulse structure"
    )
    instrument.append_initialize(
        "t_max_pulses = t_max + 3.0E-3 + (n_pulses-1.0)*1.0/14.0; // Account for n_pulses"
    )
    instrument.add_declare_var("char", "options", array=256)
    instrument.append_initialize(
        'sprintf(options,"square, y bins=200, t limits=[%g %g] bins=300",t_min,t_max);'
    )

    """
    ref = instrument.add_component("reference_tof", "Monitor_nD", after=beamstop)
    ref.set_parameters(xwidth=2*He3_gas.radius, yheight=He3_gas.yheight,
                       filename='"reference_tof.dat"', restore_neutron=1)
    ref.options = "options"
    ref.set_AT([0, 0.5*casing.yheight, 0], RELATIVE=detector_position)
    """

    detector = instrument.add_component(
        "signal", "Union_abs_logger_1D_space", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 300
    detector.filename = '"detector_signal.dat"'

    detector = instrument.add_component(
        "signal_tof", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 200
    detector.time_min = "t_min"
    detector.time_max = "t_max"
    detector.time_bins = 300
    detector.filename = '"detector_signal_tof.dat"'

    detector = instrument.add_component(
        "signal_tof_all", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 200
    detector.time_min = "t_min"
    detector.time_max = "t_max_pulses"
    detector.time_bins = 300
    detector.filename = '"detector_signal_tof_all.dat"'

    detector_event = instrument.add_component(
        "signal_tof_event", "Union_abs_logger_1D_space_event", RELATIVE=He3_gas
    )
    detector_event.target_geometry = '"He3_gas"'
    detector_event.yheight = He3_gas.yheight
    detector_event.n = 200
    detector_event.filename = '"detector_signal_event.dat"'

    """
    abs_logger_zy = instrument.add_component(
        "abs_logger_space_zy", "Union_abs_logger_2D_space"
    )
    abs_logger_zy.set_AT(0, RELATIVE=He3_gas)
    abs_logger_zy.set_parameters(
        D_direction_1='"z"',
        n1=300,
        D1_min=-0.04,
        D1_max=0.04,
        D_direction_2='"y"',
        n2=300,
        D2_min=-0.26,
        D2_max=0.26,
        filename='"abs_logger_zy.dat"',
    )
    """

    master = instrument.add_component("master", "Union_master")
    stop = instrument.add_component("stop", "Union_stop")

    instrument.settings(custom_flags="--bufsiz=10000000")

    return instrument
