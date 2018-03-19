import json
import numpy as np
import seaborn as sns
import pandas as pd


import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from modules.Bees import Swarm

class Environment(object):
    def __init__(self, bees, diffusion_coefficient, spatiotemporal_parameters, plot_params, data_dir_path):
        self._setup_spatial_information(**spatiotemporal_parameters["spatial"])
        self._setup_temporal_information(**spatiotemporal_parameters["temporal"])
        self.bees = bees
        self.display_real_img = plot_params["display_real_img"]

        self.diffusion_coefficient = diffusion_coefficient
        self.data_dir_path = data_dir_path

        # Instantiate environment plot figure
        self._setup_plots(plot_params)

    def _setup_plots(self, plot_params):
        self.show_plot = False

        self.plot_save_dir = plot_params['save_dir']
        self.plot_bee = "worker_1"
        self.full_event_keys = ""

        fig = plt.figure(figsize=(9, 7))
        self.fig = fig

        grid = plt.GridSpec(5, 5, wspace=0.4, hspace=0.3)
        self.concentration_map = fig.add_subplot(grid[0:3, 0:3])
        self.information_plot = fig.add_subplot(grid[:5, 3:5])
        self.distance_plot = fig.add_subplot(grid[3:4, :3])
        self.concentration_history_plot = fig.add_subplot(grid[4:, 4:])

    def imscatter(self, x, y, image, ax=None, zoom=1):
        try:
            image = plt.imread(image)
        except TypeError:
            # Likely already an array...
            pass

        im = OffsetImage(image, zoom=zoom)
        x, y = np.atleast_1d(x, y)
        artists = []
        for x0, y0 in zip(x, y):
            ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
            artists.append(ax.add_artist(ab))
        ax.update_datalim(np.column_stack([x, y]))
        ax.autoscale()
        return artists

    def _setup_spatial_information(self, min_x, max_x, delta_x):
        self.X1 = np.arange(min_x, max_x+delta_x, delta_x)
        self.X2 = np.arange(min_x, max_x+delta_x, delta_x)
        self.x_grid, self.y_grid = np.meshgrid(self.X1, self.X2)

        # Get maximum distance
        max_distance = np.sqrt(((min_x - max_x)/2.0)**2 + ((min_x - max_x)/2.0)**2)
        self.max_distance_from_center = max_distance

    def _setup_temporal_information(self, start_t, finish_t, delta_t):
        self.delta_t = delta_t
        self.t_array = np.arange(start_t, finish_t+delta_t, delta_t)
        self.t_array = self.t_array[1:]

    def _get_global_position(self, bee_info):
        x_i = int(np.where(np.abs(self.X1 - bee_info["x"]) < 1e-5)[0])
        y_i = int(np.where(np.abs(self.X2 - bee_info["y"]) < 1e-5)[0])
        return x_i, y_i

    def display_environment_map(self, concentration_map, time_i, timestep, init):
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
            if self.display_real_img:
                self.imscatter(x_i, y_i, bee.img, zoom=0.1, ax=self.concentration_map)
            else:
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

            if bee.type == self.plot_bee:
                self.concentration_history_plot.plot(bee.concentration_history, 'cyan')
                self.concentration_history_plot.set_title("{}".format(bee_name))
                self.concentration_history_plot.set(xlabel='Timesteps', ylabel='Pheromone \nConcentration')


        # Plot

        bee_distance_plot = sns.barplot(x="bees", y="bee_distances", data=self.bee_distance_df, color="salmon", ax=self.distance_plot)
        self.distance_plot.set_ylim(0,self.max_distance_from_center)
        for item in bee_distance_plot.get_xticklabels():
            item.set_rotation(45)

        self.concentration_map.set_title("Timestep {}: {}s".format(time_i, timestep))

        self.distance_plot.set(xlabel='Bees', ylabel='Distance to Queen')

        plt.savefig("{}/environment_timestep_{}".format(self.plot_save_dir, time_i))

        if self.show_plot:
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

    def _update_concentration_map(self, pheromone_emission_sources, current_timestep):

        # Instantiate concentration map as all 0's for current timestep
        environment_concentration_map = np.zeros([len(self.x_grid), len(self.x_grid)])

        for emission_source in pheromone_emission_sources:
            delta_t = current_timestep - emission_source["init_t"] + self.delta_t   #self.delta_t required to initialize
            term_1 = emission_source["concentration"] / np.sqrt(delta_t + 1e-9)
            term_2 = (self.x_grid - emission_source["x"] - emission_source["bias_x"] * delta_t)**2 + (self.y_grid - emission_source["y"] - emission_source["bias_y"] * delta_t)**2
            term_3 = 4 * self.diffusion_coefficient * delta_t + 1e-9

            # Calculate current bee's concentration map
            emission_source_map = term_1 * np.exp(-(term_2 / float(term_3)))

            # Update concentration map
            environment_concentration_map += emission_source_map

        return environment_concentration_map

    def _save_data(self):
        full_bee_data = {}
        for bee_i, bee in enumerate(self.bees):
            full_bee_data[bee.type] = list(bee.concentration_history)

        with open("{}/bee_concentration_history.json".format(self.data_dir_path), "w") as outfile:
            json.dump(full_bee_data, outfile)

    def run(self):

        def onpress(event):
            valid_events = ['{}'.format(i) for i in range(10)]
            if event.key in valid_events or event.key == 'enter':
                if event.key == 'enter':
                    if int(self.full_event_keys) > len(self.bees)-1:
                        self.full_event_keys = ""
                        print("Invalid Key Entry!")
                        return
                    self.concentration_history_plot.cla()
                    self.plot_bee = "worker_{}".format(self.full_event_keys)
                    self.full_event_keys = ""
                else:
                    self.full_event_keys += event.key

        self.fig.canvas.mpl_connect('key_press_event', onpress)

        pheromone_emission_sources = []

        for environment_timestep_i, environment_timestep in enumerate(self.t_array):

            # Iterate through each bee in the swarm to find emission sources
            for bee_i, bee in enumerate(self.bees):

                # Measure the bee
                bee_info = bee.measure()

                # If bee pheromone is active, update concentration map
                if bee.pheromone_active:

                    # Check if bee is emitting
                    if bee_info["emitting"]:
                        bee_info["init_t"] = environment_timestep

                        # Add emission to sources
                        pheromone_emission_sources.append(bee_info)

            # Update environment_concentration_map
            environment_concentration_map = self._update_concentration_map(pheromone_emission_sources, environment_timestep)

            global_bee_positions = {}
            for bee_i, bee in enumerate(self.bees):
                # Measure the bee's information
                bee_info = bee.measure()

                # Get the bee's global position info
                x_i, y_i = self._get_global_position(bee_info)

                # Update global bee positions
                global_bee_positions[bee.type] = {"x" : bee_info["x"], "y" : bee_info["y"]}

                # Let the bee sense their environment
                bee.sense_environment(environment_concentration_map, x_i, y_i)

            # Calculate distances to queen
            self._get_distances_to_queen(global_bee_positions)

            # Save data
            # ------------------------------------------------------------
            self._save_data()
            # ------------------------------------------------------------

            # Plot the environment
            try:
                plot_info = {
                    "concentration_map" : environment_concentration_map,
                    "time_i"            : environment_timestep_i,
                    "timestep"          : environment_timestep,
                    "init"              : environment_timestep_i==0
                }
                self.display_environment_map(**plot_info)
            except KeyboardInterrupt:
                exit(0)
