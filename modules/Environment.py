import sys
import json
import numpy as np
import seaborn as sns
import pandas as pd
import h5py

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import ListedColormap

# DM
from modules.Bees import Bee

from modules.Bees import Swarm
from modules.Plotting import Plotter

class Environment(Plotter):
    def __init__(self, bees, diffusion_coefficient, spatiotemporal_parameters, plot_params, data_dir_path, real_time_visualization, plotting_on):
        super(Environment, self).__init__()
        self._setup_spatial_information(**spatiotemporal_parameters["spatial"])
        self._setup_temporal_information(**spatiotemporal_parameters["temporal"])
        self.bees = bees
        self.display_real_img = plot_params["display_real_img"]
        self.real_time_visualization = real_time_visualization

        self.diffusion_coefficient = diffusion_coefficient
        self.data_dir_path = data_dir_path

        # Instantiate environment plot figure
        self.plotting_on = plotting_on
        if self.plotting_on:
            self._setup_plots(plot_params)

        self.measurements = {
            "distance_from_queen"   : [],
            "concentration_history" : {},
            "position_history"      : {},
            "distance_from_others"  : []    # DM added
        }

        # DM's adds
        self.worker_measurements = {"distance_from_others": []}
        # End DM's adds

        self.concentration_map_history = []


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

    # DM's adds
    def _get_distances_to_other_bees(self, bee_positions):
        for bee_pos in bee_positions:
            if bee_positions[bee_pos] != "queen":
                worker_bee = bee_positions[bee_pos]
                worker_x = worker_bee["x"]
                worker_y = worker_bee["y"]

                worker_names = []
                worker_distances = []
                for bee, pos in bee_positions.items():
                    if bee == worker_bee:
                        continue

                    other_worker_x = pos["x"]
                    other_worker_y = pos["y"]
                    distance_to_other = np.sqrt((worker_x - other_worker_x)**2 + (worker_y - other_worker_y)**2)

                    worker_names.append(bee.replace("_", "").capitalize())
                    worker_distances.append(distance_to_other)

                # Save measurement
                worker_measurement_data = {"distances": worker_distances, "average": np.median(worker_distances)}
                #self.worker_measurements["distance_from_others"].append(worker_measurement_data)
                self.measurements["distance_from_others"].append(worker_measurement_data)

                self.worker_distance_df = pd.DataFrame({"workers": worker_names, "worker_distances": worker_distances})
    # End DM's adds

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

    def log_measurement(self, bee_type, measurement):
        # DM commented out
        # print(measurement)
        # position_data = {"x" : measurement["x"], "y" : measurement["y"], "found_queen_direction" : found_queen_direction}

        # DM added
        position_data = {
            "x"                     : measurement["x"],
            "y"                     : measurement["y"],
            "found_queen_direction" : measurement["found_queen_direction"]
        }

        concentration_data = measurement["concentration"]

        if bee_type in self.measurements["concentration_history"]:
            self.measurements["concentration_history"][bee_type].append(concentration_data)
            self.measurements["position_history"][bee_type].append(position_data)
        else:
            self.measurements["concentration_history"][bee_type] = [concentration_data]
            self.measurements["position_history"][bee_type] = [position_data]

    def run(self, run_event):
        pheromone_emission_sources = []
        for environment_timestep_i, environment_timestep in enumerate(self.t_array):

            # Kill thread
            if not run_event.is_set():
                break

            # Display current timestep
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

                # Log info
                self.log_measurement(bee.type, bee_info)

                # Get the bee's global position info
                x_i, y_i = self._get_global_position(bee_info)

                # Update global bee positions
                global_bee_positions[bee.type] = {"x" : bee_info["x"], "y" : bee_info["y"]}

                # Let the bee sense their environment
                bee.sense_environment(environment_concentration_map, x_i, y_i)

            # Calculate distances to queen
            self._get_distances_to_queen(global_bee_positions)

            # DM's adds
            self._get_distances_to_other_bees(global_bee_positions)
            # End DM's adds

            # Plot the environment
            self.concentration_map_history.append(environment_concentration_map.tolist())
            if self.plotting_on:
                plot_info = {
                    "concentration_map" : environment_concentration_map,
                    "time_i"            : environment_timestep_i,
                    "timestep"          : environment_timestep,
                    "init"              : environment_timestep_i==0
                }
                self.display_environment_map(**plot_info)

        # Save data
        # ------------------------------------------------------------
        self._save_measurement_data()
        # self._save_concentration_map()
        # ------------------------------------------------------------

        if self.plotting_on:
            plt.close(self.fig)

    def _save_measurement_data(self):
        with open("{}/measurements.json".format(self.data_dir_path), "w") as outfile:
            json.dump(self.measurements, outfile)

        # DM's adds
        # with open("{}/distance_to_others_history.json".format(self.data_dir_path), "w") as outfile:
        #     json.dump(self.worker_measurements, outfile)

    # DM commented out these maps - do not need for now
    # def _save_concentration_map(self):
    #     for map_i, map in enumerate(self.concentration_map_history):
    #         with h5py.File("{}/concentration_maps/concentration_map_history_{}.h5".format(self.data_dir_path, map_i), "w") as outfile:
    #             outfile.create_dataset("concentration_map_history", data=map)
