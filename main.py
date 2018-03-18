import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from modules.Environment import Environment
from modules.Bees import Swarm

def main():

    delta_t = 0.05
    delta_x = 0.005
    diffusion_coefficient = 0.2
    num_workers = 8

    spatiotemporal_parameters = {
        "spatial"   : {
            "min_x"     : -2,
            "max_x"     : 2,
            "delta_x"   : delta_x
        },
        "temporal"  : {
            "start_t"   : 0,
            "finish_t"  : 5.0,
            "delta_t"   : delta_t
        }
    }

    swarm_parameters = {
        "queen_bee_concentration"   : 0.1,
        "worker_bee_concentration"  : 0.05,
        "worker_bee_threshold"      : 0.05,
        "num_workers"               : num_workers,
        "delta_t"                   : delta_t,
        "delta_x"                   : delta_x,
    }
    swarm = Swarm(**swarm_parameters)

    env = Environment(swarm.bees, diffusion_coefficient, spatiotemporal_parameters)
    env.run()

if __name__ == '__main__':
    main()
