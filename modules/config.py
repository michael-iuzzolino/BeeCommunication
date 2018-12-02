RANDOM_SEED = 42

TESTING = False      # Testing with one set of parameters
PLOTTING_ON = False
REAL_TIME_VISUALIZATION = False

THREADING_ON = True
NUM_ITERATIONS_PER_EXPERIMENTAL_CONDITION = 1 # Ideally, 10

NUM_WORKERS = 50
RANDOM_BEE_POSITIONS = True # If False, reads from bee_positions.txt

CONDITION_COUNTS = {
    "queen"                     : 2,
    "worker_concentration"      : 1,
    "worker_threshold"          : 1,
    "diffusion_coefficient"     : 1
}

THREADS = []
SECONDS_TO_RUN = 8
DELTA_T = 0.05 # 0.05
DELTA_X = 0.01 # 0.01
MIN_X = -3
MAX_X = 3

ROTATE_BEES_ON = False
DIFFUSION_COEFFICIENT = 0.15 # Used for TESTING
QUEEN_EMISSION_PERIOD = 6
WORKER_EMISSION_PERIOD = 4
WORKER_BEE_THRESHOLD = 0.5
DISABLE_PHEROMONE_ON_WORKER_MOVEMENT = True
