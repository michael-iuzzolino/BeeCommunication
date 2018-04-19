from simple_app import app
from flask import render_template, jsonify, request
import os
import sys
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

    # Load concentration history for heatmap
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    concentration_map_history_path = "{}/{}/data/concentration_maps/concentration_map_history_{}.h5".format(experiment_folder, experiment_id, timestep)
    with h5py.File(concentration_map_history_path, "r") as infile:
        concentration_map_history = np.array(infile["concentration_map_history"])

    concentration_data = []
    for row_i, row in enumerate(concentration_map_history):
        if row_i % 5 != 0:
            continue
        for col_i, element in enumerate(row):
            if col_i % 5 != 0:
                continue
            concentration_data.append({"x" : col_i, "y" : row_i, "value" : element})
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Load in measurements (bee concentration and position histories)
    # --------------------------------------------------------------------------------------------
    measurements_path = "{}/{}/data/measurements.json".format(experiment_folder, experiment_id)
    with open(measurements_path, "r") as infile:
        measurements = json.load(infile)

    bees_position_history = {}
    bee_concentration_history = {}
    for key, val in measurements.items():
        if key == "distance_from_queen":
            continue
        if key == "position_history":
            for bee_key, bee_val in val.items():
                bee_position = bee_val[timestep]
                bees_position_history[bee_key] = bee_position
        elif key == "concentration_history":
            for bee_key, bee_val in val.items():
                bee_concentration = bee_val
                bee_concentration_history[bee_key] = bee_concentration
    # --------------------------------------------------------------------------------------------

    results_dict = {
        "concentration_map_history" : concentration_data,
        "bees_position_history"     : bees_position_history,
        "bee_concentration_history" : bee_concentration_history
    }

    return jsonify(results_dict)

@app.route('/load_data', methods=["GET", "POST"])
def load_data():
    global experiment_folder
    experiment_folder = request.json["folder_path"]

    experiments_list = glob2.glob("{}/*".format(experiment_folder))

    distance_history = {}

    for experiment_i, experiment_path in enumerate(experiments_list):
        experiment_id = experiment_path.split("/")[-1]

        config_path = os.path.join(experiment_path, "config.json")
        with open(config_path, "r") as config_infile:
            config_info = json.load(config_infile)
            
            spatiotemporal_parameters = config_info["spatiotemporal_parameters"]
            delta_t = spatiotemporal_parameters["temporal"]["delta_t"]
            min_x = spatiotemporal_parameters["spatial"]["min_x"]
            max_x = spatiotemporal_parameters["spatial"]["max_x"]

            diffusion_coefficient = config_info["diffusion_coefficient"]
            queen_bee_concentration = config_info["swarm_parameters"]["queen_bee_concentration"]
            worker_bee_concentration = config_info["swarm_parameters"]["worker_bee_concentration"]
            worker_bee_threshold = config_info["swarm_parameters"]["worker_bee_threshold"]
            params = {
                "diffusion_coefficient"     : diffusion_coefficient,
                "queen_bee_concentration"   : queen_bee_concentration,
                "worker_bee_concentration"  : worker_bee_concentration,
                "worker_bee_threshold"      : worker_bee_threshold,
                "min_x"                     : min_x,
                "max_x"                     : max_x,
            }

        data_path = os.path.join(experiment_path, "data", "measurements.json")
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

    results_dict = {"results" : distance_history, "params" : params}

    return jsonify(results_dict)

@app.route('/init_experiment_folders', methods=["GET", "POST"])
def init_experiment_folders():
    experiment_folders = glob2.glob('../experiments/*')
    return jsonify({"experiment_folders" : experiment_folders})

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
