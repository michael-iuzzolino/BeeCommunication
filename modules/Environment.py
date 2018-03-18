import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from modules.Bees import Swarm

class Environment(object):
    def __init__(self, bees, diffusion_coefficient, spatiotemporal_parameters):
        self._setup_spatial_information(**spatiotemporal_parameters["spatial"])
        self._setup_temporal_information(**spatiotemporal_parameters["temporal"])
        self.bees = bees

        self.diffusion_coefficient = diffusion_coefficient

        # Instantiate environment plot figure
        self._setup_plots()

    def _setup_plots(self):
        fig = plt.figure(figsize=(9, 7))
        grid = plt.GridSpec(5, 5, wspace=0.4, hspace=0.3)
        self.concentration_map = fig.add_subplot(grid[0:3, 0:3])
        self.information_plot = fig.add_subplot(grid[:, 3:])
        self.distance_plot = fig.add_subplot(grid[3:4, :3])



    def _setup_spatial_information(self, min_x, max_x, delta_x):
        self.X1 = np.arange(min_x, max_x+delta_x, delta_x)
        self.X2 = np.arange(min_x, max_x+delta_x, delta_x)
        self.x_grid, self.y_grid = np.meshgrid(self.X1, self.X2)

    def _setup_temporal_information(self, start_t, finish_t, delta_t):
        self.t_array = np.arange(start_t, finish_t+delta_t, delta_t)
        self.t_array = self.t_array[1:]

    def _get_global_position(self, bee_info):
        x_i = int(np.where(np.abs(self.X1 - bee_info["x"]) < 1e-4)[0])
        y_i = int(np.where(np.abs(self.X2 - bee_info["y"]) < 1e-4)[0])

        return x_i, y_i

    def print_environment_map(self, concentration_map, timestep, init):
        if init:
            self.vmax = np.max(concentration_map.flatten())

        # Environment concentration heatmap
        sns.heatmap(concentration_map, cbar=False, cmap="magma", ax=self.concentration_map, vmin=0, vmax=self.vmax, xticklabels=0, yticklabels=0)

        self.information_plot.text(0.1, 0.95, "  Bee          Pheromone Activity", size=10)
        for bee_i, bee in enumerate(self.bees):
            x_i, y_i = self._get_global_position(bee.measure())

            bee_color = "red" if bee.random_movement_active else "green" if not bee.queen_directed_movement else "blue"
            bee_size = 30 if bee.random_movement_active else 20 if not bee.queen_directed_movement else 30

            bee_name = bee.type.replace("_", " ").capitalize()
            bee_label = "Active" if bee.pheromone_active else "Inactive"

            # Plot position
            self.concentration_map.scatter(x_i, y_i, s=bee_size, color=bee_color)

            # Bee annotate
            self.concentration_map.annotate(bee_name,
                color=bee_color,
                xy=(x_i, y_i),
                xytext=(x_i, y_i)
            )

            bee_string = "{}. {:10s}{:5s}{}".format(bee_i+1, bee_name, "", bee_label)
            self.information_plot.text(0.1, bee_i*-0.05+0.9, bee_string, color=bee_color, size=10)
            self.information_plot.set_xticks([])
            self.information_plot.set_yticks([])


        # Plot
        bee_distance_plot = sns.barplot(x="bees", y="bee_distances", data=self.bee_distance_df, color="salmon", ax=self.distance_plot)
        for item in bee_distance_plot.get_xticklabels():
            item.set_rotation(45)

        self.concentration_map.set_title("timestep: {}".format(timestep))
        plt.pause(0.005)
        self.concentration_map.cla()
        self.information_plot.cla()
        self.distance_plot.cla()

    def _get_distances_to_queen(self, bee_positions):
        queen = bee_positions["queen"]
        queen_x = queen["x"]
        queen_y = queen["y"]

        bee_names = []
        bee_distances = []
        for bee, pos in bee_positions.items():
            if bee == "queen":
                continue

            worker_x = pos["x"]
            worker_y = pos["y"]
            distance_to_queen = np.sqrt((queen_x - worker_x)**2 + (queen_y - worker_y)**2)

            bee_names.append(bee.replace("_", "").capitalize())
            bee_distances.append(distance_to_queen)

        self.bee_distance_df = pd.DataFrame({"bees" : bee_names, "bee_distances" : bee_distances})

    def run(self):

        for enironment_timestep_i, environment_timestep in enumerate(self.t_array):

            # Instantiate concentration map as all 0's for current timestep
            environment_concentration_map = np.zeros([len(self.x_grid), len(self.x_grid)])

            # Iterate through each bee in the swarm
            global_bee_positions = {}
            for bee_i, bee in enumerate(self.bees):

                # Measure the bee's information
                bee_info = bee.measure()

                # If bee pheromone is active, update concentration map
                if bee.pheromone_active:
                    term_1 = bee.concentration / np.sqrt(bee_info["emission_t"] + 1e-9)
                    term_2 = (self.x_grid - bee_info["x"] - bee_info["bias_x"] * bee_info["emission_t"])**2 + (self.y_grid - bee_info["y"] - bee_info["bias_y"] * bee_info["emission_t"])**2
                    term_3 = 4 * self.diffusion_coefficient * bee_info["emission_t"] + 1e-9

                    # Calculate current bee's concentration map
                    bee_i_concentration_map = term_1 * np.exp(-(term_2 / float(term_3)))

                    # Update concentration map
                    environment_concentration_map += bee_i_concentration_map

                # Get the bee's global position info
                x_i, y_i = self._get_global_position(bee_info)

                # Let the bee sense their environment
                bee.sense_environment(environment_concentration_map, x_i, y_i)

                # Update global bee positions
                global_bee_positions[bee.type] = {"x" : x_i, "y" : y_i}

            # Calculate distances to queen
            self._get_distances_to_queen(global_bee_positions)

            # Plot the environment
            try:
                plot_info = {
                    "concentration_map" : environment_concentration_map,
                    "timestep"          : environment_timestep,
                    "init"              : enironment_timestep_i==0
                }
                self.print_environment_map(**plot_info)
            except KeyboardInterrupt:
                exit(0)
