import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import datetime
import json
import numpy as np

from modules.Environment import Environment
from modules.Bees import Swarm

RANDOM_SEED = 42
TESTING = False

def make_directories(experiment_dir, experiment_i, num_worker_bees):
    # Experiment directory
    experiment_dir_path = "{}/experiment_{}".format(experiment_dir, experiment_i)

    # data directory
    data_dir_path = "{}/data".format(experiment_dir_path)

    # plots directory
    plots_dir_path = "{}/plots".format(experiment_dir_path)

    # environment plots directory
    env_plots_dir_path = "{}/plots/environment".format(experiment_dir_path)

    dir_paths = [experiment_dir_path, data_dir_path, plots_dir_path, env_plots_dir_path]

    # Worker plots
    for worker_i in range(num_worker_bees):
        woker_dir_path = "{}/worker_{}".format(plots_dir_path, worker_i+1)
        dir_paths.append(woker_dir_path)

    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    return dir_paths

def run_experiment(experiment_i, experiment_dir, queen_bee_params, worker_bee_params, diffusion_coefficient, spatiotemporal_parameters):
    # Make Directories
    # ---------------------------------------------------------------------------
    dirs = make_directories(experiment_dir, experiment_i, worker_bee_params["number"])
    experiment_dir_path = dirs[0]
    data_dir_path = dirs[1]
    plots_dir_path = dirs[2]
    env_plots_dir_path = dirs[3]
    # ---------------------------------------------------------------------------

    swarm_parameters = {
        "queen_bee_concentration"   : queen_bee_params["concentration"],
        "worker_bee_concentration"  : worker_bee_params["concentration"],
        "worker_bee_threshold"      : worker_bee_params["threshold"],
        "num_workers"               : worker_bee_params["number"],
        "delta_t"                   : spatiotemporal_parameters["temporal"]["delta_t"],
        "delta_x"                   : spatiotemporal_parameters["spatial"]["delta_x"],
        "min_x"                     : spatiotemporal_parameters["spatial"]["min_x"],
        "max_x"                     : spatiotemporal_parameters["spatial"]["max_x"],
        "emission_periods"          : {
            "queen"     : queen_bee_params["emission_period"],
            "worker"    : worker_bee_params["emission_period"]
        },
        "queen_movement_params"     : {
            "disable_pheromone" : worker_bee_params["disable_pheromone"]
        },
        "worker_plot_dir"           : plots_dir_path
    }


    plot_params = {
        "display_real_img"  : True,
        "save_dir"          : env_plots_dir_path
    }

    # Save parameters
    # ---------------------------------------------------------------------------
    config_save_path = "{}/config.json".format(experiment_dir_path)
    save_params = {
        "swarm_parameters" : swarm_parameters,
        "diffusion_coefficient" : diffusion_coefficient,
        "spatiotemporal_parameters" : spatiotemporal_parameters
    }
    with open(config_save_path, "w") as outfile:
        json.dump(save_params, outfile)
    # ---------------------------------------------------------------------------

    swarm = Swarm(**swarm_parameters)
    env = Environment(swarm.bees, diffusion_coefficient, spatiotemporal_parameters, plot_params, data_dir_path)
    env.run()

def main():

    num_workers = 10
    diffusion_coefficient = 0.25
    queen_emission_period = 15
    worker_emission_period = 4
    disable_pheromone_on_worker_movement = True

    spatiotemporal_parameters = {
        "spatial"   : {
            "min_x"     : -2,
            "max_x"     : 2,
            "delta_x"   : 0.005
        },
        "temporal"  : {
            "start_t"   : 0,
            "finish_t"  : 10.0,
            "delta_t"   : 0.05
        }
    }

    queen_bee_concentrations = [0.01*(i+1) for i in range(10)]
    worker_bee_concentrations = [0.005*(i+1) for i in range(10)]
    worker_bee_thresholds = [0.005*(i+1) for i in range(10)]


    # Create directory for current experiment
    # -----------------------------------------------------------------------------
    experiment_timestamp = datetime.datetime.now().strftime("%mM_%dD-%HH_%MM_%SS")
    experiment_dir = "experiments/{}".format(experiment_timestamp)
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)
    # -----------------------------------------------------------------------------

    if TESTING:
        queen_bee_params = {
            "concentration"     : 0.1,
            "emission_period"   : 15
        }

        worker_bee_params = {
            "number"            : num_workers,
            "concentration"     : 0.01,
            "threshold"         : 0.05,
            "emission_period"   : 4,
            "disable_pheromone" : True
        }

        experiment_params = {
            "experiment_i"              : 1,
            "experiment_dir"            : experiment_dir,
            "queen_bee_params"          : queen_bee_params,
            "worker_bee_params"         : worker_bee_params,
            "diffusion_coefficient"     : diffusion_coefficient,
            "spatiotemporal_parameters" : spatiotemporal_parameters
        }
        run_experiment(**experiment_params)
    else:
        experiment_i = 0
        for queen_bee_concentration in queen_bee_concentrations:
            for worker_bee_concentration in worker_bee_concentrations:
                for worker_bee_threshold in worker_bee_thresholds:
                    print("Experiment {} --- Queen Concentration: {} -- Worker Concentration: {} -- Threshold: {}".format(experiment_i, queen_bee_concentration, worker_bee_concentration, worker_bee_threshold))
                    queen_bee_params = {
                        "concentration"     : queen_bee_concentration,
                        "emission_period"   : queen_emission_period
                    }

                    worker_bee_params = {
                        "number"            : num_workers,
                        "concentration"     : worker_bee_concentration,
                        "threshold"         : worker_bee_threshold,
                        "emission_period"   : worker_emission_period,
                        "disable_pheromone" : disable_pheromone_on_worker_movement
                    }

                    experiment_params = {
                        "experiment_i"              : experiment_i,
                        "experiment_dir"            : experiment_dir,
                        "queen_bee_params"          : queen_bee_params,
                        "worker_bee_params"         : worker_bee_params,
                        "diffusion_coefficient"     : diffusion_coefficient,
                        "spatiotemporal_parameters" : spatiotemporal_parameters
                    }

                    run_experiment(**experiment_params)

                    experiment_i += 1

if __name__ == '__main__':
    np.random.seed(seed=RANDOM_SEED)
    main()
