import numpy as np


class Ray:
    def __init__(self,
                 direction=np.array([0, 0, 1]),
                 color='gray', weight=1):
        self.color = color
        self.weight = weight
        self.history = []
        self.direction = direction / np.linalg.norm(direction)  # Ensure it's a unit vector

    def add_point(self, point):
        self.history.append(np.array(point))

    def set_direction(self, direction):
        self.direction = direction / np.linalg.norm(direction)  # Ensure it's a unit vector
