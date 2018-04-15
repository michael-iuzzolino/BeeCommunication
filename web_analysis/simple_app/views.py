from simple_app import app
from flask import render_template, jsonify, request
import os
import json
import glob2
import numpy as np
import h5py

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/load_experiment', methods=["GET", "POST"])
def load_experiment():
    experiment_id = request.json['experiment_id']
    timestep = int(request.json['timestep'])
    concentration_map_history_path = "simple_app/static/data/{}/data/concentration_maps/concentration_map_history_{}.h5".format(experiment_id, timestep)
    with h5py.File(concentration_map_history_path, "r") as infile:
        concentration_map_history = np.array(infile["concentration_map_history"])

    concentration_data = []
    for row_i, row in enumerate(concentration_map_history):
        if row_i % 5 != 0:
            continue
        for col_i, element in enumerate(row):
            if col_i % 5 != 0:
                continue
            concentration_data.append({"x" : row_i, "y" : col_i, "value" : element})

    results_dict = {
        "concentration_map_history" : concentration_data
    }

    return jsonify(results_dict)

@app.route('/load_data', methods=["GET", "POST"])
def load_data():
    experiments_list = glob2.glob("simple_app/static/data/*")

    distance_history = {}

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

        averages = []
        timesteps = []
        timestep = 0
        for data_i in data:
            average_distance = data_i["average"]
            averages.append(average_distance)
            timesteps.append(timestep)
            timestep += delta_t

        distance_history["experiment_{}".format(experiment_i)] = {
            "params"    : params,
            "averages"  : averages,
            "timesteps" : timesteps
        }

    results_dict = {"results" : distance_history}

    return jsonify(results_dict)
