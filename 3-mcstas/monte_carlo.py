import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import widgets
from IPython.display import display, clear_output

# Function to update plots and estimate Pi
def plot_points(square_side_length, circle_radius,n=100):
    global points_inside_circle, total_points, estimates, estimate
    global points_x_inside, points_y_inside, points_x_outside, points_y_outside

    for _ in range(n):
        x, y = np.random.rand(2)*square_side_length  # Random points x, y between 0 and 1
        distance = np.sqrt((x-0.5*square_side_length)**2 + (y-0.5*square_side_length)**2)

        total_points += 1

        if distance <= circle_radius:
            points_inside_circle += 1
            points_x_inside.append(x)
            points_y_inside.append(y)
        else:
            points_x_outside.append(x)
            points_y_outside.append(y)

        # area of circle = pi*circle_radius**2
        # area of box = side_length**2
        # estimate =

        estimate = square_side_length**2/circle_radius**2 * points_inside_circle / total_points
        estimates.append(estimate)

    # Update scatter plots
    scatter_inside.set_offsets(np.c_[points_x_inside, points_y_inside])
    scatter_outside.set_offsets(np.c_[points_x_outside, points_y_outside])

    # Update line plot
    line.set_data(range(len(estimates)), estimates)
    if len(estimates) == 0:
        line_pi.set_data([0, 1], [np.pi, np.pi])
    else:
        line_pi.set_data([0, len(estimates)], [np.pi, np.pi])

    ax[1].relim()
    ax[1].autoscale_view()


    ax[1].set_title(f'Estimate of Pi: {estimate}')
    ax[1].set_xlabel('Number of Points')
    ax[1].set_ylabel('Estimate Value')

    # Update the figure
    fig.canvas.draw()


def example(points=100, square_side_length=1, circle_diameter=1):
    global points_inside_circle, total_points, estimates, estimate
    global points_x_inside, points_y_inside, points_x_outside, points_y_outside, scatter_outside, scatter_inside
    global line, line_pi
    global fig, ax
    circle_radius = 0.5*circle_diameter

    # Initialize some variables
    points_inside_circle = 0
    total_points = 0
    estimates = []
    estimate = 0
    points_x_inside = []
    points_y_inside = []
    points_x_outside = []
    points_y_outside = []

    # Initialize the plots
    fig, ax = plt.subplots(1, 2, figsize=(8, 6))

    # Create initial scatter plots and line plot
    scatter_inside = ax[0].scatter([], [], marker="x", color='g')
    scatter_outside = ax[0].scatter([], [], marker="x", color='r')
    line, = ax[1].plot([], [])
    line_pi, = ax[1].plot([], [], "k--")
    ax[1].text(0, np.pi, "$\pi$", fontsize=20, va="top")

    # Draw square and circle
    ax[0].add_patch(plt.Rectangle((0,0), square_side_length, square_side_length, fill=False))
    ax[0].add_patch(plt.Circle((0.5*square_side_length, 0.5*square_side_length), circle_radius, fill=False))
    ax[0].set_aspect('equal', 'box')

    # Initial Plot
    plot_points(square_side_length, circle_radius, 100)


    plt.tight_layout()


def example_interactive(square_side_length=1, circle_diameter=1):
    global points_inside_circle, total_points, estimates, estimate
    global points_x_inside, points_y_inside, points_x_outside, points_y_outside, scatter_inside, scatter_outside

    circle_radius = 0.5*circle_diameter

    # Initialize some variables
    points_inside_circle = 0
    total_points = 0
    estimates = []
    estimate = 0
    points_x_inside = []
    points_y_inside = []
    points_x_outside = []
    points_y_outside = []

    # Initialize the plots
    fig, ax = plt.subplots(1, 2, figsize=(8, 6))

    # Create initial scatter plots and line plot
    scatter_inside = ax[0].scatter([], [], marker="x", color='g')
    scatter_outside = ax[0].scatter([], [], marker="x", color='r')
    line, = ax[1].plot([], [])
    line_pi, = ax[1].plot([], [], "k--")
    ax[1].text(0, np.pi, "$\pi$", fontsize=20, va="top")

    # Draw square and circle
    ax[0].add_patch(plt.Rectangle((0,0), square_side_length, square_side_length, fill=False))
    ax[0].add_patch(plt.Circle((0.5*square_side_length, 0.5*square_side_length), circle_radius, fill=False))
    ax[0].set_aspect('equal', 'box')

    # Function to update plots and estimate Pi
    def plot_points(n=1):
        global points_inside_circle, total_points, estimates, estimate
        global points_x_inside, points_y_inside, points_x_outside, points_y_outside, scatter_inside, scatter_outside

        for _ in range(n):
            x, y = np.random.rand(2)*square_side_length  # Random points x, y between 0 and 1
            distance = np.sqrt((x-0.5*square_side_length)**2 + (y-0.5*square_side_length)**2)

            total_points += 1

            if distance <= circle_radius:
                points_inside_circle += 1
                points_x_inside.append(x)
                points_y_inside.append(y)
            else:
                points_x_outside.append(x)
                points_y_outside.append(y)

            # area of circle = pi*circle_radius**2
            # area of box = side_length**2
            # estimate =

            estimate = square_side_length**2/circle_radius**2 * points_inside_circle / total_points
            estimates.append(estimate)

        # Update scatter plots
        scatter_inside.set_offsets(np.c_[points_x_inside, points_y_inside])
        scatter_outside.set_offsets(np.c_[points_x_outside, points_y_outside])

        # Update line plot
        line.set_data(range(len(estimates)), estimates)
        if len(estimates) == 0:
            line_pi.set_data([0, 1], [np.pi, np.pi])
        else:
            line_pi.set_data([0, len(estimates)], [np.pi, np.pi])

        ax[1].relim()
        ax[1].autoscale_view()
        ax[1].set_xlabel('Number of Points')
        ax[1].set_ylabel('Estimate Value')

        # Update the figure
        fig.canvas.draw()

    # Create a button to add a random point
    button = widgets.Button(description='Add Point')

    def on_button_click(b):
        plot_points(1)
    button.on_click(on_button_click)

    ten_button = widgets.Button(description='Add 10 Points')
    def on_ten_button_click(b):
        plot_points(10)
    ten_button.on_click(on_ten_button_click)

    # Initial Plot
    plot_points(0)

    # Display button
    display(button)
    display(ten_button)

    plt.tight_layout()
