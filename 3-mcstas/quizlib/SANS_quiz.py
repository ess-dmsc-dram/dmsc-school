import mcstasscript as ms

from itertools import permutations

from .quiz import Quiz, make_red, make_green, make_orange, print_box
from .helpers import name_of_component_type, is_instrument_object


class SANS_Quiz(Quiz):
    def __init__(self):
        super().__init__()

    def question_1(self, answer=None):
        """
        Before running the instrument we need to set some parameters.
        The most important one is the *detector_distance* parameter describing the distance
        between the sample and the detector. Given the need for high angular precision in
        determining the scattering angle of the neutron, which of these would be best?

        - A: 1 m
        - B: 2 m
        - C: 3 m
        """

        feedback = {
            "A": "No, this would give the widest angle coverage, but worst resolution",
            "B": "No, it's possible to get better angular precision with another setting",
            "C": "Yes, a large distance between sample and detector provides high angular precision",
        }

        self.multiple_choice(answer=answer, correct_answer="C", feedback=feedback)

    def question_2(self, answer=None):
        """
        Set the parameters of the instrument using the *set_parameters* method.
        - sample_distance: 150 m
        - wavelength: 6 Å
        - wavelength band: 1.5 Å
        - enable_sample: 0
        - n_pulses: 1
        """

        # check instrument object parameters

        required_parameters = dict(
            sample_distance=150,
            wavelength=6,
            d_wavelength=1.5,
            enable_sample=0,
            n_pulses=1,
            detector_distance=3.0,
        )

        if not is_instrument_object(answer):
            return

        parameters = answer.parameters.parameters

        for key, value in required_parameters.items():
            if key not in parameters:
                print_box(
                    f"The parameter {key} was not found in the instrument.", False
                )
                return

            if not value == parameters[key].value:
                print_box(
                    f"The parameter {key} had value {parameters[key].value}, which was not as expected.",
                    False,
                )
                return

        print_box("The parameters of the instrument were correctly set!", True)

    def question_3(self, answer=None):
        """
        The detector is a He3 tube centered 25 cm above the beam height and with a metal casing.

        What does the signal look like without sample?
        - A: The majority of the signal close to the direct beam
        - B: Flat signal over detector height
        - C: The majority of the signal is far away from the direct beam
        """

        feedback = {
            "A": "Yes, since the detector is above the beam, -0.25 m would be beam height, "
            "and the majority of the counts are seen at the lowest y values",
            "B": "No, sadly the signal is not as flat as one could have hoped",
            "C": "No, since the detector is above the beam, that would require the majority of "
            "the counts to be at large y values",
        }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)

    def question_4(self, answer=None):
        """
        Is this a problem for a SANS instrument?
        - A: Yes
        - B: No
        """
        feedback = {
            "A": "Exactly, since this region correspond to the lowest measured angles, "
            "crucial for small angle scattering",
            "B": "The quiz disagrees, a large signal at low height and thus low angle masks"
            "data important for small angle scattering",
        }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)

    def question_5(self, answer=None):
        """
        How can it be improved?
        - A: By adding a Velocity selector
        - B: By adding a Chopper
        - C: By adding a Beamstop
        - D: By adding a Slit
        """

        feedback = {
            "A": "No, that would improve the energy resolution",
            "B": "No, that would improve the energy resolution",
            "C": "Yes, the issue arise from the direct beam scattering in the casing, a beamstop can prevent this",
            "D": "From a McStas point of view this could work, but there is an easier solution",
        }

        self.multiple_choice(answer=answer, correct_answer="C", feedback=feedback)

    def question_6(self, answer=None):
        """
        Use either the *show_diagram* or *show_components* method on the instrument object
        to get an overview of the component sequence in the instrument.
        Where would you place the new component?

        - A: After the source
        - B: Before the sample
        - C: After the sample
        - D: Before the detector position
        """

        feedback = {
            "A": "No, that would prevent the beam from reaching the sample",
            "B": "No, that would prevent the beam from reaching the sample",
            "C": "Yes, that would remove the part of the beam that did not scatter in the sample",
            "D": "Yes, that would remove the part of the beam that did not scatter in the sample",
        }

        if not isinstance(answer, list):
            answer = [answer]

        for single_answer in answer:
            self.multiple_choice(
                answer=single_answer, correct_answer=["C", "D"], feedback=feedback
            )

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
        if "Beamstop" not in comp_types:
            print_box(
                "Did not find any beamstop added to this instrument object", False
            )
            return

        if not comp_types.count("Beamstop") == 1:
            print_box(
                "Found several beamstops added to this instrument, only one is necessary!"
                "You may need to rerun the notebook from the top to get a fresh start.",
                False,
            )
            return

        beamstop_name = name_of_component_type(answer, "Beamstop")
        comp_names = [x.name for x in answer.component_list]

        beamstop_index = comp_names.index(beamstop_name)
        sample_index = comp_names.index("sample")
        detector_position_index = comp_names.index("detector_position")

        if beamstop_index < sample_index:
            print_box(
                "The beamstop was inserted before the sample, this won't work!", False
            )
            return

        if beamstop_index > detector_position_index:
            print_box(
                "The beamstop was inserted after the detector position, this is not quite right",
                False,
            )
            return

        msg = "The beamstop was added at the right point in the component sequence and with right parameters!"
        required_pars = dict(xwidth=0.1, yheight=0.02)
        self.last_component_in_instr_check(
            answer=answer,
            comp_type_str="Beamstop",
            required_pars=required_pars,
            required_AT_relative=None,
            required_AT_data=None,
            required_ROTATED_relative=None,
            required_ROTATED_data=None,
            success_msg=msg,
            comp_name=beamstop_name,
            print_output=True,
        )

    def question_8(self, answer=None):
        if not is_instrument_object(answer):
            return

        comp_types = [x.component_name for x in answer.component_list]
        if not "Beamstop" in comp_types:
            print_box(
                "Did not find any beamstop added to this instrument object", False
            )
            return

        if not comp_types.count("Beamstop") == 1:
            print_box(
                "Found several beamstops added to this instrument, only one is necessary!"
                "You may need to rerun the notebook from the top to get a fresh start.",
                False,
            )
            return

        beamstop_name = name_of_component_type(answer, "Beamstop")
        comp_names = [x.name for x in answer.component_list]

        beamstop_index = comp_names.index(beamstop_name)
        sample_index = comp_names.index("sample")
        detector_position_index = comp_names.index("detector_position")

        if beamstop_index < sample_index:
            print_box(
                "The beamstop was inserted before the sample, this won't work!", False
            )
            return

        if beamstop_index > detector_position_index:
            print_box(
                "The beamstop was inserted after the detector position, this is not quite right",
                False,
            )
            return

        beamstop_component = answer.get_component(beamstop_name)
        if beamstop_component.AT_data[2] == 2.7:
            print_box("The distance to the beamstop was set directly as a number, use the variable name instead. It is the right value though!", False)
            return

        alternate_answers = [[0, 0, "0.9*detector_distance"],
                             [0, 0, "0.90*detector_distance"],
                             [0, 0, "detector_distance*0.9"],
                             [0, 0, "detector_distance*0.90"],
                             [0, 0, "9*detector_distance/10"],
                             [0, 0, "detector_distance/10*9"],
                             [0, 0, "detector_distance/10*9.0"],
                             [0, 0, "detector_distance/10.0*9"],
                             [0, 0, "detector_distance/10.0*9.0"],
                             [0, 0, "90/100*detector_distance"],
                             [0, 0, "90.0/100.0*detector_distance"],
                             [0, 0, "90/100.0*detector_distance"],
                             [0, 0, "90.0/100*detector_distance"],
                            ]
        if beamstop_component.AT_data in alternate_answers:
            check_AT_answer = beamstop_component.AT_data
        else:
            check_AT_answer = [0, 0, "0.9*detector_distance"]

        msg = "The beamstop was added at the right point in the component sequence and space!"
        required_pars = dict(xwidth=0.1, yheight=0.02)
        self.last_component_in_instr_check(
            answer=answer,
            comp_type_str="Beamstop",
            required_AT_relative="sample_position",
            required_AT_data=check_AT_answer,
            success_msg=msg,
            comp_name=beamstop_name,
            print_output=True,
        )

    def question_9(self, answer=None):
        """
        Do you see an improvement compared to earlier results?
        - A: Yes
        - B: No
        """
        feedback = {
            "A": "The large signal at low y has disappeared!",
            "B": "There are still issues, but the most significant one should have been fixed",
        }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)

    def question_10(self, answer=None):
        """
        Compare the results with and without sample. Where on the detector are the difference largest?
        - A: Lowest part of the detector
        - B: Middle of the detector
        - C: Top of the detector
        """
        feedback = {
            "A": "Yes, there should be around 500 times larger count rate at the lowest part of the detector",
            "B": "No, there is some interesting structure, but the count rate is not much greater than background",
            "C": "No, at large angles the signal is almost equal to the background.",
        }

        self.multiple_choice(answer=answer, correct_answer="A", feedback=feedback)
