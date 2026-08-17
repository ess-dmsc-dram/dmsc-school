import mcstasscript as ms
import numpy as np


def make(**kwargs):

    # The detectors sit on a circle of radius
    #   sample_analyzer_distance - analyzer_detector_distance*cos(2*analyzer_angle) = 0.21 m
    # around the sample, so neighbouring casings (radius 0.03 m) only clear each other when
    # 2*0.21*sin(spacing/2) > 0.06 m, i.e. a spacing above 16.5 deg. 20 deg leaves 13 mm.
    # analyzer_directions = [20, 50, 80, 110, 140]
    analyzer_directions = [20, 40, 60, 80, 100, 120, 140, 160]
    plot_indices = [1, 3]  # index 1 has glitch

    instrument = ms.McStas_instr("QENS", **kwargs)

    # Value used when reading data to multiply all weights in order to units from intensity to counts, set this to the time span of the experiment.
    instrument.add_parameter(
        "double",
        "integration_time",
        value=3600 * 6,
        comment="[s] Time span of experiment",
    )

    # Calculations
    detector_offset = instrument.add_declare_var(
        "double", "detector_offset", value=0.25
    )
    analyzer_angle = instrument.add_declare_var("double", "analyzer_angle")
    instrument.append_initialize(
        "analyzer_angle = RAD2DEG*0.5*atan(detector_offset/sample_analyzer_distance);"
    )
    instrument.append_initialize('printf("Analyzer_angle: %lf \\n", analyzer_angle);')

    instrument.add_declare_var("double", "backscattering_wavelength")
    instrument.append_initialize(
        "backscattering_wavelength = 2.0*analyzer_d*sin(DEG2RAD*0.5*(180-2.0*analyzer_angle));"
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
        "double",
        "energy_width_ueV",
        value=3,
        comment="Simulated energy range in micro eV",
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

    sample_dist = instrument.add_parameter(
        "double", "sample_distance", value=8.0, comment="[m] Source Sample distance"
    )
    sample_position = instrument.add_component("sample_position", "Arm")
    sample_position.set_AT([0, 0, "sample_distance"], RELATIVE=src)
    sample_position.set_SPLIT(10)
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

    instrument.add_component("init", "Union_init")

    sample_analyzer_dist = instrument.add_parameter(
        "double",
        "sample_analyzer_distance",
        value=3.0,
        comment="[m] Sample analyzer distance",
    )

    analyzer_detector_dist = instrument.add_parameter(
        "double",
        "analyzer_detector_distance",
        value=2.8,
        comment="[m] Sample analyzer distance",
    )

    sample_choice = instrument.add_parameter(
        "string",
        "sample_choice",
        value='"Elastic"',
        comment="Choice of sample type, Elastic or QENS_sample",
    )
    sample_choice.add_option('"Elastic"', options_are_legal=True)
    sample_choice.add_option('"QENS_sample"', options_are_legal=True)

    # set up samples with direction code
    instrument.add_user_var("int", "channel_index")

    selector = instrument.add_component("channel_selector", "Arm")
    selector.append_EXTEND(f"""
    channel_index = floor({len(analyzer_directions)}*rand01());
    """)

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

    instrument.add_declare_var("double", "t_min")
    instrument.add_declare_var("double", "t_max")
    instrument.add_declare_var("double", "t_max_pulses")
    instrument.add_declare_var("double", "total_sample_detector_distance")
    instrument.append_initialize(
        "total_sample_detector_distance = sample_analyzer_distance + analyzer_detector_distance;"
    )
    instrument.append_initialize(
        "t_min = (backscattering_wavelength)*(sample_distance - 0.7 + total_sample_detector_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = (backscattering_wavelength)*(sample_distance + 1.0 + total_sample_detector_distance)/(K2V*2*PI);"
    )
    instrument.append_initialize(
        "t_max = t_max + 4.0E-3; // Account for ESS pulse structure"
    )
    instrument.append_initialize(
        "t_max_pulses = t_max + (n_pulses-1.0)*1.0/14.0; // Account for n_pulses"
    )

    # Si (111) as Miracles: Q = 2*pi/3.135
    analyzer_d = instrument.add_declare_var("double", "analyzer_d", value=3.135)
    analyzer_q = instrument.add_declare_var(
        "double", "analyzer_q", value=2 * np.pi / 3.135
    )

    # Calculations for q dependent quasi-elastic width
    instrument.add_declare_var("double", "hbar")
    instrument.append_initialize("hbar = 6.582119569E-16;")

    instrument.add_declare_var("double", "sample_D")
    instrument.add_declare_var("double", "sample_tau")
    instrument.add_declare_var("double", "use_inelastic")

    instrument.append_initialize("""
        if (strcmp(sample_choice, "Elastic") == 0) {
            use_inelastic = 0.0;
            sample_D = 2.4E-9; // defaults
            sample_tau = 1E-12;
        } else if (strcmp(sample_choice, "QENS_sample") == 0) {
            use_inelastic = 1.0;
            sample_D = 4.6E-10;
            sample_tau = 2.2E-11;
        } else {
            printf("sample_choice parameter did not match any sample choice! \\n");
            exit(1);
        }

    """)

    # typical values
    # D = 2.4E-9 # s
    # tau = 1E-12 # m^2/s

    for index, analyzer_direction in enumerate(analyzer_directions):
        analyzer_dir = instrument.add_component(f"analyzer_{index}_dir", "Arm")
        analyzer_dir.set_AT(0, sample_position)
        analyzer_dir.set_ROTATED([0, analyzer_direction, 0], RELATIVE=sample_position)

        instrument.add_declare_var("double", f"Q_{index}")
        instrument.append_initialize(
            f"Q_{index}=1E10*4.0*PI/backscattering_wavelength*sin(DEG2RAD*{analyzer_direction}/2.0);"
        )

        c_gamma = f"use_inelastic*1E3*hbar*sample_D*Q_{index}*Q_{index}/(1.0+sample_D*sample_tau*Q_{index}*Q_{index})"

        instrument.append_initialize(
            f'if (!mcdotrace) printf("gamma_value {index} = %lf", {c_gamma});'
        )

        WHEN_expression = f"channel_index=={index}"

        inc = instrument.add_component(f"Incoherent_sample_{index}", "Incoherent")
        inc.set_RELATIVE(analyzer_dir)
        inc.set_WHEN(WHEN_expression)

        inc.set_parameters(
            radius=0.01,
            yheight=0.03,
            target_z=sample_analyzer_dist,
            focus_xw=0.03,
            focus_yh=0.03,
            gamma=c_gamma,
            f_QE=0.92,
            sigma_abs=2.0,
        )

        analyzer_pos = instrument.add_component(f"analyzer_{index}_pos", "Arm")
        analyzer_pos.set_AT([0, 0, sample_analyzer_dist], RELATIVE=analyzer_dir)

        analyzer_orientation = instrument.add_component(
            f"analyzer_{index}_orientation", "Arm"
        )
        analyzer_orientation.set_AT(0, RELATIVE=analyzer_pos)
        analyzer_orientation.set_ROTATED([0, 90, 0], RELATIVE=analyzer_pos)

        return_orientation = instrument.add_component(
            f"return_orientation_{index}", "Arm"
        )
        return_orientation.set_AT(0, RELATIVE=analyzer_pos)
        return_orientation.set_ROTATED([0, 180, 0], RELATIVE=analyzer_pos)

        return_dir = instrument.add_component(f"return_dir_{index}", "Arm")
        return_dir.set_AT(0, return_orientation)
        return_dir.set_ROTATED(
            ["-2.0*analyzer_angle", 0, 0], RELATIVE=return_orientation
        )

        analyzer = instrument.add_component(f"analyzer_{index}", "Monochromator_flat")
        analyzer.set_parameters(
            zwidth=0.15, yheight=0.05, r0=0.7, Q=analyzer_q, mosaich=30, mosaicv=30
        )
        analyzer.set_AT(0, RELATIVE=analyzer_orientation)
        analyzer.set_ROTATED([0, 0, "analyzer_angle"], RELATIVE=analyzer_orientation)

        # Add a slit before each casing
        slit = instrument.add_component(f"Slit_{index}", "Slit")
        slit.set_parameters(xwidth=0.06, yheight=0.1)
        slit.set_AT(
            [0, 0, f"{analyzer_detector_dist.name} - 0.05"], RELATIVE=return_dir
        )

        if index == 1:
            # Only apply glitch in one channel
            slit.append_EXTEND("// Simulate detector glitch with timing")
            slit.append_EXTEND("if (y > 0.14*0.08 && y < 0.24*0.08 && rand01() > 0.23)")
            slit.append_EXTEND("t += 0.00034;")

        slit.set_WHEN(WHEN_expression)
        analyzer.set_WHEN(WHEN_expression)

        # Create detector casing with gas volume inside
        casing = instrument.add_component(f"Al_container_{index}", "Union_cylinder")
        casing.set_parameters(
            yheight=0.1,
            radius=0.03,
            p_interact=0.25,
            material_string='"Al"',
            priority=300 + 2 * index,
        )
        casing.set_AT([0, 0, analyzer_detector_dist], return_dir)

        He3_gas = instrument.add_component(f"He3_gas_{index}", "Union_cylinder")
        He3_gas.set_AT_RELATIVE(casing)
        He3_gas.set_parameters(
            yheight=casing.yheight - 0.02,
            radius=casing.radius - 4e-3,
            material_string='"He3"',
            priority=301 + 2 * index,
            p_interact=0.2,
        )

        if index in plot_indices:
            detector = instrument.add_component(
                f"signal_space_{index}", "Union_abs_logger_1D_space", RELATIVE=He3_gas
            )
            detector.target_geometry = f'"He3_gas_{index}"'
            detector.yheight = He3_gas.yheight
            detector.n = 50
            detector.filename = f'"detector_signal_space_{index}.dat"'

            detector = instrument.add_component(
                f"signal_time_{index}", "Union_abs_logger_1D_time", RELATIVE=He3_gas
            )
            detector.target_geometry = f'"He3_gas_{index}"'
            detector.time_min = "t_min"
            detector.time_max = "t_max"
            detector.n = 100
            detector.filename = f'"detector_signal_time_{index}.dat"'

            detector = instrument.add_component(
                f"signal_tof_{index}", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
            )
            detector.target_geometry = f'"He3_gas_{index}"'
            detector.yheight = He3_gas.yheight
            detector.n = 50
            detector.time_min = "t_min"
            detector.time_max = "t_max"
            detector.time_bins = 250
            detector.filename = f'"detector_signal_2D_{index}.dat"'

            """
            # Skipped as the multiple pulses exercise is not done
            detector = instrument.add_component(
                f"signal_tof_all_{index}", "Union_abs_logger_1D_space_tof", RELATIVE=He3_gas
            )
            detector.target_geometry = f'"He3_gas_{index}"'
            detector.yheight = He3_gas.yheight
            detector.n = 50
            detector.time_min = "t_min"
            detector.time_max = "t_max_pulses"
            detector.time_bins = 350
            detector.filename = f'"detector_signal_2D_all_{index}.dat"'
            """

        detector_event = instrument.add_component(
            f"signal_tof_event_{index}",
            "Union_abs_logger_1D_space_event",
            RELATIVE=He3_gas,
        )
        detector_event.target_geometry = f'"He3_gas_{index}"'
        detector_event.yheight = He3_gas.yheight
        detector_event.n = 200
        detector_event.filename = f'"detector_signal_event_{index}.dat"'

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
