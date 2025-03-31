from .quiz import Quiz, make_red, make_green, make_orange, print_box
from .helpers import name_of_component_type, is_instrument_object


class Powder_Quiz(Quiz):
    def __init__(self):
        super().__init__()
