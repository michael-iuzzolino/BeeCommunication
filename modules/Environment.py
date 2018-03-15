import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Bee(object):
    def __init__(self, init_x, init_y, init_concentration, activation_threshold, diffusion_coefficient, dx=0, dy=0, bee_type="worker", init_active=False):
        self.x = init_x
        self.y = init_y
        self.type = bee_type
        self.active = init_active
        self.concentration = init_concentration
        self.init_concentration = init_concentration
        self.diffusion_coefficient = diffusion_coefficient
        self.activation_threshold = activation_threshold

        self.dx = dx
        self.dy = dy

    def get_position(self, t):
        self.x += self.dx * t
        self.y += self.dy * t

        return self.x, self.y

class Environment(object):
    def __init__(self, min_x=-2, max_x=2, start_t=0, finish_t=0.5, num_bees=5):
        self._setup_spatial_information(min_x, max_x)
        self._setup_temporal_information(start_t, finish_t)
        self._create_bees(num_bees)

        self.wind_x = 0
        self.wind_y = 0

        self.bias = 0

    def _setup_spatial_information(self, min_x, max_x, delta_x=0.005):
        self.X1 = np.arange(min_x, max_x+delta_x, delta_x)
        self.X2 = np.arange(min_x, max_x+delta_x, delta_x)
        self.x_grid, self.y_grid = np.meshgrid(self.X1, self.X2)

    def _setup_temporal_information(self, start_t, finish_t, delta_t=0.01):
        finish_t += delta_t
        self.t_array = np.arange(start_t, finish_t, delta_t)

    def _create_bees(self, num_bees, init_concentration=0.1, activation_threshold=0.005, diffusion_coefficient=0.5):
        coords = [[-0.5, 0], [0.5, 0], [-0.5, 1], [-1, -0.5], [0.5, -0.5]]
        queen_data = {
            "init_x"                : 0,
            "init_y"                : 0,
            "init_concentration"    : init_concentration,
            "activation_threshold"  : activation_threshold,
            "diffusion_coefficient" : diffusion_coefficient,
            "init_active"           : True,
            "dx"                    : 0.8,
            "dy"                    : 0.8
        }

        bees = {"queen" : queen_data}

        get_worker_data = lambda bee_i : {
            "init_x"                : coords[bee_i][0],
            "init_y"                : coords[bee_i][1],
            "init_concentration"    : init_concentration,
            "activation_threshold"  : activation_threshold,
            "diffusion_coefficient" : diffusion_coefficient,
            "init_active"           : False,
            "dx"                    : np.random.uniform()*2 - 1,
            "dy"                    : np.random.uniform()*2 - 1
        }

        worker_bees = {"worker_{}".format(i+1) : get_worker_data(i) for i in range(num_bees)}

        for worker_bee, worker_bee_info in worker_bees.items():
            bees[worker_bee] = worker_bee_info

        self.bees = []
        for bee, bee_info in bees.items():
            bee_info["bee_type"] = bee
            self.bees.append(Bee(**bee_info))

    def run(self):

        fig, ax = plt.subplots(1, 1)
        for t_i, t in enumerate(self.t_array, 1):
            concentration = np.zeros([len(self.x_grid), len(self.x_grid)])
            for bee_i, bee in enumerate(self.bees):
                if bee.active:

                    bee_diffusion = bee.diffusion_coefficient
                    current_t = t - bee.concentration
                    bee_x, bee_y = bee.get_position(current_t)
                    term_1 = bee.init_concentration / np.sqrt(current_t)
                    term_2 = (self.x_grid - bee_x - self.wind_x * current_t)**2 + (self.y_grid - bee_y - self.wind_y * current_t)**2
                    current_c = term_1 * np.exp(-(term_2 / float(4 * bee_diffusion * current_t))) + self.bias
                    concentration += current_c



            for bee_i, bee in enumerate(self.bees):
                if not bee.active:
                    current_t = t - bee.concentration
                    bee_x, bee_y = bee.get_position(current_t)
                    test = np.abs(self.X1 - bee_x)

                    try:
                        x_i = int(np.where(np.abs(self.X1 - bee_x) < 1e-4)[0])
                        y_i = int(np.where(np.abs(self.X2 - bee_y) < 1e-4)[0])

                        if concentration[y_i, x_i] >= bee.activation_threshold:
                            bee.active = True
                            bee.concentration = t

                    except:
                        pass

            try:
                sns.heatmap(concentration, cbar=False, cmap="magma", ax=ax)

                for bee in self.bees:
                    if not bee.active:
                        continue
                    bee_x, bee_y = bee.get_position(current_t)
                    try:
                        x_i = int(np.where(np.abs(self.X1 - bee_x) < 1e-4)[0])
                        y_i = int(np.where(np.abs(self.X2 - bee_y) < 1e-4)[0])
                        ax.annotate(bee.type,
                            color='red',
                            xy=(x_i, y_i),
                            xytext=(x_i-80, y_i+125),
                            arrowprops=dict(facecolor='red', shrink=0.05),
                        )
                    except:
                        pass
                plt.pause(0.005)
                plt.cla()
            except:
                pass
