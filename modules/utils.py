import os
from modules.config import *

def make_directories(experiment_dir, experiment_i, Q, W, D, T, experiment_iteration, num_worker_bees):
    # Experiment directory
    experiment_dir_path = "{}/experiment{}_Q{}_W{}_D{}_T{}".format(experiment_dir, experiment_i, Q, W, D, T,)

    # data directory
    data_dir_path = "{}/data".format(experiment_dir_path)

    # Concentration maps - DM commented out
    concentration_map_dir_path = "{}/data/concentration_maps".format(experiment_dir_path)

    dir_paths = [experiment_dir_path, data_dir_path, concentration_map_dir_path]

    # plots directory
    if PLOTTING_ON:
        plots_dir_path = "{}/plots".format(experiment_dir_path)

        dir_paths.append(plots_dir_path)

        # environment plots directory
        env_plots_dir_path = "{}/plots/environment".format(experiment_dir_path)

        dir_paths.append(env_plots_dir_path)

        # Worker plots
        for worker_i in range(num_worker_bees):
            woker_dir_path = "{}/worker_{}".format(plots_dir_path, worker_i+1)
            dir_paths.append(woker_dir_path)

    # Make dirs
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    return dir_paths

def check_all_threads_finished():
    all_finished = True
    for thread in THREADS:
        if not thread.isAlive():
            thread.join()
            all_finished = False
    return all_finished
