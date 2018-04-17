import sys
import json
import numpy as np
import seaborn as sns
import pandas as pd
import h5py

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import ListedColormap

from modules.Bees import Swarm

class Environment(object):
    def __init__(self, bees, diffusion_coefficient, spatiotemporal_parameters, plot_params, data_dir_path, real_time_visualization):
        self._setup_spatial_information(**spatiotemporal_parameters["spatial"])
        self._setup_temporal_information(**spatiotemporal_parameters["temporal"])
        self.bees = bees
        self.display_real_img = plot_params["display_real_img"]
        self.real_time_visualization = real_time_visualization

        self.diffusion_coefficient = diffusion_coefficient
        self.data_dir_path = data_dir_path

        # Instantiate environment plot figure
        self._setup_plots(plot_params)

        self.measurements = {"distance_from_queen" : []}

        self.concentration_map_history = []

        self.other_bee_distances = []

    def _setup_plots(self, plot_params):
        self.plot_save_dir = plot_params['save_dir']
        self.plot_bee = "worker_1"
        self.full_event_keys = ""

        fig = plt.figure(figsize=(9, 7))
        self.fig = fig

        grid = plt.GridSpec(7, 5, wspace=0.4, hspace=0.3)
        self.concentration_map = fig.add_subplot(grid[0:3, 0:3])
        self.information_plot = fig.add_subplot(grid[:4, 3:5])
        self.distance_plot = fig.add_subplot(grid[3:4, :3])
        self.concentration_history_plot = fig.add_subplot(grid[5:, 3:])
        self.distance_history_plot = fig.add_subplot(grid[5:, :2])

        cmaps = ["magma", "plasma", "viridis", sns.cubehelix_palette(20)]
        self.concentration_cmap = cmaps[0]

        # Switch bee profile
        # ----------------------------------------------------------------------
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
        # ----------------------------------------------------------------------

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
        self.min_x = min_x
        self.max_x = max_x

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

        def find_nearest(array, value):
            idx = (np.abs(array-value)).argmin()
            return array[idx]

        try:
            x_i = np.where(self.X1 == find_nearest(self.X1, bee_info["x"]))[0][0]
            y_i = np.where(self.X2 == find_nearest(self.X2, bee_info["y"]))[0][0]
        except:
            print('bee_info["x"]: {}'.format(bee_info["x"]))
            print('bee_info["y"]: {}'.format(bee_info["y"]))

        return x_i, y_i

    def display_environment_map(self, concentration_map, time_i, timestep, init):
        if init:
            self.vmax = np.max(concentration_map.flatten())

        # Environment concentration heatmap
        sns.heatmap(concentration_map, cbar=False, cmap=self.concentration_cmap, ax=self.concentration_map, vmin=0, vmax=self.vmax, xticklabels=0, yticklabels=0)

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
            if len(self.bees) < 14:
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


        # Distance Bar Plot
        # ----------------------------------------------------------------------------------------
        bee_distance_plot = sns.barplot(x="bees", y="bee_distances", data=self.bee_distance_df, color="salmon", ax=self.distance_plot)
        self.distance_plot.set_ylim(0, self.max_distance_from_center)
        for item in bee_distance_plot.get_xticklabels():
            item.set_rotation(45)

        self.concentration_map.set_title("Timestep {}: {}s".format(time_i, timestep))
        self.distance_plot.set(xlabel="", ylabel='Distance to Queen')
        # ----------------------------------------------------------------------------------------


        # Plot average distance to queen
        # ----------------------------------------------------------------------------------------
        ave_distances = [ele["average"] for ele in self.measurements["distance_from_queen"]]
        self.distance_history_plot.plot(ave_distances)
        self.distance_history_plot.set_title("Average Distance from Queen")
        self.distance_history_plot.set(xlabel='Timestep', ylabel='Average Distance')
        # ----------------------------------------------------------------------------------------

        plt.savefig("{}/environment_timestep_{}".format(self.plot_save_dir, time_i))

        if self.real_time_visualization:
            plt.pause(0.005)

        self.concentration_map.cla()
        self.information_plot.cla()
        self.distance_plot.cla()

    # def _get_distances_to_other_bees(self, bee_positions):
    #
    #     target_bees = [bee for bee in bee_positions.keys() if bee != "queen"] # ["worker_1", "worker_2", ..., "worker_N"]
    #
    #     for target_bee in target_bees:
    #         target_bee_position = bee_positions[target_bee]
    #         target_bee_x = target_bee_position["x"]
    #         target_bee_y = target_bee_position["y"]
    #
    #         other_bees = [bee for bee in target_bees if bee != target_bee]
    #         distances = []
    #         for other_bee in otherbees:
    #             other_bee_position = bee_positions[other_bee]
    #             other_bee_x = other_bee_position["x"]
    #             other_bee_y = other_bee_position["y"]
    #
    #             distance = np.sqrt((target_bee_x - other_bee_x)**2 + (target_bee_y - other_bee_y)**2)
    #             distances.append(distance)
    #
    #         distance_average = np.mean(distances)
    #
    #         other_bee_distances.append({"bee_id" : target_bee, "distance_average" : distance_average})



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

        # Save measurement
        measurement_data = { "distances" : bee_distances, "average" : np.median(bee_distances)}
        self.measurements["distance_from_queen"].append(measurement_data)

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
            full_bee_data[bee.type] = {
                "concentration_history" : list(bee.concentration_history),
                "position_history"      : list(bee.position_history)
            }

        with open("{}/bee_concentration_history.json".format(self.data_dir_path), "w") as outfile:
            json.dump(full_bee_data, outfile)

    def _save_concentration_map(self):
        for map_i, map in enumerate(self.concentration_map_history):
            with h5py.File("{}/concentration_maps/concentration_map_history_{}.h5".format(self.data_dir_path, map_i), "w") as outfile:
                outfile.create_dataset("concentration_map_history", data=map)

    def run(self):
        pheromone_emission_sources = []
        for environment_timestep_i, environment_timestep in enumerate(self.t_array):

            sys.stdout.write("\rTimestep {}/{}".format(environment_timestep_i+1, len(self.t_array)))
            sys.stdout.flush()

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
                self.concentration_map_history.append(environment_concentration_map.tolist())
                self.display_environment_map(**plot_info)
            except KeyboardInterrupt:
                exit(0)

        self._save_measurement_data()
        self._save_concentration_map()
        plt.close(self.fig)

    def _save_measurement_data(self):
        with open("{}/distance_to_queen_history.json".format(self.data_dir_path), "w") as outfile:
            json.dump(self.measurements, outfile)
