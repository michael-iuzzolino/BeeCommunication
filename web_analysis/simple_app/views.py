from simple_app import app
from flask import render_template, jsonify, request
import os
import json
import glob2
import numpy as np
import h5py
import pandas as pd

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/load_experiment', methods=["GET", "POST"])
def load_experiment():
    experiment_id = request.json['experiment_id']
    timestep = int(request.json['timestep'])

    print(experiment_id);

    print("timestep: {}".format(timestep))

    concentration_map_history_path = "simple_app/static/data/{}/data/concentration_maps/concentration_map_history_{}.h5".format(experiment_id, timestep)
    with h5py.File(concentration_map_history_path, "r") as infile:
        concentration_map_history = np.array(infile["concentration_map_history"])

    bee_concentration_history_path = "simple_app/static/data/{}/data/bee_concentration_history.json".format(experiment_id)
    with open(bee_concentration_history_path, "r") as infile:
        bee_concentration_history = json.load(infile)

    bees_position_history = {}
    for key, val in bee_concentration_history.items():
        bee_position = val["position_history"][timestep]
        bees_position_history[key] = bee_position

    concentration_data = []
    for row_i, row in enumerate(concentration_map_history):
        if row_i % 5 != 0:
            continue
        for col_i, element in enumerate(row):
            if col_i % 5 != 0:
                continue
            concentration_data.append({"x" : col_i, "y" : row_i, "value" : element})

    results_dict = {
        "concentration_map_history" : concentration_data,
        "bees_position_history"     : bees_position_history
    }

    return jsonify(results_dict)

@app.route('/load_data', methods=["GET", "POST"])
def load_data():
    experiments_list = glob2.glob("simple_app/static/data/*")

    distance_history = {}


    for experiment_i, experiment_path in enumerate(experiments_list):
        experiment_id = experiment_path.split("/")[-1]

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

        distance_history[experiment_id] = {
            "params"    : params,
            "averages"  : averages,
            "timesteps" : timesteps
        }

    results_dict = {"results" : distance_history}

    return jsonify(results_dict)

@app.route('/save_plot', methods=["GET", "POST"])
def save_plot():
    experiment_name = request.json['experiment_name']
    save_data = request.json['save_data']
    save_path = 'saved_data/{}.csv'.format(experiment_name)
    successful = True
    try:
        averages_series = pd.Series(save_data["averages"])
        timesteps_series = pd.Series(save_data["timesteps"])
        df = pd.concat([timesteps_series, averages_series], axis=1)
        df.columns = ["average_distances", "timesteps"]
        with open(save_path, 'w') as outfile:
            outfile.write("experiment parameters")
            for key, val in save_data["params"].items():
                outfile.write("{},{}\n".format(key, val))
        with open(save_path, 'a') as outfile:
            df.to_csv(outfile, header=True)
    except Exception as e:
        print("Error Saving Plot")
        print(e)
        successful = False

    return jsonify({"successful" : successful})
