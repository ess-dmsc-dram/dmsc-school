import numpy as np
import math
import random
from scipy.spatial.transform import Rotation as R


class Component:
    def __init__(self, position=np.array([0, 0, 0]), rotation=np.array([0, 0, 0])):
        self.position = np.array(position)
        self.rotation = np.array(rotation)
        self.global_position = None
        self.global_rotation = None
        self.is_monitor = False

    def set_global_coordinates(self, parent_position, parent_rotation):
        rotation_matrix = R.from_euler('xyz', parent_rotation, degrees=True)
        self.global_position = rotation_matrix.apply(self.position) + parent_position
        self.global_rotation = parent_rotation + self.rotation

    def interact(self, ray):
        return ray

    def visualize(self, ax):
        pass

class Source(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0],
                 normal=[0,0,1], width=1, height=1, angle_spread=1):
        super().__init__(position, rotation)
        self.normal = np.array(normal) / np.linalg.norm(normal)  # Ensure it's a unit vector
        self.width = width
        self.height = height
        self.angle_spread = math.radians(angle_spread)  # Convert to radians

    def interact(self, ray):
        # Calculate the random starting point on the rectangle
        offset_x = random.uniform(-self.width / 2, self.width / 2)
        offset_y = random.uniform(-self.height / 2, self.height / 2)

        # Starting point in the local coordinate system
        local_start_point = np.array([offset_x, offset_y, 0])

        # Set the starting point and direction of the ray
        ray.add_point(local_start_point)

        # Add random angular deviation to the normal vector for the ray direction
        theta = random.uniform(-self.angle_spread, self.angle_spread)
        phi = random.uniform(0, 2 * math.pi)

        dx = math.sin(theta) * math.cos(phi)
        dy = math.sin(theta) * math.sin(phi)
        dz = math.cos(theta)

        deviation_vector = np.array([dx, dy, dz])

        # Rotate deviation vector to align with the source's normal
        rotation_axis = np.cross([0, 0, 1], self.normal)
        rotation_angle = math.acos(np.dot([0, 0, 1], self.normal))

        rotation_matrix = R.from_rotvec(rotation_angle * rotation_axis)
        rotated_deviation = rotation_matrix.apply(deviation_vector)

        final_direction = self.normal + rotated_deviation
        final_direction = final_direction / np.linalg.norm(final_direction)  # Re-normalize to unit vector

        ray.set_direction(final_direction)

        return ray

    def visualize(self, ax):
        # Create the 4 corners of the rectangle in the local coordinate system
        half_width = self.width / 2
        half_height = self.height / 2
        corners_local = np.array([
            [half_width, half_height, 0],
            [-half_width, half_height, 0],
            [-half_width, -half_height, 0],
            [half_width, -half_height, 0]
        ])

        # Transform the corners to the global coordinate system
        rotation_matrix = R.from_euler('xyz', self.global_rotation, degrees=True)
        corners_global = rotation_matrix.apply(corners_local) + self.global_position

        # Extract x, y, z coordinates of the corners
        x, y, z = corners_global.T

        # Plot the rectangle edges
        ax.plot([x[0], x[1]], [y[0], y[1]], [z[0], z[1]], c='k')
        ax.plot([x[1], x[2]], [y[1], y[2]], [z[1], z[2]], c='k')
        ax.plot([x[2], x[3]], [y[2], y[3]], [z[2], z[3]], c='k')
        ax.plot([x[3], x[0]], [y[3], y[0]], [z[3], z[0]], c='k')

    def get_visualization_points(self):
        corner1 = np.array([-self.width / 2, -self.height / 2, 0])
        corner2 = np.array([self.width / 2, -self.height / 2, 0])
        corner3 = np.array([self.width / 2, self.height / 2, 0])
        corner4 = np.array([-self.width / 2, self.height / 2, 0])

        return [(corner1, corner2, corner3, corner4, corner1)]


class Propagator(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], distance=1):
        super().__init__(position, rotation)
        self.distance = distance

    def interact(self, ray):
        # Calculate the new position based on the ray's direction and the distance
        new_position = ray.history[-1] + ray.direction * self.distance

        # Add the new position to the ray's history
        ray.add_point(new_position)

        return ray

    def visualize(self, ax):
        # Visualization for the Propagator could be a line segment indicating
        # the direction and distance of propagation. We'll start the line at the
        # component's position and extend it in the direction the rays will be propagated.

        start = self.global_position
        end = start + self.distance * np.array(
            [0, 0, 1])  # Assume rays propagate along z-axis in local coordinate system

        ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], c='r', linestyle='--')

    def get_visualization_points(self):
        start = self.position
        end = start + self.distance * np.array([0, 0, 1])

        return []

class Arm(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0]):
        super().__init__(position, rotation)

    def interact(self, ray):
        return ray

    def visualize(self, ax):
        # Visualization for the Propagator could be a line segment indicating
        # the direction and distance of propagation. We'll start the line at the
        # component's position and extend it in the direction the rays will be propagated.
        pass

    def get_visualization_points(self):
        return []


class Mirror(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0],
                 width=1, height=1, verbose=False):
        super().__init__(position, rotation)
        self.normal = np.array([1, 0, 0])
        self.width = width
        self.height = height
        self.verbose = verbose

    def interact(self, ray):
        # Assume the ray's last point is its current position
        ray_start = ray.history[-1]

        # Find the intersection point between the ray and the mirror
        N = self.normal
        P0 = np.array([0, 0, 0])
        L0 = ray_start
        L = ray.direction

        # Ensure N and L are normalized
        N = N / np.linalg.norm(N)
        L = L / np.linalg.norm(L)

        t = np.dot(P0 - L0, N) / np.dot(L, N)

        if t < 0:
            # Ray is pointing away from the mirror
            return ray

        intersection = L0 + t * L

        # Check if the intersection point is within the size of the mirror
        half_width = self.width / 2
        half_height = self.height / 2
        if abs(intersection[2]) > half_width or abs(intersection[1]) > half_height:
            # Ray missed the mirror
            """
            if self.verbose:
                print("missed", t, ray.history)
            """
            return ray

        # Calculate the reflected direction
        R = L - 2 * np.dot(L, N) * N
        ray.set_direction(R)

        # Add the intersection point to the ray's history
        ray.add_point(intersection)

        if self.verbose:
            print("hit", t)
            for history in ray.history:
                print("  ", history)

        return ray
    """
    def visualize(self, ax):
        # Create the 4 corners of the square mirror in the local coordinate system
        half_size = self.size / 2
        corners_local = np.array([
            [half_size, half_size, 0],
            [-half_size, half_size, 0],
            [-half_size, -half_size, 0],
            [half_size, -half_size, 0]
        ])

        # Transform the corners to the global coordinate system
        rotation_matrix = R.from_euler('xyz', self.global_rotation, degrees=True)
        corners_global = rotation_matrix.apply(corners_local) + self.global_position

        # Extract x, y, z coordinates of the corners
        x, y, z = corners_global.T

        # Plot the mirror edges
        ax.plot([x[0], x[1]], [y[0], y[1]], [z[0], z[1]], c='k')
        ax.plot([x[1], x[2]], [y[1], y[2]], [z[1], z[2]], c='k')
        ax.plot([x[2], x[3]], [y[2], y[3]], [z[2], z[3]], c='k')
        ax.plot([x[3], x[0]], [y[3], y[0]], [z[3], z[0]], c='k')
    """

    def get_visualization_points(self):

        """
        corner1 = np.array([-self.width / 2, -self.height / 2, 0])
        corner2 = np.array([self.width / 2, -self.height / 2, 0])
        corner3 = np.array([self.width / 2, self.height / 2, 0])
        corner4 = np.array([-self.width / 2, self.height / 2, 0])
        """

        corner1 = np.array([0, -self.height / 2, -self.width / 2])
        corner2 = np.array([0, -self.height / 2, self.width / 2])
        corner3 = np.array([0, self.height / 2, self.width / 2])
        corner4 = np.array([0, self.height / 2, -self.width / 2])

        return [(corner1, corner2, corner3, corner4, corner1)]


class Monitor(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0],
                 width=1, height=1, nx=20, ny=20, verbose=False):
        super().__init__(position, rotation)
        self.normal = np.array([0, 0, 1])
        self.width = width
        self.height = height
        self.verbose = verbose

        self.is_monitor = True
        self.nx = nx
        self.ny = ny
        self.intensity = np.zeros((nx, ny))
        self.counts = np.zeros((nx, ny))

    def interact(self, ray):
        # Assume the ray's last point is its current position
        ray_start = ray.history[-1]

        # Find the intersection point between the ray and the mirror
        N = self.normal
        P0 = np.array([0, 0, 0])
        L0 = ray_start
        L = ray.direction

        # Ensure N and L are normalized
        N = N / np.linalg.norm(N)
        L = L / np.linalg.norm(L)

        t = np.dot(P0 - L0, N) / np.dot(L, N)

        if t < 0:
            # Ray is pointing away from the mirror
            return ray

        intersection = L0 + t * L

        # Check if the intersection point is within the size of the mirror
        half_width = self.width / 2
        half_height = self.height / 2
        if abs(intersection[0]) > half_width or abs(intersection[1]) > half_height:
            # Ray missed the monitor
            return ray

        detector_x = intersection[0] + half_width
        detector_y = intersection[1] + half_height

        index_x = int(np.floor(self.nx*detector_x/self.width))
        index_y = int(np.floor(self.ny*detector_y/self.height))

        self.intensity[index_x, index_y] += ray.weight
        self.counts[index_x, index_y] += 1

        # Add the intersection point to the ray's history
        ray.add_point(intersection)

        if self.verbose:
            print("hit", t)
            for history in ray.history:
                print("  ", history)

        return ray

    def get_visualization_points(self):

        corner1 = np.array([-self.width / 2, -self.height / 2, 0])
        corner2 = np.array([self.width / 2, -self.height / 2, 0])
        corner3 = np.array([self.width / 2, self.height / 2, 0])
        corner4 = np.array([-self.width / 2, self.height / 2, 0])

        return [(corner1, corner2, corner3, corner4, corner1)]

    def get_axis_1D(self):
        x = np.linspace(-0.5 * self.width, 0.5 * self.width, self.nx)
        y = np.linspace(-0.5 * self.height, 0.5 * self.height, self.ny)

        return x, y

    def get_axis_3D(self):

        x, y = self.get_axis_1D()

        X = np.zeros((self.nx, 3))
        Y = np.zeros((self.ny, 3))

        X[:, 0] = x
        Y[:, 1] = y

        return X, Y

    def show_data(self, ax):
        pass


class RectangularTube(Component):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0],
                 width=0.1, height=0.1, length=1, verbose=False):
        super().__init__(position, rotation)
        self.width = width
        self.height = height
        self.length = length

    def find_intersection(self, ray, wall_normal, wall_point, side):
        # Implement ray-plane intersection logic here and check the boundaries
        # If there's an intersection within the tube wall, return the distance `t` and the intersection point
        # Otherwise, return None, None
        ray_start = ray.history[-1]

        # Find the intersection point between the ray and the mirror
        N = np.array(wall_normal)
        P0 = np.array(wall_point)
        L0 = ray_start
        L = ray.direction

        # Ensure N and L are normalized
        N = N / np.linalg.norm(N)
        L = L / np.linalg.norm(L)

        t = np.dot(P0 - L0, N) / np.dot(L, N)

        if t < 0:
            # Ray is pointing away from the mirror
            return None, None, 1

        intersection = L0 + t * L

        if side in ["top", "bottom"]:
            if abs(intersection[0]) > self.width/2 or intersection[2] < 0 or intersection[2] > self.length:
                # Ray missed the mirror
                return None, None, 1

        elif side in ["left", "right"]:
            if abs(intersection[1]) > self.height/2 or intersection[2] < 0 or intersection[2] > self.length:
                # Ray missed the mirror
                return None, None, 1
        else:
            raise ValueError("Side not recognized")

        """
        # Check if the intersection point is within the size of the mirror
        half_width = dimensions[0] / 2
        half_height = dimensions[1] / 2
        if abs(intersection[0]) > half_width or abs(intersection[1]) > half_height:
            # Ray missed the mirror
            return None, 1, 1
        """

        # Calculate the reflected direction
        R = L - 2 * np.dot(L, N) * N

        return t, intersection, R

    def interact(self, ray):
        max_reflections = 500  # Set a limit to avoid infinite loop
        num_reflections = 0
        last_side = None

        while num_reflections < max_reflections:
            closest_t = float('inf')
            closest_intersection = None
            closest_normal = None

            # Define normals for the four walls
            normals = [
                [0, 1, 0],  # Bottom
                [0, -1, 0],   # Top
                [1, 0, 0],  # Left
                [-1, 0, 0]    # Right
            ]

            wall_points = [
                [0, -self.height/2, self.length/2],  # Bottom
                [0, self.height/2, self.length/2],  # Top
                [-self.width/2, 0, self.length/2],  # Left
                [self.width/2, 0, self.length/2]  # Right
            ]

            dimension_list = [
                [self.length, self.width],
                [self.length, self.width],
                [self.length, self.height],
                [self.length, self.height],
            ]

            side_list = ["bottom", "top", "left", "right"]

            # Find the closest wall that the ray will hit next
            for normal, wall_point, side in zip(normals, wall_points, side_list):
                if side == last_side:
                    # Skip the last side as the ray is on that side.
                    continue

                t, intersection_point, new_direction = self.find_intersection(ray, normal, wall_point, side)

                if t is not None and t < closest_t:
                    closest_t = t
                    closest_intersection = intersection_point
                    closest_new_direction = new_direction
                    closest_side = side


            # If the ray doesn't hit any wall, it has left the tube
            if closest_intersection is None:
                break

            # Reflect the ray off the closest wall
            ray.add_point(closest_intersection)
            ray.set_direction(closest_new_direction)
            num_reflections += 1
            last_side = closest_side

        return ray

    def get_visualization_points(self):
        # Define corner points for visualization

        corner1 = np.array([-self.width / 2, -self.height / 2, 0])
        corner2 = np.array([self.width / 2, -self.height / 2, 0])
        corner3 = np.array([self.width / 2, self.height / 2, 0])
        corner4 = np.array([-self.width / 2, self.height / 2, 0])
        corner5 = np.array([-self.width / 2, -self.height / 2, self.length])
        corner6 = np.array([self.width / 2, -self.height / 2, self.length])
        corner7 = np.array([self.width / 2, self.height / 2, self.length])
        corner8 = np.array([-self.width / 2, self.height / 2, self.length])

        return [(corner1, corner2, corner3, corner4, corner1,
                corner5, corner6, corner2, corner6,
                corner7, corner3, corner7, corner8,
                corner4, corner8, corner5)]