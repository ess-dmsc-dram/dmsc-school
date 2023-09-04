import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from .component import Source, Arm, Propagator, Mirror, RectangularTube, Monitor

from .ray import Ray

class Simulator:
    def __init__(self):
        self.components = []

    def add_component(self, name, *args, relative=None, **kwargs):
        if name == "Source":
            obj = Source(*args, **kwargs)
        elif name == "Arm":
            obj = Arm(*args, **kwargs)
        elif name == "Propagator":
            obj = Propagator(*args, **kwargs)
        elif name == "Guide":
            obj = RectangularTube(*args, **kwargs)
        elif name == "Mirror":
            obj = Mirror(*args, **kwargs)
        elif name == "Monitor":
            obj = Monitor(*args, **kwargs)
        else:
            raise ValueError("Unknown component name")

        self.include_component(obj, relative=relative)
        return obj

    def include_component(self, component, relative=None):
        if relative:
            component.set_global_coordinates(relative.global_position, relative.global_rotation)
        else:
            component.set_global_coordinates(np.array([0, 0, 0]), np.array([0, 0, 0]))

        self.components.append(component)

    def transform_to_local(self, ray, component):
        rotation_matrix = R.from_euler('xyz', -component.global_rotation, degrees=True)
        if len(ray.history) > 0:
            local_history = rotation_matrix.apply(np.array(ray.history) - component.global_position)
            ray.history = local_history.tolist()

        rotation_matrix = R.from_euler('xyz', -component.global_rotation, degrees=True)
        local_direction = rotation_matrix.apply(ray.direction)
        ray.set_direction(local_direction)
        return ray

    def transform_to_global(self, ray, component):
        rotation_matrix = R.from_euler('xyz', component.global_rotation, degrees=True)
        if len(ray.history) > 0:
            global_history = rotation_matrix.apply(np.array(ray.history)) + component.global_position
            ray.history = global_history.tolist()

        rotation_matrix = R.from_euler('xyz', component.global_rotation, degrees=True)
        global_direction = rotation_matrix.apply(ray.direction)
        ray.set_direction(global_direction)
        return ray

    def run(self, num_rays):
        rays = []
        for _ in range(num_rays):
            ray = Ray()
            for component in self.components:
                ray = self.transform_to_local(ray, component)
                ray = component.interact(ray)
                ray = self.transform_to_global(ray, component)
            rays.append(ray)
        return rays

    def visualize(self, rays):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for component in self.components:
            component.visualize(ax)
        for ray in rays:
            ray_points = np.array(ray.history)
            ax.plot(ray_points[:,0], ray_points[:,1], ray_points[:,2], color=ray.color)

        ax.view_init(elev=90, azim=30)
        plt.show()

    def transform_points_to_global(self, points, position, rotation_matrix):
        # Apply rotation
        rotated_points = [rotation_matrix @ point for point in points]
        # Apply translation
        translated_points = [point + position for point in rotated_points]
        return translated_points

    def transform_points_to_global(self, points, position, rotation_matrix):
        # Apply rotation and translation
        rotated_points = [rotation_matrix.apply(np.array(point)) for point in points]
        translated_points = [point + position for point in rotated_points]
        #translated_points = [point for point in rotated_points]
        return translated_points

    def visualize(self, rays, show_coordinates=False, ray_alpha=0.7, aspect=(2,1,1)):
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        first_component = True


        for component in self.components:

            local_points_list = component.get_visualization_points()

            rotation_matrix = R.from_euler('xyz', component.global_rotation, degrees=True)
            for local_points in local_points_list:
                # Transform points to the global coordinate system
                global_points = self.transform_points_to_global(local_points, component.global_position,
                                                                rotation_matrix)

                # print("global", global_points)
                x, y, z = zip(*global_points)

                # Use different order to get z horizontal
                ax.plot(z, x, y, "-k")

            if show_coordinates:
                if isinstance(show_coordinates, float):
                    clx = show_coordinates
                    cly = show_coordinates
                    clz = show_coordinates
                elif isinstance(show_coordinates, list):
                    clx = show_coordinates[0]
                    cly = show_coordinates[1]
                    clz = show_coordinates[2]
                else:
                    clx = 0.1
                    cly = 0.1
                    clz = 0.1

                local_coordinate_points = [([0,0,0], [clx,0,0]), ([0,0,0], [0,cly,0]), ([0,0,0], [0,0,clz])]
                global_coordinate_points = self.transform_points_to_global(local_coordinate_points,
                                                                           component.global_position,
                                                                           rotation_matrix)

                if first_component:
                    x, y, z = zip(*global_coordinate_points[0])
                    ax.plot(z, x, y, "-r", label="x")

                    x, y, z = zip(*global_coordinate_points[1])
                    ax.plot(z, x, y, "-g", label="y")

                    x, y, z = zip(*global_coordinate_points[2])
                    ax.plot(z, x, y, "-b", label="z")

                    first_component = False
                else:
                    x, y, z = zip(*global_coordinate_points[0])
                    ax.plot(z, x, y, "-r")

                    x, y, z = zip(*global_coordinate_points[1])
                    ax.plot(z, x, y, "-g")

                    x, y, z = zip(*global_coordinate_points[2])
                    ax.plot(z, x, y, "-b")

        for ray in rays:
            ray_points = np.array(ray.history)
            ax.plot(ray_points[:,2], ray_points[:,0], ray_points[:,1], color=ray.color, alpha=ray_alpha)


        if component.is_monitor:
            # This is a monitor, try to show result
            #component.show_data(ax)


            x, y = component.get_axis_1D()
            X, Y = np.meshgrid(x, y)
            Z = np.zeros(X.shape)

            X_flat = X.flatten()
            Y_flat = Y.flatten()
            Z_flat = Z.flatten()

            coordinates = []
            for index in range(len(X_flat)):
                coordinates.append(np.array([X_flat[index], X_flat[index], Z_flat[index]]))

            rotation_matrix = R.from_euler('xyz', component.global_rotation, degrees=True)
            global_coordinates = self.transform_points_to_global(coordinates, component.global_position, rotation_matrix)

            X_flat_global = np.zeros(X_flat.shape)
            Y_flat_global = np.zeros(Y_flat.shape)
            Z_flat_global = np.zeros(Z_flat.shape)
            for index in range(len(global_coordinates)):
                X_flat_global[index] = global_coordinates[index][0]
                Y_flat_global[index] = global_coordinates[index][1]
                Z_flat_global[index] = global_coordinates[index][2]

            X_global = X_flat_global.reshape(X.shape)
            Y_global = Y_flat_global.reshape(Y.shape)
            Y_global = Y_global.T
            Z_global = Z_flat_global.reshape(Z.shape)

            if component.counts.sum() > 0:
                color_value = component.intensity/np.max(np.max(component.intensity))
                my_col = cm.winter(color_value.T)
                surf = ax.plot_surface(Z_global, X_global, Y_global, rstride=1, cstride=1,
                                       facecolors=my_col, linewidth=0, antialiased=False, shade=False)

        ax.set_xlabel("z [m]")
        ax.set_ylabel("x [m]")
        ax.set_zlabel("y [m]")

        ax.set_box_aspect(aspect)

        if show_coordinates:
            ax.legend()

        plt.show()
        plt.tight_layout()

