import mcstasscript as ms

from itertools import permutations

from .quiz import Quiz, make_red, make_green, make_orange, print_box
from .helpers import name_of_component_type, is_instrument_object

class QENS_Quiz(Quiz):
    def __init__(self):
        super().__init__()

    def question_1(self, answer=None):
        """
        Before running the instrument we need to set some parameters.
        The most important one is the *sample_distance* parameter describing
        the distance between the source and the sample. Given the need for
        high precision in determining the energy of the neutron, which of
        the following instrument lengths should be chosen?

        - A: 30 m
        - B: 60 m
        - C: 150 m
        """

        feedback = {"A": "No, a short instrument would provide greater bandwidth but "
                         "lower precision when determining the neutron energy",
                    "B": "No, there is a better option among the available choices",
                    "C": "Yes, a long instrument inherently provides a greater accuracy "
                         "when determining the neutron flight time and thus energy.",
                    }

        self.multiple_choice(answer=answer, correct_answer="C", feedback=feedback)

    def question_2(self, answer=None):
        """
        Set the *sample_distance* corresponding to the answer above and set the simulated energy width to 3 $\\mu$eV.
        """
        # check instrument object parameters

        required_parameters = dict(sample_distance=150, energy_width_ueV=5,
                                   sample_choice='"Elastic"', n_pulses=1,
                                   analyzer_distance=3.0)

        if not is_instrument_object(answer):
            return

        parameters = answer.parameters.parameters

        for key, value in required_parameters.items():
            if key not in parameters:
                print_box(f"The parameter {key} was not found in the instrument.", False)
                return

            if not value == parameters[key].value:
                print_box(f"The parameter {key} had value {parameters[key].value}, which was not as expected.", False)
                return

        print_box("The parameters of the instrument were correctly set!", True)

    def question_3(self, answer=None):
        """
        Look at the time distribution of the signal, which statement about this data is true?
        - A: The data looks like a typical inelastic signal
        - B: The data looks like the ESS pulse structure
        - C: The data looks like a typical elastic signal
        - D: The data looks like the analyzer selected to too broad an energy range
        """

        feedback = {"A": "No, there is something off about this signal ",
                    "B": "Yes, the time distribution is dominated by the ESS pulse structure",
                    "C": "No, that would be very narrow in time distribution",
                    "D": "No, look at the asymmetric start and end of the signal"
                    }

        self.multiple_choice(answer=answer, correct_answer="B", feedback=feedback)

    def question_4(self, answer=None):
        """
        Is this a problem for a backscattering instrument?
        - A: Yes, the low time resolution means low energy resolution
        - B: No, the low time resolution is not necessary for high energy resolution
        """

        feedback = {"A": "Exactly, the time of flight is used to calculate the initial neutron energy ",
                    "B": "The time of flight is used to calculate the initial neutron energy, "
                         "thus a bad time resolution results in a bad energy resolution which is "
                         "a big problem for a Quasi Elastic Neutron Scattering instrument",
                    }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)

    def question_5(self, answer=None):
        """
        How can the instrument be improved?
        - A: Add a chopper to control the time aspect
        - B: Add a slit before sample to reduce the illuminated area
        - C: Add a slit before analyzer to ensure same angle
        - D: Add a spin polarizer to select spin state
        """

        feedback = {"A": "Yes, that would limit the uncertainty on the time of flight",
                    "B": "No, that would not help in a meaningful way, the sample "
                         "is short compared to the flightpath",
                    "C": "No, the simulated analyzer is rather small, no need for a slit "
                         "to reduce the size further. QENS instruments often use much larger analyzers",
                    "D": "No, that wouldn't help the poor time resolution"
                    }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)

    def question_6(self, answer=None):
        """
        Use either the *show_diagram* or *show_components* method on the
        instrument object to get an overview of the component sequence in
        the instrument. Where would you place the new component?

        - A: After the source
        - B: Before the sample position
        - C: After the sample position
        - D: After the analyzer
        """

        feedback = {"A": "Yes, as we want to reduce the uncertainty in when the neutron was at the source, "
                         "placing the chopper as close to the source as possible is optimal.",
                    "B": "Technically yes, but only because we are not simulating a guide between source and sample.",
                    "C": "No, the chopper is needed to improve measured time of flight between source and sample, "
                         "a chopper after the sample would not help",
                    "D": "No, the chopper is needed to improve measured time of flight between source and sample, "
                         "a chopper after the analyzer would not help"
                    }

        if not isinstance(answer, list):
            answer = [answer]

        for single_answer in answer:
            self.multiple_choice(answer=single_answer, correct_answer=["A", "B"], feedback=feedback)

    def question_7(self, answer=None):
        """
        Use the *add_component* method on the instrument to add a chopper.
        Place it in the component sequence by using either the *before* or *after* keyword argument.

        Set the parameters:
         - yheight: 0.05 m
         - radius: 0.7 m
         - nslit: 1.0
         - nu, delay and theta_0: To the variables calculated in the instrument (use quotation marks)
        """

        if not is_instrument_object(answer):
            return

        comp_types = [x.component_name for x in answer.component_list]
        if "DiskChopper" not in comp_types:
            print_box("Did not find any DiskChopper added to this instrument object", False)
            return

        if not comp_types.count("DiskChopper") == 1:
            print_box("Found several DiskChopper's added to this instrument, only one is necessary!"
                      "You may need to rerun the notebook from the top to get a fresh start.", False)
            return

        chopper_name = name_of_component_type(answer, "DiskChopper")
        comp_names = [x.name for x in answer.component_list]

        chopper_index = comp_names.index(chopper_name)
        source_index = comp_names.index("source")
        sample_index = comp_names.index("sample_position")

        if chopper_index < source_index:
            print_box("The DiskChopper was inserted before the source, this won't work!", False)
            return

        if chopper_index > sample_index:
            print_box("The DiskChopper was inserted after the sample position, this is not quite right", False)
            return

        msg = "The DiskChopper was added at the right point in the component sequence and with correct parameters!"
        required_pars = dict(yheight=0.05, radius=0.7, nu="chopper_frequency",
                             nslit=1.0, delay="chopper_delay", theta_0="chopper_theta")
        self.last_component_in_instr_check(answer=answer, comp_type_str="DiskChopper",
                                           required_pars=required_pars,
                                           required_AT_relative=None,
                                           required_AT_data=None,
                                           required_ROTATED_relative=None,
                                           required_ROTATED_data=None,
                                           success_msg=msg,
                                           comp_name=chopper_name, print_output=True)

    def question_8(self, answer=None):
        """
        The next physical location of the component need to be specified,
        which is done using the *set_AT* component. This method takes a list
        of 3 numbers, corresponding to the *x*, *y* and *z* coordinates of
        the component. One can also specify in what coordinate system one
        wants to work, which can be that of any preceding component. Use
        the *RELATIVE* keyword to work in the *source* coordinate system.
        The position of the chopper is needed for calculating phase, so it
        is available as a variable in the instrument, use this variable to
        set the position.
        """

        if not is_instrument_object(answer):
            return

        comp_types = [x.component_name for x in answer.component_list]
        if "DiskChopper" not in comp_types:
            print_box("Did not find any DiskChopper added to this instrument object", False)
            return

        if not comp_types.count("DiskChopper") == 1:
            print_box("Found several DiskChopper's added to this instrument, only one is necessary!"
                      "You may need to rerun the notebook from the top to get a fresh start.", False)
            return

        chopper_name = name_of_component_type(answer, "DiskChopper")
        comp_names = [x.name for x in answer.component_list]

        chopper_index = comp_names.index(chopper_name)
        source_index = comp_names.index("source")
        sample_index = comp_names.index("sample_position")

        if chopper_index < source_index:
            print_box("The DiskChopper was inserted before the source, this won't work!", False)
            return

        if chopper_index > sample_index:
            print_box("The DiskChopper was inserted after the sample position, this is not quite right", False)
            return

        chopper_component = answer.get_component(chopper_name)
        if chopper_component.AT_data[2] == 6.5:
            print_box("The distance to the chopper was set directly as a number, use the variable name instead. It is the right value though!", False)
            return

        msg = "The DiskChopper was added at the right point in the space!"
        required_pars = dict(yheight=0.05, radius=0.7, nu="chopper_frequency",
                             nslit=1.0, delay="chopper_delay", theta_0="chopper_theta")
        self.last_component_in_instr_check(answer=answer, comp_type_str="DiskChopper",
                                           required_pars=required_pars,
                                           required_AT_relative="source",
                                           required_AT_data=[0, 0, "chopper_distance"],
                                           required_ROTATED_relative=None,
                                           required_ROTATED_data=None,
                                           success_msg=msg,
                                           comp_name=chopper_name, print_output=True)

    def question_9(self, answer=None):
        """
        - Q: What is the time resolution of the instrument? (at multiplier=10, FWHM)
        - A: 0.246 ms
        """
        success_msg = "Yes!"
        below_msg = "Expected a larger value, are you using the full width at half max convention?" \
                    "It should be possible to zoom and get mouse coordinates on the plot."
        above_msg = "Expected a smaller value. You can ignore the small side peak." \
                    "It should be possible to zoom and get mouse coordinates on the plot."

        self.insert_value(answer, 0.000246,
                          feedback_correct=success_msg,
                          feedback_below=below_msg, feedback_above=above_msg,
                          tolerance_factor=0.2)

    def question_10(self, answer=None):
        """
        - Q: What is the time width when using a known sample with 12 ueV broadening?
        - A: 1.26 ms
        """
        success_msg = "Yes!"
        below_msg = "Expected a larger value, are you using the full width at half max convention?" \
                    "It should be possible to zoom and get mouse coordinates on the plot."
        above_msg = "Expected a smaller value. You can ignore the small side peak." \
                    "It should be possible to zoom and get mouse coordinates on the plot."

        self.insert_value(answer, 0.00126,
                          feedback_correct=success_msg,
                          feedback_below=below_msg, feedback_above=above_msg,
                          tolerance_factor=0.25)

    def question_11(self, answer=None):
        """
        - Q: By taking the ratio between the time width at the known and unknown sample, what would the expected energy width (HWHM) of the unknown sample be?
        - A: 8.24 ueV
        """
        success_msg = "Yes! Lets see how this early estimate holds up with more thorough analysis over the next days."
        below_msg = "Expected a larger value, are you comparing the time width of the known and unknown sample results and normalizing with the known energy width?"
        above_msg = "Expected a smaller value, are you comparing the time width of the known and unknown sample results and normalizing with the known energy width?"

        self.insert_value(answer, 8.238,
                          feedback_correct=success_msg,
                          feedback_below=below_msg, feedback_above=above_msg,
                          tolerance_factor=0.20)
