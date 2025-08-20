from .quiz import Quiz, print_box
from .helpers import name_of_component_type, is_instrument_object


class Powder_Quiz(Quiz):
    def question_1(self, answer=None):
        """
        ### Q1
        Select appropriate sample size given Vanadium has a macroscopic scattering cross section Sigma of around 0.35 cm^-1. A neutron beam with intensity $I_0$ that travel in a media a distance of $z$ will be attenuated as the neutrons scatter in the material, and the remaining intensity $I$ can be calculated with the Beer-Lambert law:
        I = I_0 e^{-z Sigma}


        For our experiment we want to observe neutrons that scattered once, as neutrons that scatter more than once would be considered background.

        What sample depth would be appropriate?

        - A: 10 cm (3% left, 97% scatters)
        - B: 1 cm (70% left, 30% scatters)
        - C: 1 mm (96.5% left, 3.5% scatters)
        """

        feedback = {
            "A": "No, that sample would be too large, while its very likely the "
            "neutron scatters, its also very unlikely it only scatters once",
            "B": "Yes, this is a reasonable mix, here there is a 30% probability "
            "for a neutron to scatter, so about 20% scatters exactly once.",
            "C": "No, such a small sample would provide great data, but the experiment "
            "would take too long as only 3.5% of the neutrons would be scattered.",
        }

        self.multiple_choice(answer=answer, correct_answer="B", feedback=feedback)

    def question_2(self, answer=None):
        """
        ### Set sample size in simulated instrument
        Use the *set_parameters* method to set the sample thickness, here using the parameter *sample_radius*. Set the wavelength range using "l_min" and "l_max" to 2.5 - 2.501.
        """
        # check instrument object parameters

        required_parameters = dict(
            sample_radius=0.005,
            l_min=2.5,
            l_max=2.501,
            sample_choice='"no_sample"',
            n_pulses=1,
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
        - Q: Whats the relative uncertainty on the time observed at the sample position, FWHM?
             Insert value as a percentage
        - A: 2.715 %
        """
        success_msg = "Yes!"
        below_msg = (
            "Expected a larger value, are you using the full width at half max convention? "
            "It should be possible to zoom and get mouse coordinates on the plot."
        )
        above_msg = (
            "Expected a smaller value. You can ignore the small side peak. "
            "It should be possible to zoom and get mouse coordinates on the plot."
        )

        self.insert_value(
            answer,
            2.715,
            feedback_correct=success_msg,
            feedback_below=below_msg,
            feedback_above=above_msg,
            tolerance_factor=0.15,
        )

    def question_4(self, answer=None):
        """
        This will correspond to the wavelength resolution at this wavelength, generally we need less than 1% for powder diffraction, is this sufficient?

        multiple choice
        - A: yes
        - B: no
        """

        feedback = {
            "A": "No, this would result in insufficient wavelength resolution for powder diffraction.",
            "B": "Yes, this would result in insufficient wavelength resolution for powder diffraction.",
        }

        self.multiple_choice(answer=answer, correct_answer="B", feedback=feedback)

    def question_5(self, answer=None):
        """
        How could we improve this?
        - A: monochromator
        - B: chopper
        - C: velocity selector
        - D: shorter guide
        """

        feedback = {
            "A": "No, even though that would work, we would not be utilizing the advantage of our pulsed source ",
            "B": "Yes, that would ensure we knew that all neutrons passed through that point "
            "in the guide at the same time, improving the time uncertainty.",
            "C": "No, while a velocity selector can help, they are better suited for when low time resolution "
            "is necessary, for a powder diffraction instrument we need higher accuracy.",
            "D": "No, would actually degrade the time resolution further as the travel time is reduced, yet the "
            "long pulse length remains constant.",
        }

        self.multiple_choice(answer=answer, correct_answer="B", feedback=feedback)

    def question_6(self, answer=None):
        """
        The chopper needs to be inserted outside of the ESS monolith which has a radius of 6 m. Where in the McStas component sequence would that have to go?

        - A: before feeder
        - B: after feeder
        - C: before expanding
        - D: after expanding
        """

        feedback = {
            "A": "No, the feeder starts inside the monolith where there is no room for a chopper.",
            "B": "Yes, the feeder ends just outside the monolith, so this is a great spot",
            "C": "Yes, the expanding section of the guide starts shortly after the monolith ends "
            "so this would be a great spot.",
            "D": "No, the chopper performs better close to the source, there are better places to "
            "add it.",
        }

        if not isinstance(answer, list):
            answer = [answer]

        for single_answer in answer:
            self.multiple_choice(
                answer=single_answer, correct_answer=["B", "C"], feedback=feedback
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
        if "DiskChopper" not in comp_types:
            print_box(
                "Did not find any DiskChopper added to this instrument object", False
            )
            return

        if not comp_types.count("DiskChopper") == 1:
            print_box(
                "Found several DiskChopper's added to this instrument, only one is necessary! "
                "You may need to rerun the notebook from the top to get a fresh start.",
                False,
            )
            return

        chopper_name = name_of_component_type(answer, "DiskChopper")
        comp_names = [x.name for x in answer.component_list]

        chopper_index = comp_names.index(chopper_name)
        feeder_index = comp_names.index("feeder")
        expanding_index = comp_names.index("expanding")

        if chopper_index < feeder_index:
            print_box(
                "The DiskChopper was inserted before the feeder, this won't work!",
                False,
            )
            return

        if chopper_index > expanding_index:
            print_box(
                "The DiskChopper was inserted after the expanding section, this is not quite right",
                False,
            )
            return

        msg = "The DiskChopper was added at the right point in the component sequence and with correct parameters!"
        required_pars = dict(
            yheight=0.05,
            radius=0.35,
            nu="frequency_multiplier*14.0",
            nslit=1.0,
            delay="delay",
            theta_0=7.0,
        )
        self.last_component_in_instr_check(
            answer=answer,
            comp_type_str="DiskChopper",
            required_pars=required_pars,
            required_AT_relative=None,
            required_AT_data=None,
            required_ROTATED_relative=None,
            required_ROTATED_data=None,
            success_msg=msg,
            comp_name=chopper_name,
            print_output=True,
        )

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
            print_box(
                "Did not find any DiskChopper added to this instrument object", False
            )
            return

        if not comp_types.count("DiskChopper") == 1:
            print_box(
                "Found several DiskChopper's added to this instrument, only one is necessary! "
                "You may need to rerun the notebook from the top to get a fresh start.",
                False,
            )
            return

        chopper_name = name_of_component_type(answer, "DiskChopper")
        comp_names = [x.name for x in answer.component_list]

        chopper_index = comp_names.index(chopper_name)
        feeder_index = comp_names.index("feeder")
        expanding_index = comp_names.index("expanding")

        if chopper_index < feeder_index:
            print_box(
                "The DiskChopper was inserted before the feeder, this won't work!",
                False,
            )
            return

        if chopper_index > expanding_index:
            print_box(
                "The DiskChopper was inserted after the expanding section, this is not quite right",
                False,
            )
            return

        chopper_component = answer.get_component(chopper_name)
        if chopper_component.AT_data[2] == 6.5:
            print_box(
                "The distance to the chopper was set directly as a number, use the variable name instead. It is the right value though!",
                False,
            )
            return

        msg = "The DiskChopper was added at the right point in the space!"
        required_pars = dict(
            yheight=0.05,
            radius=0.35,
            nu="frequency_multiplier*14.0",
            nslit=1.0,
            delay="delay",
            theta_0=7.0,
        )
        self.last_component_in_instr_check(
            answer=answer,
            comp_type_str="DiskChopper",
            required_pars=required_pars,
            required_AT_relative="Source",
            required_AT_data=[0, 0, "chopper_position"],
            required_ROTATED_relative=None,
            required_ROTATED_data=None,
            success_msg=msg,
            comp_name=chopper_name,
            print_output=True,
        )

    def question_9(self, answer=None):
        """
        - Q: Whats the relative time uncertainty with this setup? Insert the answer as a percentage.
        - A: 0.4665176401 %
        """
        success_msg = "Yes!"
        below_msg = (
            "Expected a larger value, are you using the full width at half max convention? "
            "It should be possible to zoom and get mouse coordinates on the plot."
        )
        above_msg = (
            "Expected a smaller value. You can ignore the small side peak. "
            "It should be possible to zoom and get mouse coordinates on the plot."
        )

        self.insert_value(
            answer,
            0.4665176401,
            feedback_correct=success_msg,
            feedback_below=below_msg,
            feedback_above=above_msg,
            tolerance_factor=0.15,
        )

    def question_10(self, answer=None):
        """
        ### Set parameters for run with Si sample
        Set wavelength interval from 0.5 to 4.0 Å
        Select sample called "sample_Si", you will need to use '"string"'.
        """
        # check instrument object parameters

        required_parameters = dict(
            frequency_multiplier=3,
            l_min=0.5,
            l_max=4.0,
            detector_height=1.5,
            sample_radius=0.005,
            sample_height=0.02,
            sample_choice='"sample_Si"',
            n_pulses=1,
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

    def question_11(self, answer=None):
        """
        What do we see in the plots from event data?

        - A: Inelastic peaks
        - B: Magnetic scattering
        - C: Bragg peaks
        """

        feedback = {
            "A": "No, this instrument does not analyse the neutron energy after scattering, it assumes elastic scattering.",
            "B": "No, there is no magnetic properties in the simulated sample",
            "C": "Yes, the visible curves follow Braggs law, the incoming wavelength is correlated with the "
            "time and thus the different bragg peaks follow their own curve in wavelength and theta.",
        }

        if not isinstance(answer, list):
            answer = [answer]

        for single_answer in answer:
            self.multiple_choice(
                answer=single_answer, correct_answer=["C"], feedback=feedback
            )
