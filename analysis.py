import os
import json
import glob2
import numpy as np
import matplotlib.pyplot as plt

experiment_folders_list = glob2.glob("experiments/*")

experiment_dir = experiment_folders_list[0]

experiments_list = np.sort(glob2.glob("{}/*".format(experiment_dir)))

distance_history = {}

fig, ax = plt.subplots(2, 1, figsize=(6,7))

for experiment_i, experiment_path in enumerate(experiments_list):
    config_path = os.path.join(experiment_path, "config.json")
    with open(config_path, "r") as config_infile:
        config_info = json.load(config_infile)
        spatiotemporal_parameters = config_info["spatiotemporal_parameters"]
        delta_t = spatiotemporal_parameters["temporal"]["delta_t"]

        diffusion_coefficient = config_info["diffusion_coefficient"]
        queen_bee_concentration = config_info["swarm_parameters"]["queen_bee_concentration"]
        worker_bee_concentration = config_info["swarm_parameters"]["worker_bee_concentration"]

        params = {
            "diffusion_coefficient"     : diffusion_coefficient,
            "queen_bee_concentration"   : queen_bee_concentration,
            "worker_bee_concentration"  : worker_bee_concentration
        }

    data_path = os.path.join(experiment_path, "data", "distance_to_queen_history.json")
    with open(data_path, "r") as data_infile:
        data = json.load(data_infile)["distance_from_queen"]

    for key, vals in distance_history.items():
        D = vals["params"]["diffusion_coefficient"]
        Q_C = vals["params"]["queen_bee_concentration"]
        W_C = vals["params"]["worker_bee_concentration"]
        label = "D: {}, Q_C: {}, W_C: {}".format(D, Q_C, W_C)
        ax[1].plot(vals["timesteps"], vals["averages"], label=label)

    plt.legend()

    averages = []
    timesteps = []
    timestep = 0
    for data_i in data:
        average_distance = data_i["average"]
        averages.append(average_distance)
        timesteps.append(timestep)
        timestep += delta_t
        ax[0].plot(timesteps, averages)

        ax[0].set_title("diffusion_coefficient: {}\n worker_bee_concentration: {}\n queen_bee_concentration: {}".format(diffusion_coefficient, worker_bee_concentration, queen_bee_concentration))
        ax[0].set_xlabel("Timestep (s)")
        ax[0].set_ylabel("Average Distance to Queen")

        plt.pause(0.05)
        ax[0].cla()

    ax[1].cla()

    distance_history["experiment_{}".format(experiment_i)] = {
        "params"    : params,
        "averages"  : averages,
        "timesteps" : timesteps
    }
