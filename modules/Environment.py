import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from modules.Bees import Swarm

class Environment(object):
    def __init__(self, bees, diffusion_coefficient, spatiotemporal_parameters):
        self._setup_spatial_information(**spatiotemporal_parameters["spatial"])
        self._setup_temporal_information(**spatiotemporal_parameters["temporal"])
        self.bees = bees

        self.diffusion_coefficient = diffusion_coefficient

    def _setup_spatial_information(self, min_x, max_x, delta_x):
        self.X1 = np.arange(min_x, max_x+delta_x, delta_x)
        self.X2 = np.arange(min_x, max_x+delta_x, delta_x)
        self.x_grid, self.y_grid = np.meshgrid(self.X1, self.X2)

    def _setup_temporal_information(self, start_t, finish_t, delta_t):
        self.t_array = np.arange(start_t, finish_t+delta_t, delta_t)
        self.t_array = self.t_array[1:]

    def run(self):
        fig, ax = plt.subplots(1, 1)

        for enironment_timestep_i, environment_timestep in enumerate(self.t_array):
            print("t_i: {}, {}".format(enironment_timestep_i, environment_timestep))
            environment_concentration_map = np.zeros([len(self.x_grid), len(self.x_grid)])
            for bee_i, bee in enumerate(self.bees):
                # Update bee's movement and pheromone emission

                bee.update()

                if bee.pheromone_active:
                    bee_info = bee.measure()
                    term_1 = bee.concentration / np.sqrt(bee_info["emission_t"] + 1e-9)
                    term_2 = (self.x_grid - bee_info["x"] - bee_info["bias_x"] * bee_info["emission_t"])**2 + (self.y_grid - bee_info["y"] - bee_info["bias_y"] * bee_info["emission_t"])**2
                    current_c = term_1 * np.exp(-(term_2 / float(4 * self.diffusion_coefficient * bee_info["emission_t"])))
                    environment_concentration_map += current_c

            for bee_i, bee in enumerate(self.bees):
                bee_info = bee.measure()
                try:
                    x_i = int(np.where(np.abs(self.X1 - bee_info["x"]) < 1e-4)[0])
                    y_i = int(np.where(np.abs(self.X2 - bee_info["y"]) < 1e-4)[0])
                    bee.sense_environment(environment_concentration_map, x_i, y_i)
                except:
                    pass


            for bee_i, bee in enumerate(self.bees):
                if not bee.pheromone_active:
                    bee_info = bee.measure()

                    try:
                        x_i = int(np.where(np.abs(self.X1 - bee_info["x"]) < 1e-4)[0])
                        y_i = int(np.where(np.abs(self.X2 - bee_info["y"]) < 1e-4)[0])


                        # NOTE: WORKER BEE ACTIVATED HERE
                        if environment_concentration_map[y_i, x_i] >= bee.activation_threshold:
                            print("{} Bee movement stopped. Pheromone starting.".format(bee.type))
                            bee.find_queen(environment_concentration_map, x_i, y_i)
                            bee.pheromone_active = True
                            bee.movement_active = False
                            bee.concentration = t
                    except:
                        pass

            try:
                print(environment_concentration_map.flatten())
                MIN = np.min(environment_concentration_map.flatten())
                MAX = np.max(environment_concentration_map.flatten())
                print("MIN {}, MAX {}".format(MIN, MAX))
                sns.heatmap(environment_concentration_map, cbar=False, cmap="magma", ax=ax, vmin=0, vmax=0.5)
                plt.title("t: {}".format(environment_timestep))
                for bee_i, bee in enumerate(self.bees):
                    # if not bee.active or not bee.type == "queen":
                    #     continue
                    bee_info = bee.measure()

                    x_i = int(np.where(np.abs(self.X1 - bee_info["x"]) < 1e-4)[0])
                    y_i = int(np.where(np.abs(self.X2 - bee_info["y"]) < 1e-4)[0])
                    bee_color = "green" if bee.movement_active else "red"
                    bee_size = 30 if bee.movement_active else 20
                    arrow_shrink = 0.05 if bee.movement_active else 0.005
                    bee_name = bee.type.replace("_", " ").capitalize()
                    bee_label = "{} Active".format(bee_name) if bee.pheromone_active else "{} Inactive".format(bee_name)
                    ax.scatter(x_i, y_i, s=bee_size, color=bee_color)

                    # Bee annotate
                    ax.annotate(bee_name,
                        color=bee_color,
                        xy=(x_i, y_i),
                        xytext=(x_i, y_i)
                    )

                    # Bee legend annotate
                    ax.annotate("{}. {}".format(bee_i+1, bee_label),
                        color=bee_color,
                        xy=(50, 100),
                        xytext=(50, bee_i*40 +40),
                        # arrowprops=dict(facecolor=bee_color, shrink=arrow_shrink),
                    )
                plt.pause(0.005)
                plt.cla()
            except KeyboardInterrupt:
                exit(0)
            # except Exception as e:
            #     print("ERROR LINE 80")
            #     print(e)
