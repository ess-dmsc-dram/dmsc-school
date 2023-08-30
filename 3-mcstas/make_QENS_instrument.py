import numpy as np
import mcstasscript as ms


def make(**kwargs):
    instrument = ms.McStas_instr("QENS", **kwargs)

    # Value used when reading data to multiply all weights in order to units from intensity to counts, set this to the time span of the experiment.
    instrument.add_parameter(
        "double", "integration_time", value=1, comment="[s] Time span of experiment"
    )

    # Calculations
    detector_offset = instrument.add_declare_var(
        "double", "detector_offset", value=0.25
    )
    analyzer_angle = instrument.add_declare_var("double", "analyzer_angle")
    instrument.append_initialize(
        "analyzer_angle = RAD2DEG*0.5*atan(detector_offset/analyzer_distance);"
    )
    instrument.append_initialize('printf("Analyzer_angle: %lf \\n", analyzer_angle);')

    instrument.add_declare_var("double", "backscattering_wavelength")
    instrument.append_initialize(
        "backscattering_wavelength = 2*analyzer_d*sin(DEG2RAD*0.5*(180-2.0*analyzer_angle));"
    )
    instrument.add_declare_var("double", "backscattering_energy")
    instrument.append_initialize(
        "backscattering_energy = (2.0*PI/backscattering_wavelength)*K2V*(2.0*PI/backscattering_wavelength)*K2V*VS2E;"
    )

    instrument.append_initialize(
        'printf("2 theta: %lf \\n", DEG2RAD*0.5*(180-2.0*analyzer_angle));'
    )
    instrument.append_initialize(
        'printf("Selected wavelength: %lf \\n", 2*analyzer_d*sin(DEG2RAD*0.5*(180-2.0*analyzer_angle)));'
    )

    instrument.add_parameter(
        "double", "energy_width_ueV", comment="Simulated energy range in micro eV"
    )
    instrument.add_declare_var("double", "energy_width_meV")
    instrument.append_initialize("energy_width_meV = 1E-3*energy_width_ueV;")

    instrument.add_declare_var("double", "min_energy")
    instrument.add_declare_var("double", "max_energy")
    instrument.append_initialize(
        "min_energy = backscattering_energy - 0.5*energy_width_meV;"
    )
    instrument.append_initialize(
        "max_energy = backscattering_energy + 0.5*energy_width_meV;"
    )

    instrument.add_declare_var("double", "min_wavelength")
    instrument.add_declare_var("double", "max_wavelength")

    instrument.append_initialize("min_wavelength = 2.0*PI/(sqrt(max_energy)*SE2V*V2K);")
    instrument.append_initialize("max_wavelength = 2.0*PI/(sqrt(min_energy)*SE2V*V2K);")

    src = instrument.add_component("source", "ESS_butterfly")
    src.yheight = 0.03
    src.focus_xw = 0.025
    src.focus_yh = 0.025
    src.cold_frac = 0.95
    src.dist = "sample_distance"
    # instrument.add_parameter("double", "wavelength", value=6.26, comment="[AA]  Mean wavelength of neutrons")
    # instrument.add_parameter("double", "d_wavelength", value=3.0, comment="[AA]  Wavelength spread of neutrons")
    src.Lmin = "min_wavelength"
    src.Lmax = "max_wavelength"
    instrument.add_parameter(
        "double", "n_pulses", value=3.0, comment="Number of pulses from source"
    )
    src.acc_power = "2*(n_pulses/14)"
    src.n_pulses = "n_pulses"
    src.append_EXTEND(
        "// Compensate for lack of guide and analyzer area with weight increase"
    )
    src.append_EXTEND("p*=7e5;")

    """
    enable_chopper = instrument.add_parameter("double", "enable_chopper", value=1,
                                             comment="0 for no chopper, 1 for chopper")
    enable_chopper.add_option(1, options_are_legal=True)
    enable_chopper.add_option(0, options_are_legal=True)

    chopper = instrument.add_component("chopper", "DiskChopper")
    chopper.set_parameters(yheight=0.05, radius=0.7, nu="chopper_frequency",
                           nslit=1.0, delay="chopper_delay", theta_0="chopper_theta")
    chopper.set_AT("chopper_distance", RELATIVE=src)
    chopper.set_WHEN("enable_chopper==1")
    """

    sample_dist = instrument.add_parameter(
        "double", "sample_distance", value=8.0, comment="[m] Source Sample distance"
    )
    sample_position = instrument.add_component("sample_position", "Arm")
    sample_position.set_AT([0, 0, "sample_distance"], RELATIVE=src)

    instrument.add_declare_var("double", "t_min_sample")
    instrument.add_declare_var("double", "t_max_sample")
    instrument.add_declare_var("double", "t_max_sample_pulses")
    instrument.append_initialize(
        "t_min_sample = (min_wavelength)*(sample_distance - 0.05)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max_sample = (max_wavelength)*(sample_distance + 0.2)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max_sample_pulses = t_max_sample + 3.0E-3; // Account for ESS pulse structure"
    )

    """
    tof_wave = instrument.add_component("tof_wave", "TOFLambda_monitor")
    tof_wave.set_parameters(nL=500, nt=500, tmin="1E6*t_min_sample", tmax="1E6*t_max_sample",
                            xwidth=1.0, yheight=1.0,
                            Lmin="min_wavelength",
                            Lmax="max_wavelength",
                            filename='"tof_wave.dat"', restore_neutron=1)
    tof_wave.set_AT(0, RELATIVE=sample_position)

    tof_wave_pulses = instrument.add_component("tof_wave_pulses", "TOFLambda_monitor")
    tof_wave_pulses.set_parameters(nL=500, nt=500, tmin="1E6*t_min_sample", tmax="1E6*t_max_sample_pulses",
                            xwidth=1.0, yheight=1.0,
                            Lmin="min_wavelength",
                            Lmax="max_wavelength",
                            filename='"tof_wave_pulses.dat"', restore_neutron=1)
    tof_wave_pulses.set_AT(0, RELATIVE=sample_position)
    """

    instrument.add_component("init", "Union_init")

    sample_choice = instrument.add_parameter(
        "string", "sample_choice", value='"Elastic"', comment="Choice of sample type"
    )
    sample_choice.add_option('"Elastic"', options_are_legal=True)
    sample_choice.add_option('"Known_quasi-elastic"', options_are_legal=True)
    sample_choice.add_option('"Unknown_quasi-elastic"', options_are_legal=True)

    instrument.add_declare_var("double", "enable_elastic")
    instrument.add_declare_var("double", "enable_known_quasi")
    instrument.add_declare_var("double", "enable_unknown_quasi")

    instrument.append_initialize(
        """
    if (strcmp(sample_choice, "Elastic") == 0) {
        enable_elastic = 1;
        enable_known_quasi = 0;
        enable_unknown_quasi = 0;
    } else if (strcmp(sample_choice, "Known_quasi-elastic") == 0) {
        enable_elastic = 0;
        enable_known_quasi = 1;
        enable_unknown_quasi = 0;
    } else if (strcmp(sample_choice, "Unknown_quasi-elastic") == 0) {
        enable_elastic = 0;
        enable_known_quasi = 0;
        enable_unknown_quasi = 1;
    } else {
        printf("sample_choice parameter did not match any sample choice! \\n");
        exit(1);
    }
    """
    )

    # Elastic
    incoherent = instrument.add_component("incoherent", "Incoherent_process")
    incoherent.set_parameters(sigma=3.08, unit_cell_volume=20.0)

    material = instrument.add_component("elastic_material", "Union_make_material")
    material.set_parameters(my_absorption=0.57, process_string='"incoherent"')

    # Known quasi
    instrument.add_parameter(
        "double",
        "gamma_ueV",
        value=10,
        comment="[ueV] Energy width of known quasi-elastic sample",
    )
    gamma = instrument.add_declare_var("double", "gamma_meV")
    instrument.append_initialize("gamma_meV = 1E-3*gamma_ueV;")
    quasi1 = instrument.add_component("quasi_incoherent", "Incoherent_process")
    quasi1.set_parameters(sigma=3.08, gamma=gamma, unit_cell_volume=20.0, f_QE=0.99)

    material = instrument.add_component(
        "known_quasi_elastic_material", "Union_make_material"
    )
    material.set_parameters(my_absorption=0.57, process_string='"quasi_incoherent"')

    # Unknown quasi
    quasi1 = instrument.add_component("quasi_incoherent_1", "Incoherent_process")
    quasi1.set_parameters(sigma=1.0, gamma=0.0008, unit_cell_volume=20.0, f_QE=0.99)

    quasi2 = instrument.add_component("quasi_incoherent_2", "Incoherent_process")
    quasi2.set_parameters(sigma=2.2, gamma=0.0035, unit_cell_volume=20.0, f_QE=0.99)

    material = instrument.add_component(
        "unknown_quasi_elastic_material", "Union_make_material"
    )
    material.set_parameters(
        my_absorption=0.57, process_string='"quasi_incoherent_1,quasi_incoherent_2"'
    )

    analyzer_direction = instrument.add_declare_var(
        "double", "analyzer_direction", value=30
    )
    dist = instrument.add_parameter(
        "double", "analyzer_distance", value=3.0, comment="[m] Sample analyzer distance"
    )

    all_samples = dict(
        radius=0.01,
        yheight=0.03,
        p_interact=0.4,
        target_z=dist,
        focus_xw=0.01,
        focus_xh=0.01,
    )

    cylinder = instrument.add_component("elastic_sample", "Union_cylinder")
    cylinder.set_parameters(
        **all_samples,
        material_string='"elastic_material"',
        priority=10,
        number_of_activations="enable_elastic",
        visualize="enable_elastic",
    )
    cylinder.set_AT(0, RELATIVE=sample_position)
    cylinder.set_ROTATED([0, analyzer_direction, 0], RELATIVE=sample_position)

    cylinder = instrument.add_component("known_quasi_elastic_sample", "Union_cylinder")
    cylinder.set_parameters(
        **all_samples,
        material_string='"known_quasi_elastic_material"',
        priority=11,
        number_of_activations="enable_known_quasi",
        visualize="enable_known_quasi",
    )
    cylinder.set_AT(0, RELATIVE=sample_position)
    cylinder.set_ROTATED([0, analyzer_direction, 0], RELATIVE=sample_position)

    cylinder = instrument.add_component(
        "unknown_quasi_elastic_sample", "Union_cylinder"
    )
    cylinder.set_parameters(
        **all_samples,
        material_string='"unknown_quasi_elastic_material"',
        priority=12,
        number_of_activations="enable_unknown_quasi",
        visualize="enable_unknown_quasi",
    )
    cylinder.set_AT(0, RELATIVE=sample_position)
    cylinder.set_ROTATED([0, analyzer_direction, 0], RELATIVE=sample_position)

    master = instrument.add_component("sample_master", "Union_master")

    analyzer_dir = instrument.add_component("analyzer_dir", "Arm")
    analyzer_dir.set_AT(0, sample_position)
    analyzer_dir.set_ROTATED([0, analyzer_direction, 0], RELATIVE=sample_position)

    """
    mon = instrument.add_component("monitor", "PSD_monitor")
    mon.nx = 100
    mon.ny = 100
    mon.filename = '"psd.dat"'
    mon.xwidth = 0.08
    mon.yheight = 0.08
    mon.restore_neutron = 1
    mon.set_AT([0,0,dist], RELATIVE=analyzer_dir)
    """

    analyzer_pos = instrument.add_component("analyzer_pos", "Arm")
    analyzer_pos.set_AT([0, 0, dist], RELATIVE=analyzer_dir)

    analyzer_orientation = instrument.add_component("analyzer_orientation", "Arm")
    analyzer_orientation.set_AT(0, RELATIVE=analyzer_pos)
    analyzer_orientation.set_ROTATED([0, 90, 0], RELATIVE=analyzer_pos)

    # Si (111) as Miracles: Q = 2*pi/3.135
    analyzer_d = instrument.add_declare_var("double", "analyzer_d", value=3.135)
    analyzer_q = instrument.add_declare_var(
        "double", "analyzer_q", value=2 * np.pi / 3.135
    )

    analyzer = instrument.add_component("analyzer", "Monochromator_flat")
    analyzer.set_parameters(
        zwidth=0.05, yheight=0.05, r0=0.7, Q=analyzer_q, mosaich=30, mosaicv=30
    )
    analyzer.set_AT(0, RELATIVE=analyzer_orientation)
    analyzer.set_ROTATED([0, 0, "analyzer_angle"], RELATIVE=analyzer_orientation)

    return_orientation = instrument.add_component("return_orientation", "Arm")
    return_orientation.set_AT(0, RELATIVE=analyzer_pos)
    return_orientation.set_ROTATED([0, 180, 0], RELATIVE=analyzer_pos)

    return_dir = instrument.add_component("return_dir", "Arm")
    return_dir.set_AT(0, return_orientation)
    return_dir.set_ROTATED(["-2.0*analyzer_angle", 0, 0], RELATIVE=return_orientation)

    slit = instrument.add_component("detector_slit", "Slit")
    slit.set_parameters(xwidth=0.06, yheight=0.1)
    slit.set_AT([0, 0, "analyzer_distance - 0.1"], RELATIVE=return_dir)
    slit.append_EXTEND(f"// Simulate detector glitch with timing")
    slit.append_EXTEND(f"if (y > 0.14*0.08 && y < 0.24*0.08 && rand01() > 0.23)")
    slit.append_EXTEND(f"t += 0.00034;")

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

    Cap_incoherent = instrument.add_component("Cap_incoherent", "Incoherent_process")
    Cap_incoherent.sigma = 80
    Cap_incoherent.packing_factor = 1
    Cap_incoherent.unit_cell_volume = 120

    Cap = instrument.add_component("Cap", "Union_make_material")
    Cap.process_string = '"Cap_incoherent"'
    Cap.my_absorption = 0.8

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
        yheight=0.1, radius=0.03, p_interact=0.25, material_string='"Al"', priority=300
    )
    casing.set_AT([0, 0, dist], return_dir)

    He3_gas = instrument.add_component("He3_gas", "Union_cylinder")
    He3_gas.set_AT_RELATIVE(casing)
    He3_gas.set_parameters(
        yheight=casing.yheight - 0.02,
        radius=casing.radius - 4e-3,
        material_string='"He3"',
        priority=310,
        p_interact=0.2,
    )

    """
    size_fraction = 0.95
    buble = instrument.add_component("buble", "Union_cylinder")
    buble.set_AT([0, 0.1*casing.yheight, -(1-size_fraction)*He3_gas.radius], casing)
    buble.set_parameters(yheight=0.01, radius=0.999*size_fraction*He3_gas.radius,
                           material_string='"Vacuum"', priority=311, p_interact=0.2)
    """

    """
    cap_dist = 0.35
    Caps = instrument.add_component("Caps", "Union_cylinder")
    Caps.set_AT([0, 0.25*casing.yheight, cap_dist], casing)
    Caps.set_parameters(yheight=0.1*casing.yheight, radius=casing.radius-2E-3,
                        material_string='"Cap"', priority=290, p_interact=0.45,
                        target_z=-cap_dist, target_y=0, target_x=0,
                        focus_xh=0.01, focus_xw=0.02)
    """

    instrument.add_declare_var("double", "t_min")
    instrument.add_declare_var("double", "t_max")
    instrument.add_declare_var("double", "t_max_pulses")
    instrument.append_initialize(
        "t_min = (backscattering_wavelength)*(sample_distance - 0.1 + 2*analyzer_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = (backscattering_wavelength)*(sample_distance + 1.0 + 2*analyzer_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = t_max + 4.0E-3; // Account for ESS pulse structure"
    )
    instrument.append_initialize(
        "t_max_pulses = t_max + (n_pulses-1.0)*1.0/14.0; // Account for n_pulses"
    )

    detector = instrument.add_component(
        "signal_space", "Union_abs_logger_1D_space", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 50
    detector.filename = '"detector_signal_space.dat"'

    detector = instrument.add_component(
        "signal_time", "Union_abs_logger_1D_time", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.time_min = "t_min"
    detector.time_max = "t_max"
    detector.n = 200
    detector.filename = '"detector_signal_time.dat"'

    detector = instrument.add_component(
        "signal_tof", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 50
    detector.time_min = "t_min"
    detector.time_max = "t_max"
    detector.time_bins = 300
    detector.filename = '"detector_signal_2D.dat"'

    detector = instrument.add_component(
        "signal_tof_all", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
    )
    detector.target_geometry = '"He3_gas"'
    detector.yheight = He3_gas.yheight
    detector.n = 50
    detector.time_min = "t_min"
    detector.time_max = "t_max_pulses"
    detector.time_bins = 300
    detector.filename = '"detector_signal_2D_all.dat"'

    detector_event = instrument.add_component(
        "signal_tof_event", "Union_abs_logger_1D_space_event", RELATIVE=He3_gas
    )
    detector_event.target_geometry = '"He3_gas"'
    detector_event.yheight = He3_gas.yheight
    detector_event.n = 200
    detector_event.filename = '"detector_signal_event.dat"'

    """
    abs_logger_zy = instrument.add_component("abs_logger_space_zy", "Union_abs_logger_2D_space")
    abs_logger_zy.set_AT(0, RELATIVE=He3_gas)
    abs_logger_zy.set_parameters(D_direction_1='"z"', n1=300,
                                 D1_min=-0.04, D1_max=0.04,
                                 D_direction_2='"y"', n2=300,
                                 D2_min=-0.26, D2_max=0.26,
                                 filename='"abs_logger_zy.dat"')
    """

    master = instrument.add_component("detector_master", "Union_master")
    stop = instrument.add_component("stop", "Union_stop")

    return instrument


def add_chopper_code(instrument):
    src = instrument.get_component("source")
    src.tfocus_dist = "chopper_distance"
    src.tfocus_time = "chopper_delay"
    src.tfocus_width = "1.5*chopper_time_width"

    instrument.add_parameter(
        "double",
        "frequency_multiplier",
        value=3,
        comment="Ratio between chopper and source frequency",
    )
    instrument.add_declare_var(
        "double",
        "chopper_distance",
        value=6.5,
        comment="[m] Distance from source to chopper",
    )

    instrument.add_declare_var("double", "chopper_delay")
    instrument.append_initialize(
        "chopper_delay = 0.5*2.86E-3 + backscattering_wavelength*chopper_distance/(K2V*2*PI);"
    )

    instrument.add_declare_var("double", "chopper_frequency")
    instrument.add_declare_var("double", "chopper_theta", value=12)
    instrument.append_initialize("chopper_frequency = 14.0*frequency_multiplier;")

    instrument.add_declare_var("double", "chopper_time_width")
    instrument.append_initialize(
        "chopper_time_width = (chopper_theta/360)/chopper_frequency;"
    )
