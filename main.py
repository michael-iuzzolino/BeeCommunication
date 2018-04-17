import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import datetime
import json
import numpy as np

from modules.Environment import Environment
from modules.Bees import Swarm

RANDOM_SEED = 42
TESTING = True
REAL_TIME_VISUALIZATION = True
ROTATE_BEES_ON = False

NUM_WORKERS = 100
RANDOM_BEE_POSITIONS = True # If False, reads from bee_positions.txt

CONDITION_COUNTS = {
    "queen" : 2,
    "worker_concentration" : 2,
    "worker_threshold" : 2,
    "diffusion_cefficient" : 2
}

SECONDS_TO_RUN = 2
DELTA_T = 0.05 # 0.05
DELTA_X = 0.1 # 0.01
MIN_X = -5
MAX_X = 5


DIFFUSION_COEFFICIENT = 0.25
QUEEN_EMISSION_PERIOD = 5
WORKER_EMISSION_PERIOD = 2
WORKER_BEE_THRESHOLD = 0.5
DISABLE_PHEROMONE_ON_WORKER_MOVEMENT = True

def make_directories(experiment_dir, experiment_i, num_worker_bees):
    # Experiment directory
    experiment_dir_path = "{}/experiment_{}".format(experiment_dir, experiment_i)

    # data directory
    data_dir_path = "{}/data".format(experiment_dir_path)

    concentration_map_dir_path = "{}/data/concentration_maps".format(experiment_dir_path)

    # plots directory
    plots_dir_path = "{}/plots".format(experiment_dir_path)

    # environment plots directory
    env_plots_dir_path = "{}/plots/environment".format(experiment_dir_path)

    dir_paths = [experiment_dir_path, data_dir_path, plots_dir_path, env_plots_dir_path, concentration_map_dir_path]

    # Worker plots
    for worker_i in range(num_worker_bees):
        woker_dir_path = "{}/worker_{}".format(plots_dir_path, worker_i+1)
        dir_paths.append(woker_dir_path)

    # Make dirs
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
        "worker_plot_dir"           : plots_dir_path,
        "rotate_bees_ON"            : ROTATE_BEES_ON,
        "random_positions"          : RANDOM_BEE_POSITIONS
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
    env = Environment(swarm.bees, diffusion_coefficient, spatiotemporal_parameters, plot_params, data_dir_path, REAL_TIME_VISUALIZATION)
    env.run()

def main():
    spatiotemporal_parameters = {
        "spatial"   : {
            "min_x"     : MIN_X,
            "max_x"     : MAX_X,
            "delta_x"   : DELTA_X
        },
        "temporal"  : {
            "start_t"   : 0,
            "finish_t"  : SECONDS_TO_RUN,
            "delta_t"   : DELTA_T
        }
    }

    queen_bee_concentrations = np.linspace(0.01, 0.5, CONDITION_COUNTS["queen"])
    worker_bee_concentrations = np.linspace(0.005, 0.5, CONDITION_COUNTS["worker_concentration"])
    diffusion_coefficients = np.linspace(0.05, 0.5, CONDITION_COUNTS["worker_threshold"])
    worker_bee_thresholds = np.linspace(0, 0.5, CONDITION_COUNTS["diffusion_cefficient"])

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
            "number"            : NUM_WORKERS,
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
            "diffusion_coefficient"     : DIFFUSION_COEFFICIENT,
            "spatiotemporal_parameters" : spatiotemporal_parameters
        }
        run_experiment(**experiment_params)
    else:
        num_experiments = len(queen_bee_concentrations) * len(worker_bee_concentrations) * len(diffusion_coefficients) * len(worker_bee_thresholds)
        experiment_i = 0
        for queen_bee_concentration in queen_bee_concentrations:
            for worker_bee_concentration in worker_bee_concentrations:
                for diffusion_coefficient in diffusion_coefficients:
                    for worker_bee_threshold in worker_bee_thresholds:
                        print("\n\nExperiment {}/{} --- Queen Concentration: {} -- Worker Concentration: {} -- Diffussion Coefficient: {}".format(experiment_i+1, num_experiments, queen_bee_concentration, worker_bee_concentration, diffusion_coefficient))
                        queen_bee_params = {
                            "concentration"     : queen_bee_concentration,
                            "emission_period"   : QUEEN_EMISSION_PERIOD
                        }

                        worker_bee_params = {
                            "number"            : NUM_WORKERS,
                            "concentration"     : worker_bee_concentration,
                            "threshold"         : worker_bee_threshold,
                            "emission_period"   : WORKER_EMISSION_PERIOD,
                            "disable_pheromone" : DISABLE_PHEROMONE_ON_WORKER_MOVEMENT
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
