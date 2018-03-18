import numpy as np

class Bee(object):
    def __init__(self, bee_type, init_position, pheromone_concentration, activation_threshold, movement, activity, bias, delta_t, delta_x, emission_interval):

        self.x, self.y = init_position
        self.type = bee_type
        self.movement_active = activity["movement"]
        self.pheromone_active = activity["pheromone"]
        print("pheromone_active")
        self.concentration = pheromone_concentration
        self.activation_threshold = activation_threshold

        self.dx, self.dy = movement

        self.bias_x, self.bias_y = bias

        self.found_queen = False

        self.emission_interval = emission_interval
        self.emission_timestep = 0
        self.movement_timestep = 0
        self.num_timesteps_stopped = 0
        self.delta_t = delta_t
        self.delta_x = delta_x

    def update(self):
        if self.pheromone_active:
            self.emission_timestep += 1

            if self.emission_timestep > self.emission_interval:
                self.emission_timestep = 0

        if self.movement_active and not self.found_queen:
            self.movement_timestep += 1

            # Pick direction, sign, and magnitude
            direction = "x" if np.random.uniform() < 0.5 else "y"
            sign = 1 if np.random.uniform() < 0.5 else -1
            steps = np.random.randint(1, 5)

            self.__dict__[direction] += self.delta_x*sign*steps

        if self.found_queen and self.num_timesteps_stopped < 4:
            self.num_timesteps_stopped += 1

        elif self.found_queen and self.num_timesteps_stopped >= 4:
            self.pheromone_active = False
            self.x += self.directions_to_queen["x"]*self.delta_x
            self.y += self.directions_to_queen["y"]*self.delta_x

    def sense_environment(self, concentration_map, x_i, y_i):
        if self.found_queen and self.num_timesteps_stopped >= 4:
            self.find_queen(concentration_map, x_i, y_i)

    def measure(self):
        bee_info = {
            "x"             : self.x,
            "y"             : self.y,
            "bias_x"        : self.bias_x,
            "bias_y"        : self.bias_y,
            "emission_t"    : self.emission_timestep * self.delta_t
        }
        return bee_info

    def find_queen(self, concentration_map, x_i, y_i):
        print("{} looking for queen.".format(self.type))
        current_c = concentration_map[x_i, y_i]
        local_map = concentration_map[x_i-1:x_i+2, y_i-1:y_i+2]

        max_c = np.max(local_map[np.where(local_map > current_c)])
        max_index = list(np.where(local_map == max_c))
        max_indices = [int(i)-1 for i in max_index]

        self.directions_to_queen = { "x" : max_indices[0], "y": max_indices[1] }
        self.found_queen = True

        # Update bias
        bias_x = -1 if self.directions_to_queen["x"] > 0 else 1
        bias_y = -1 if self.directions_to_queen["y"] > 0 else 1

        norm = np.sqrt(bias_x**2 + bias_y**2) + 1e-9

        self.bias_x = bias_x / float(norm)
        self.bias_y = bias_y / float(norm)

class Swarm(object):
    def __init__(self, num_workers, queen_bee_concentration, worker_bee_concentration, worker_bee_threshold, delta_t, delta_x, emission_invervals):

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
            "emission_interval"         : emission_invervals["queen"]
        }

        bees = {"queen" : queen_data}

        sign = lambda : 1 if np.random.uniform() < 0.5 else -1
        new_position = lambda bee_i : ([0.2, 0.25, 0.35, 0.45, 0.55, 0.65][np.random.randint(6)]*sign(), [0.05, 0.1, 0.15, 0.45, 0.55, 0.65][np.random.randint(6)]*sign())

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
            "emission_interval"         : emission_invervals["worker"]
        }

        worker_bees = {"worker_{}".format(i+1) : get_worker_data(i) for i in range(num_workers)}

        for worker_bee, worker_bee_info in worker_bees.items():
            bees[worker_bee] = worker_bee_info

        self.bees = []
        for bee, bee_info in bees.items():
            bee_info["bee_type"] = bee
            bee_info["delta_t"] = delta_t
            bee_info["delta_x"] = delta_x
            print(bee_info)
            self.bees.append(Bee(**bee_info))
