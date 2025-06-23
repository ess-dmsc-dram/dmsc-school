import numpy as np
import mcstasscript as ms

source_to_psc = 6.5
guide_to_sample = 0.6


def add_guide(instrument, source):
    """
    Adds simple guide to instrument

    :param instrument: McStasScript instrument object
    :param source: McStasScript component object for the source used before the guide
    :return: McStasScript instrument object
    """
    source_to_feeder = 2.0

    feeder = instrument.add_component("feeder", "Elliptic_guide_gravity")
    feeder.set_parameters(
        xwidth=0.08,
        yheight=0.06,
        dimensionsAt='"entrance"',
        l=4.3,
        m=3,
        alpha=3.2,
        linxw=4.5,
        linyh=2.05,
        loutxw=0.4,
        loutyh=0.3,
    )
    feeder.set_AT(source_to_feeder, RELATIVE=source)

    # Update the source focus parameters to match the first guide element
    source.set_parameters(
        dist=source_to_feeder, focus_xw=feeder.xwidth, focus_yh=1.2 * feeder.yheight
    )  # larger focus_yh due to gravity

    # Position of pulse shaping chopper, placed in the choppers.py file
    PSC_position = instrument.add_component("PSC_position", "Arm")
    PSC_position.set_AT(source_to_psc, RELATIVE=source)

    # Define cross section of curved section
    curved_section_width = 0.08
    curved_section_height = 0.12

    # half ellipse
    expanding = instrument.add_component("expanding", "Elliptic_guide_gravity")
    expanding.set_parameters(
        xwidth=curved_section_width,
        yheight=curved_section_height,
        dimensionsAt='"exit"',
        l=10,
        m=3,
        alpha=3.2,
        linxw=1.2,
        linyh=0.4,
    )
    expanding.set_parameters(
        loutxw=expanding.l + expanding.linxw, loutyh=expanding.l + expanding.linyh
    )
    expanding.set_AT(0.05, RELATIVE=PSC_position)

    # Curved section
    curved_length = 160 - 6.55 - 10 - 10  # full length - chopper
    total_rotation = 1  # total rotation in [deg]
    n_segments = 12
    segment_length = curved_length / n_segments
    segment_rotation = total_rotation / n_segments
    instrument.add_parameter("guide_curve_deg", value=1.0)

    previous_component = expanding
    previous_length = expanding.l
    for index in range(n_segments):
        guide = instrument.add_component("guide_" + str(index), "Guide_gravity")
        guide.set_parameters(
            w1=curved_section_width,
            h1=curved_section_height,
            l=segment_length,
            m=1.5,
            alpha=3.0,
        )
        guide.set_AT(
            previous_length + 3e-3, RELATIVE=previous_component
        )  # Leave 3 mm length between segments
        guide.set_ROTATED(
            [0, f"guide_curve_deg/{n_segments:.1f}", 0], RELATIVE=previous_component
        )

        # In order to place the next guide element relative to this one, we save it as previous
        previous_component = guide
        previous_length = guide.l

    # half ellipse
    focusing = instrument.add_component("focusing", "Elliptic_guide_gravity")
    focusing.set_parameters(
        xwidth=curved_section_width,
        yheight=curved_section_height,
        dimensionsAt='"entrance"',
        l=10,
        m=3,
        alpha=3.2,
        loutxw=guide_to_sample + 0.05,
        loutyh=guide_to_sample + 0.05,
    )
    focusing.set_parameters(
        linxw=focusing.l + focusing.loutxw, linyh=focusing.l + focusing.loutyh
    )
    focusing.set_AT(previous_length + 3e-3, RELATIVE=previous_component)

    # guide end is used by backend to place sample position
    guide_end = instrument.add_component("guide_end", "Arm")
    guide_end.set_AT(focusing.l, RELATIVE=focusing)


def add_choppers(instrument):
    instrument.add_parameter(
        "chopper_wavelength_center", value=2.5, comment="Center of wavelength band [AA]"
    )
    instrument.add_declare_var("double", "chopper_position", value=source_to_psc)
    instrument.add_declare_var("double", "speed")
    delay_var = instrument.add_declare_var("double", "delay")

    # Calculate appropriate chopper delay in McStas initialize using C code
    instrument.append_initialize("""
    speed = 2.0*PI/chopper_wavelength_center*K2V;
    delay = chopper_position/speed;
    delay += 0.5*2.86E-3;
    """)

    # Parameter setting chopper speed
    instrument.add_parameter(
        "double",
        "frequency_multiplier",
        value=1,
        comment="[1] Chopper frequency as multiple of source frequency",
    )

    chopper = instrument.add_component(
        "chopper",
        "DiskChopper",
        after="PSC_position",  # Place after PSC_position arm in component sequence
        RELATIVE="PSC_position",
    )  # Place at PSC_position in space
    chopper.theta_0 = 7.0
    chopper.nslit = 1
    chopper.radius = 0.35
    chopper.yheight = 0.05
    chopper.nu = (
        "frequency_multiplier*14.0"  # Calculation performed in McStas instrument file
    )
    chopper.delay = delay_var  # Declare variable object


def add_backend_classic(instrument, include_event_monitors=True):
    # Classic detectors

    rotated_sample_position = instrument.add_component("rotated_sample_position", "Arm", RELATIVE="sample_position")

    pixel_min = 0

    theta_bins = 320
    ybins = 20
    monitor = instrument.add_component("Banana_large", "Monitor_nD")
    monitor.set_parameters(
        radius=3.5,
        yheight="detector_height",
        filename='"direct_event_banana_signal_large.dat"',
        restore_neutron=1,
        user1='"source_time"',
        # user2='"n_scattering_sample"'
    )
    # monitor.options = f'"banana theta bins={theta_bins} limits=[10, 170] y bins={ybins}, neutron pixel min={pixel_min}, t, v, l, user1, user2, list all neutrons"'
    monitor.options = f'"banana theta bins={theta_bins} limits=[10, 170] y bins={ybins}, neutron pixel min={pixel_min}, t, v, l, user1, list all neutrons"'
    monitor.set_AT(0.0, RELATIVE="rotated_sample_position")
    # monitor.set_GROUP("detectors")

    # increment pixel id using the given detector resolution
    pixel_min += theta_bins * ybins + 10

    theta_bins = 60
    ybins = 20
    monitor = instrument.add_component("Banana_small", "Monitor_nD")
    monitor.set_parameters(
        radius=3.5,
        yheight="detector_height",
        filename='"direct_event_banana_signal_small.dat"',
        restore_neutron=1,
        user1='"source_time"',
        # user2='"n_scattering_sample"'
    )
    # monitor.options = f'"banana theta bins={theta_bins} limits=[-40, -10] y bins={ybins}, neutron pixel min={pixel_min}, t, v, l, user1, user2, list all neutrons"'
    monitor.options = f'"banana theta bins={theta_bins} limits=[-170, -140] y bins={ybins}, neutron pixel min={pixel_min}, t, v, l, user1, list all neutrons"'
    monitor.set_AT(0.0, RELATIVE="rotated_sample_position")
    # monitor.set_GROUP("detectors")

    """
    monitor = instrument.add_component("metadata_monitor", "Monitor_nD")
    monitor.set_parameters(filename='"metadata.dat"',
                           restore_neutron=1, user1='"source_time"', user2='"n_scattering_sample"')
    monitor.options = f'"Previous, t, v, l, user1, user2, list all neutrons"'
    monitor.set_AT(0.0, RELATIVE="sample_position")
    """


def add_backend_union(instrument, include_event_monitors=True):
    from mcstasscript.tools.ncrystal_union import add_ncrystal_union_material

    instrument.add_component("init", "Union_init")

    # Air around the sample
    add_ncrystal_union_material(
        instrument, "Air", "gasmix::air/25C/1.0atm/0.30relhumidity"
    )
    add_ncrystal_union_material(instrument, "He3", "gasmix::He/5bar/25C/He_is_He3")

    # Aluminium
    Al_incoherent = instrument.add_component("Al_incoherent", "Incoherent_process")
    Al_incoherent.set_parameters(sigma=4 * 0.0082, unit_cell_volume=66.4)

    Al_powder = instrument.add_component("Al_powder", "Powder_process")
    Al_powder.reflections = '"Al.laz"'

    Al = instrument.add_component("Al", "Union_make_material")
    Al.process_string = '"Al_incoherent,Al_powder"'
    Al.my_absorption = 100 * 4 * 0.231 / 66.4

    instrument.add_component("start_union_geometries", "Arm")

    tube_angles = np.linspace(10, 170, 16 * 3)
    # tube_angles.extend(np.linspace(-10, -40, 3*3))

    pixel_min = 0
    for index, angle in enumerate(tube_angles):
        direction = instrument.add_component("direction_" + str(index), "Arm")
        direction.set_RELATIVE("sample_position")
        direction.set_ROTATED([0, angle, 0], RELATIVE="sample_position")

        casing = instrument.add_component("case_" + str(index), "Union_cylinder")
        casing.set_parameters(
            radius=0.05,
            yheight="detector_height",
            material_string='"Al"',
            priority=10 + index,
        )
        casing.set_AT(3.5, RELATIVE=direction)

        gas_name = "gas_" + str(index)
        gas = instrument.add_component(gas_name, "Union_cylinder", RELATIVE=casing)
        gas.set_parameters(
            radius=casing.radius - 2e-3,
            yheight="detector_height - 0.01",
            material_string='"He3"',
            priority=casing.priority + 0.1,
            p_interact=0.5,
        )

        options = f'"previous x bins=1 limits=[-0.03, 0.03] y bins={20}, neutron pixel min={pixel_min} t, l, list all neutron"'
        abs_logger = instrument.add_component(
            "abs_logger_" + str(index), "Union_abs_logger_nD"
        )
        abs_logger.set_RELATIVE(gas)
        abs_logger.set_parameters(
            radius=gas.radius,
            yheight=gas.yheight,
            target_geometry=f'"{gas_name}"',
            options=options,
            filename=f'"data_{index}.dat"',
        )

        pixel_min += 1 * 20

    logger_zx = instrument.add_component(
        "full_logger_space_zx", "Union_logger_2D_space", RELATIVE="sample_position"
    )
    logger_zx.set_parameters(
        D_direction_1='"z"',
        D1_min=-4,
        D1_max=4,
        n1=400,
        D_direction_2='"x"',
        D2_min=-4,
        D2_max=4,
        n2=400,
        filename='"full_logger_zx.dat"',
    )

    logger_xy = instrument.add_component(
        "full_logger_space_xy", "Union_logger_2D_space", RELATIVE="sample_position"
    )
    logger_xy.set_parameters(
        D_direction_1='"x"',
        D1_min=-4,
        D1_max=4,
        n1=400,
        D_direction_2='"y"',
        D2_min=-2,
        D2_max=2,
        n2=400,
        filename='"full_logger_xy.dat"',
    )

    instrument.add_component("master", "Union_master")

    instrument.add_component("stop", "Union_stop")


def add_backend(instrument, detectors="classic", include_event_monitors=True):
    # inserting basic monitors before sample position to ensure they are placed before any sample inserted later
    guide_end = instrument.get_component("guide_end")

    psd_sample = instrument.add_component("PSD_sample", "PSD_monitor")
    psd_sample.set_AT(guide_to_sample, RELATIVE=guide_end)
    psd_sample.set_parameters(
        nx=100,
        ny=100,
        xwidth=0.03,
        yheight=0.03,
        filename='"sample_PSD.dat"',
        restore_neutron=1,
    )

    wavelength = instrument.add_component("wavelength", "L_monitor")
    wavelength.set_AT(guide_to_sample, RELATIVE=guide_end)
    wavelength.set_parameters(
        nL=100,
        Lmin="l_min",
        Lmax="l_max",  # Using parameters defined in make
        xwidth=0.03,
        yheight=0.03,
        filename='"wavelength.dat"',
        restore_neutron=1,
    )

    # Sample position, an actual sample can be inserted "after" this
    sample_position = instrument.add_component("sample_position", "Arm")
    sample_position.set_AT(guide_to_sample, RELATIVE="guide_end")

    fixed_source = instrument.add_component("fixed_source", "Arm")
    fixed_source.set_AT(-160.6, RELATIVE=sample_position)

    instrument.add_parameter("detector_height", value=2.5)

    if detectors == "classic":
        instrument.add_component("init", "Union_init")
        instrument.add_component("start_union_geometries", "Arm")
        instrument.add_component("master", "Union_master")
        instrument.add_component("stop", "Union_stop")

        add_backend_classic(instrument, include_event_monitors=include_event_monitors)
    elif detectors == "union":
        add_backend_union(instrument, include_event_monitors=include_event_monitors)
    else:
        raise ValueError("Unknown value for detector")


def make(
    union_detectors=False, include_choppers=True, include_event_monitors=True, **kwargs
):
    instrument = ms.McStas_instr("powder", **kwargs)

    # project_path = os.path.dirname(os.path.abspath(__file__))
    # instrument.add_search(os.path.join(project_path, "required_mcstas_components"), help_name="Project path")

    # Source and its parameters
    l_min = instrument.add_parameter(
        "l_min", value=0.5, comment="Minimum simulated wavelength [AA]"
    )
    l_max = instrument.add_parameter(
        "l_max", value=4.0, comment="Maximum simulated wavelength [AA]"
    )
    n_pulses = instrument.add_parameter(
        "int", "n_pulses", value=1, comment="Number of simulated pulses"
    )

    Source = instrument.add_component("Source", "ESS_butterfly")
    Source.set_parameters(
        sector='"W"',
        beamline=2,
        yheight=0.03,
        cold_frac=0.5,
        c_performance=1,
        t_performance=1,
        Lmin=l_min,
        Lmax=l_max,
        n_pulses=n_pulses,
        acc_power=2,
    )

    # Have particles remember their time leaving the source
    instrument.add_user_var("double", "source_time")
    Source.append_EXTEND("source_time = t;")

    # Source.append_EXTEND("t = t/100 + 0.5*2.86E-3;") # Makes it a short pulse source for testing

    # Add the guide system, source component used to set proper focusing
    add_guide(instrument, source=Source)

    # Add the choppers to their positions defined by the add_guide function
    if include_choppers:
        add_choppers(instrument)

    if union_detectors:
        detectors = "union"
    else:
        detectors = "classic"

    add_backend(
        instrument, detectors=detectors, include_event_monitors=include_event_monitors
    )

    # ================ Si sample ================
    Si_inc = instrument.add_component(
        "Si_inc", "Incoherent_process", before="start_union_geometries"
    )
    Si_inc.sigma = 8*0.004
    Si_inc.unit_cell_volume = 160.15

    Si_pow = instrument.add_component(
        "Si_pow", "Powder_process", before="start_union_geometries"
    )
    Si_pow.reflections = '"Si.laz"'

    Si = instrument.add_component(
        "Si", "Union_make_material", before="start_union_geometries"
    )
    Si.process_string = '"Si_inc,Si_pow"'
    Si.my_absorption = 100 * 8*0.171 / 160.15


    Si_fraction = 0.2

    # ================ Mixture sample ================
    Sample_inc_vernite = instrument.add_component(
        "Sample_inc_vernite", "Incoherent_process", before="start_union_geometries"
    )
    Sample_inc_vernite.sigma = 4*3.4176
    Sample_inc_vernite.unit_cell_volume = 1079.1
    Sample_inc_vernite.packing_factor = 1 - Si_fraction

    Sample_inc_Si = instrument.add_component(
        "Sample_inc_Si", "Incoherent_process", before="start_union_geometries"
    )
    Sample_inc_Si.sigma = 8*0.004
    Sample_inc_Si.unit_cell_volume = 160.15
    Sample_inc_Si.packing_factor = Si_fraction

    Sample_pow_vernite = instrument.add_component(
        "Sample_pow_vernite", "Powder_process", before="start_union_geometries"
    )
    Sample_pow_vernite.reflections = '"Na2Ca3Al2F14.laz"'
    Sample_pow_vernite.packing_factor = 1 - Si_fraction

    Sample_pow_Si = instrument.add_component(
        "Sample_pow_Si", "Powder_process", before="start_union_geometries"
    )
    Sample_pow_Si.reflections = '"Si.laz"'
    Sample_pow_Si.packing_factor = Si_fraction

    Sample = instrument.add_component(
        "Sample", "Union_make_material", before="start_union_geometries"
    )
    Sample.process_string = '"Sample_inc_Si,Sample_inc_vernite,Sample_pow_vernite,Sample_pow_Si"'
    Sample.my_absorption = (100 * 4 * 2.9464 / 1079.1) * (1-Si_fraction) + Si_fraction* (100 * 8 * 0.171 / 160.15)


    # ================ Vanadium sample ================
    Vanadium_inc = instrument.add_component(
        "Vanadium_inc", "Incoherent_process", before="start_union_geometries"
    )
    mult = 2
    Vanadium_inc.sigma = mult * 4.94
    Vanadium_inc.unit_cell_volume = 27.66

    Vanadium = instrument.add_component(
        "Vanadium", "Union_make_material", before="start_union_geometries"
    )
    Vanadium.process_string = '"Vanadium_inc"'
    Vanadium.my_absorption = 100 * mult * 5.08 / Vanadium_inc.unit_cell_volume

    # ================ Fe sample ================
    Fe_inc = instrument.add_component(
        "Fe_inc", "Incoherent_process", before="start_union_geometries"
    )
    mult = 2
    Fe_inc.sigma = mult*0.4
    Fe_inc.unit_cell_volume = 24.04

    Fe_pow = instrument.add_component(
        "Fe_pow", "Powder_process", before="start_union_geometries"
    )
    Fe_pow.reflections = '"Fe.laz"'

    Fe = instrument.add_component(
        "Fe", "Union_make_material", before="start_union_geometries"
    )
    Fe.process_string = '"Fe_inc,Fe_pow"'
    Fe.my_absorption = 100 * mult*2.56 / Fe_inc.unit_cell_volume


    # ========================================================
    radius = instrument.add_parameter("sample_radius", value=0.01)
    height = instrument.add_parameter("sample_height", value=0.05)

    instrument.add_parameter("string", "sample_choice", value='"sample_Si"', options=['"sample_Si"', '"sample_2"', '"sample_vanadium"', '"sample_fe"'])

    instrument.add_declare_var("int", "sample_Si_active")
    instrument.add_declare_var("int", "sample_2_active")
    instrument.add_declare_var("int", "sample_vanadium_active")
    instrument.add_declare_var("int", "sample_fe_active")
    instrument.append_initialize('''
    if (strcmp(sample_choice, "sample_Si") == 0) {
       sample_Si_active = 1;
       sample_2_active = 0;
       sample_vanadium_active = 0;
       sample_fe_active = 0;
    }
    else if (strcmp(sample_choice, "sample_2") == 0) {
       sample_Si_active = 0;
       sample_2_active = 1;
       sample_vanadium_active = 0;
       sample_fe_active = 0;
    }
    else if (strcmp(sample_choice, "sample_vanadium") == 0) {
       sample_Si_active = 0;
       sample_2_active = 0;
       sample_vanadium_active = 1;
       sample_fe_active = 0;
    }
    else if (strcmp(sample_choice, "sample_fe") == 0) {
       sample_Si_active = 0;
       sample_2_active = 0;
       sample_vanadium_active = 0;
       sample_fe_active = 1;
    }
    ''')

    sample = instrument.add_component(
        "sample_Si",
        "Union_cylinder",
        after="start_union_geometries",
        RELATIVE="sample_position",
    )
    sample.set_parameters(
        radius=radius, yheight=height, material_string='"Si"', priority=5,
        number_of_activations = "sample_Si_active"
    )

    sample = instrument.add_component(
        "sample_2",
        "Union_cylinder",
        after="start_union_geometries",
        RELATIVE="sample_position",
    )
    sample.set_parameters(
        radius=radius, yheight=height, material_string='"Sample"', priority=6,
        number_of_activations = "sample_2_active"
    )

    sample = instrument.add_component(
        "sample_vanadium",
        "Union_cylinder",
        after="start_union_geometries",
        RELATIVE="sample_position",
    )
    sample.set_parameters(
        radius=radius, yheight=height, material_string='"Vanadium"', priority=7,
        number_of_activations = "sample_vanadium_active"
    )

    sample = instrument.add_component(
        "sample_fe",
        "Union_cylinder",
        after="start_union_geometries",
        RELATIVE="sample_position",
    )
    sample.set_parameters(
        radius=radius, yheight=height, material_string='"Fe"', priority=8,
        number_of_activations = "sample_fe_active"
    )


    # remember number of scattering events
    instrument.add_user_var("double", "n_scattering_sample")
    # Always keep the sample as the first geometry (0 is the surrounding vacuum)
    instrument.get_component("master").append_EXTEND(
        "n_scattering_sample = scattered_flag[1];"
    )

    return instrument
