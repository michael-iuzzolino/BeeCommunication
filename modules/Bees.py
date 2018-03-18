import numpy as np

class Bee(object):
    def __init__(self, bee_type, init_position, pheromone_concentration, activation_threshold, movement, activity, bias, delta_t, delta_x):

        self.type = bee_type
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
        self.found_queen_direction = False
        self.wait_threshold = 4 # wait 4 timesteps after finding the queen before moving
        self.num_timesteps_waited = 0

        # Bias is directed pheromone emission
        self.bias_x, self.bias_y = bias

        self.pheromone_emission_timestep = 1

        # Spatiotemporal intervals
        self.delta_t = delta_t
        self.delta_x = delta_x

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

                # Update position to head in direction of queen
                steps = np.random.randint(1, 6)
                self.x += self.directions_to_queen["x"]*self.delta_x*steps
                self.y += self.directions_to_queen["y"]*self.delta_x*steps

        # If random movement active, determine new movement behavior
        elif self.random_movement_active:

            # Pick direction, sign, and magnitude
            direction = "x" if np.random.uniform() < 0.5 else "y"
            sign = 1 if np.random.uniform() < 0.5 else -1
            steps = np.random.randint(1, 6)

            # Update random movement direction
            self.__dict__[direction] += self.delta_x*sign*steps

    def sense_environment(self, concentration_map, x_i, y_i):
        if self.found_queen:
            return
            
        # Check if worker will be activated
        if not self.pheromone_active:
            if concentration_map[x_i, y_i] >= self.activation_threshold:
                self.activate_pheromones()
                self.find_queen(concentration_map, x_i, y_i)

        # look for queen, if appropriate
        if self.queen_directed_movement:
            self.find_queen(concentration_map, x_i, y_i)

        self.update()

    def measure(self):
        bee_info = {
            "x"             : self.x,
            "y"             : self.y,
            "bias_x"        : self.bias_x,
            "bias_y"        : self.bias_y,
            "emission_t"    : self.pheromone_emission_timestep * self.delta_t
        }
        return bee_info

    def activate_pheromones(self):
        self.pheromone_active = True
        self.random_movement_active = False

    def find_queen(self, concentration_map, x_i, y_i):
        current_c = concentration_map[x_i, y_i]
        local_map = concentration_map[x_i-1:x_i+2, y_i-1:y_i+2]

        try:
            max_c = np.max(local_map[np.where(local_map > current_c)])
            max_index = list(np.where(local_map == max_c))
            max_indices = [int(i)-1 for i in max_index]

            self.directions_to_queen = { "x" : max_indices[0], "y": max_indices[1] }
            self.found_queen_direction = True

            # Update bias
            bias_x = -1 if self.directions_to_queen["x"] > 0 else 1
            bias_y = -1 if self.directions_to_queen["y"] > 0 else 1

            norm = np.sqrt(bias_x**2 + bias_y**2) + 1e-9

            self.bias_x = bias_x / float(norm)
            self.bias_y = bias_y / float(norm)
        except ValueError:
            self.found_queen = True
            self.queen_directed_movement = False

class Swarm(object):
    def __init__(self, num_workers, queen_bee_concentration, worker_bee_concentration, worker_bee_threshold, delta_t, delta_x):

        queen_data = {
            "init_position"             : (0, 0),
            "pheromone_concentration"   : queen_bee_concentration,
            "activation_threshold"      : worker_bee_threshold,
            "activity"                  : {
                "movement"  : False,
                "pheromone" : True
            },
            "movement"                  : (0.0, 0.0),
            "bias"                      : (0, 0)
        }

        bees = {"queen" : queen_data}

        bee_distances = [0.4, 0.55, 0.95, 1.05]
        sign = lambda : 1 if np.random.uniform() < 0.5 else -1
        position = lambda : bee_distances[np.random.randint(len(bee_distances))]*sign()
        new_position = lambda bee_i : (position(), position())

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
            "bias"                      : temp_bias
        }

        worker_bees = {"worker_{}".format(i+1) : get_worker_data(i) for i in range(num_workers)}

        for worker_bee, worker_bee_info in worker_bees.items():
            bees[worker_bee] = worker_bee_info

        self.bees = []
        for bee, bee_info in bees.items():
            bee_info["bee_type"] = bee
            bee_info["delta_t"] = delta_t
            bee_info["delta_x"] = delta_x
            self.bees.append(Bee(**bee_info))
