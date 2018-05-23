# Imports
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import scipy
from scipy import ndimage
from skimage.transform import rotate
import matplotlib.pyplot as plt

################################### CLASS: BEES #######################################

class Bee(object):
    def __init__(self, bee_type, init_position, pheromone_concentration, activation_threshold, movement, activity, bias, delta_t, delta_x, min_x, max_x, emission_period, queen_movement_params, plot_dir, rotate_bees_ON=False):
        # Class constructor method

        self.type = bee_type                            # Queen or worker
        self.rotate_bees_ON = rotate_bees_ON            # Rotating images not working yet... False for now

        self.img = ndimage.imread('imgs/queen_bee.png') if bee_type == "queen" else ndimage.imread('imgs/worker_bee.png')
        self.current_heading = 90

        self.x, self.y = init_position
        self.random_movement_active = activity["movement"]
        self.pheromone_active = activity["pheromone"]
        self.concentration = pheromone_concentration
        self.activation_threshold = activation_threshold

        # Movement of the bee
        self.dx, self.dy = movement

        # Set queen finding behavior params
        self.queen_directed_movement = False
        self.found_queen = False
        self.queen_movement_params = queen_movement_params
        self.found_queen_direction = False
        self.wait_threshold = int(np.random.normal(10, 1)) # wait X timesteps after finding the queen before moving
        self.num_timesteps_waited = 0

        # Bias is directed pheromone emission for workers
        self.bias_x, self.bias_y = bias

        # Emission period
        self.emission_period = emission_period
        self.pheromone_emission_timestep = 1

        # Spatiotemporal intervals
        self.delta_t = delta_t
        self.delta_x = delta_x
        self.min_x = min_x
        self.max_x = max_x

        # History information
        self.plot_dir = plot_dir

### ------------------------------------------------------- ###

    def rotate_bees(self):

        # This method rotates the bees towards the queen's direction as they
        # detetct & go uphill the pheromone gradients

        try:
            # Calculate the direction bee needs to turn from its current
            # dir to head to queen
            degree_to_queen = np.arctan2(self.bias_y, self.bias_x) * 180 / np.pi

            degree_difference = self.current_heading + degree_to_queen

            # Why make it negative?
            degree_difference *= -1

            # DM commented out this test code
            # if self.type == "worker_6":
            #     print("degree_to_queen: {}".format(degree_to_queen))
            #     print("self.current_heading: {}".format(self.current_heading))
            #     print("degree_difference: {}".format(degree_difference))
            #     raw_input("")

            # Rotate the image
            self.img = rotate(self.img, degree_to_queen)

            # Update current heading
            self.current_heading = self.current_heading

        except Exception as e:
            print(e)

### ------------------------------------------------------- ###

    def update(self):

        # If pheromone active, increment emission timestep
        if self.pheromone_active:
            self.pheromone_emission_timestep += 1

        # Check if queen has been found
        if self.found_queen_direction:
            # Check if queen-directed movement can be enabled yet
            if self.num_timesteps_waited < self.wait_threshold:
                self.num_timesteps_waited += 1
            else:
                # Waited long enough; Enable movement toward queen
                self.queen_directed_movement = True

                # Set queen movement parameters
                # ========================================================================
                if self.queen_movement_params["disable_pheromone"]:
                    self.pheromone_active = False
                # ========================================================================

                # Update position to head in direction of queen
                steps = np.random.randint(1, 4)
                self.x += self.directions_to_queen["x"]*self.delta_x*steps
                self.y += self.directions_to_queen["y"]*self.delta_x*steps

            # Rotate image!
            if self.rotate_bees_ON:
                self.rotate_bees()

        # If random movement active, determine new movement behavior
        elif self.random_movement_active:

            # Pick direction, sign, and magnitude
            direction = "x" if np.random.uniform() < 0.5 else "y"
            sign = 1 if np.random.uniform() < 0.5 else -1
            steps = np.random.randint(1, 6)

            # Constrain movement to board (self.x and self.y here)
            self.__dict__[direction] += self.delta_x*sign*steps

            if self.__dict__[direction] <= self.min_x:
                self.__dict__[direction] += self.delta_x

            elif self.__dict__[direction] >= self.max_x:
                self.__dict__[direction] -= self.delta_x

        # Constrain x and y to bounds of space (self.min_x, self.max_x)
        # ------------------------------------------------------------
        for dimension in ["x", "y"]:
            if self.__dict__[dimension] < self.min_x:
                self.__dict__[dimension] = self.min_x
            elif self.__dict__[dimension] > self.max_x:
                self.__dict__[dimension] = self.max_x
        # ------------------------------------------------------------

### ------------------------------------------------------- ###

    def sense_environment(self, concentration_map, x_i, y_i):
        # If they already found the queen, do nothing
        if self.found_queen:
            return

        # Check if worker will be activated
        if not self.pheromone_active:

            if concentration_map[x_i, y_i] >= self.activation_threshold:
                self.activate_pheromones()
                self.found_queen_direction = True

        # look for queen
        if not self.type == "queen":
            self.find_queen(concentration_map, x_i, y_i)

        self.update()

### ------------------------------------------------------- ###

    def measure(self):
        emitting = True if self.pheromone_emission_timestep % self.emission_period == 1 else False

        bee_info = {
            "x"                     : self.x,
            "y"                     : self.y,
            "bias_x"                : self.bias_x,
            "bias_y"                : self.bias_y,
            "concentration"         : self.concentration,
            "emitting"              : emitting,
            "found_queen_direction" : self.found_queen_direction,
            "type"                  : self.type
        }
        return bee_info

### ------------------------------------------------------- ###

    def activate_pheromones(self):
        self.pheromone_active = True
        self.random_movement_active = False

### ------------------------------------------------------- ###

    def find_queen(self, concentration_map, x_i, y_i):
        current_c = concentration_map[x_i, y_i]
        local_map = concentration_map[x_i-1:x_i+2, y_i-1:y_i+2]

        try:
            # Get the max concentration in the local map
            max_concentration = np.max(local_map[np.where(local_map > current_c)])

            # Get the indicies of the max concentration
            max_concentration_indices = list(np.where(local_map == max_concentration))

            # Adjust the indicies to be within [-1, 1] rather than in [0, 2]
            adjusted_indices = [int(i)-1 for i in max_concentration_indices]

            # Assign directions to queen
            self.directions_to_queen = { "x" : adjusted_indices[0], "y": adjusted_indices[1] }

            # Update bias
            bias_direction_x = -1 if self.directions_to_queen["x"] > 0 else 1
            bias_direction_y = -1 if self.directions_to_queen["y"] > 0 else 1

            # Vector norm
            norm = np.sqrt(bias_direction_x**2 + bias_direction_y**2) + 1e-9

            # Update bias
            self.bias_x = bias_direction_x / float(norm)
            self.bias_y = bias_direction_y / float(norm)

        except ValueError:
            self.found_queen = True
            self.queen_directed_movement = False

################################### CLASS: SWARM #######################################

class Swarm(object):
    def __init__(self, num_workers, queen_bee_concentration, worker_bee_concentration, worker_bee_threshold, delta_t, delta_x, min_x, max_x, emission_periods, queen_movement_params, worker_plot_dir, rotate_bees_ON, random_positions):

        queen_data = {
            "init_position"             : (0, 0),
            "pheromone_concentration"   : queen_bee_concentration,
            "activation_threshold"      : worker_bee_threshold,
            "activity"                  : {
                "movement"  : False,
                "pheromone" : True
            },
            "movement"                  : (0.0, 0.0),
            "bias"                      : (0, 0),
            "emission_period"           : emission_periods["queen"],
            "queen_movement_params"     : queen_movement_params,
            "plot_dir"                  : None
        }

        bees = {"queen" : queen_data}

        if random_positions:
            position = lambda : np.random.uniform(min_x, max_x)
            new_position = lambda bee_i : (position(), position())
        else:
            def new_position(bee_i):
                with open("bee_positions.txt", "r") as infile:
                    bee_position_data = infile.readlines()
                bee_i_position = bee_position_data[bee_i].split(",")
                bee_i_position = [float(ele) for ele in bee_i_position]

                return bee_i_position



        temp_bias_1 = 0.25
        temp_bias_2 = np.sqrt(1 - temp_bias_1**2)
        temp_bias = (temp_bias_1, temp_bias_2)

        get_worker_data = lambda bee_i : {
            "init_position"             : (new_position(bee_i)),
            "pheromone_concentration"   : worker_bee_concentration,
            "activation_threshold"      : worker_bee_threshold,
            "activity"                  : {
                "movement"  : True,
                "pheromone" : False
            },
            "movement"                  : (0.001, 0.001),
            "bias"                      : temp_bias,
            "emission_period"           : emission_periods["worker"],
            "queen_movement_params"     : queen_movement_params,
            "plot_dir"                  : "{}/worker_{}".format(worker_plot_dir, bee_i),
            "rotate_bees_ON"            : rotate_bees_ON
        }

        worker_bees = {"worker_{}".format(i+1) : get_worker_data(i) for i in range(num_workers)}

        for worker_bee, worker_bee_info in worker_bees.items():
            bees[worker_bee] = worker_bee_info

        self.bees = []
        for bee, bee_info in bees.items():
            bee_info["bee_type"] = bee
            bee_info["delta_t"] = delta_t
            bee_info["delta_x"] = delta_x
            bee_info["min_x"] = min_x
            bee_info["max_x"] = max_x

            self.bees.append(Bee(**bee_info))
