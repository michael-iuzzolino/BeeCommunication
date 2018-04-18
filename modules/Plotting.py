import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import ListedColormap

class Plotter(object):
    def __init__(self):
        pass

    def _setup_plots(self, plot_params):
        self.plot_save_dir = plot_params['save_dir']
        self.plot_bee = "worker_1"
        self.full_event_keys = ""

        fig = plt.figure(figsize=(9, 7))
        self.fig = fig

        grid = plt.GridSpec(7, 5, wspace=0.4, hspace=0.3)
        self.concentration_map = fig.add_subplot(grid[0:3, 0:3])
        self.information_plot = fig.add_subplot(grid[:4, 3:5])
        self.distance_plot = fig.add_subplot(grid[3:4, :3])
        self.concentration_history_plot = fig.add_subplot(grid[5:, 3:])
        self.distance_history_plot = fig.add_subplot(grid[5:, :2])

        cmaps = ["magma", "plasma", "viridis", sns.cubehelix_palette(20)]
        self.concentration_cmap = cmaps[0]

        # Switch bee profile
        # ----------------------------------------------------------------------
        def onpress(event):
            valid_events = ['{}'.format(i) for i in range(10)]
            if event.key in valid_events or event.key == 'enter':
                if event.key == 'enter':
                    if int(self.full_event_keys) > len(self.bees)-1:
                        self.full_event_keys = ""
                        print("Invalid Key Entry!")
                        return
                    self.concentration_history_plot.cla()
                    self.plot_bee = "worker_{}".format(self.full_event_keys)
                    self.full_event_keys = ""
                else:
                    self.full_event_keys += event.key

        self.fig.canvas.mpl_connect('key_press_event', onpress)
        # ----------------------------------------------------------------------

    def imscatter(self, x, y, image, ax=None, zoom=1):
        try:
            image = plt.imread(image)
        except TypeError:
            # Likely already an array...
            pass

        im = OffsetImage(image, zoom=zoom)
        x, y = np.atleast_1d(x, y)
        artists = []
        for x0, y0 in zip(x, y):
            ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
            artists.append(ax.add_artist(ab))
        ax.update_datalim(np.column_stack([x, y]))
        ax.autoscale()
        return artists

    def display_environment_map(self, concentration_map, time_i, timestep, init):
        if init:
            self.vmax = np.max(concentration_map.flatten())

        # Environment concentration heatmap
        sns.heatmap(concentration_map, cbar=False, cmap=self.concentration_cmap, ax=self.concentration_map, vmin=0, vmax=self.vmax, xticklabels=0, yticklabels=0)

        self.information_plot.text(0.1, 0.95, "  Bee          Pheromone Activity", size=10)
        for bee_i, bee in enumerate(self.bees):
            x_i, y_i = self._get_global_position(bee.measure())

            bee_color = "red" if bee.random_movement_active else "green" if not bee.queen_directed_movement else "blue"
            bee_size = 30 if bee.random_movement_active else 20 if not bee.queen_directed_movement else 30

            bee_name = bee.type.replace("_", " ").capitalize()
            bee_label = "Active" if bee.pheromone_active else "Inactive"

            # Plot position
            if self.display_real_img:
                self.imscatter(x_i, y_i, bee.img, zoom=0.1, ax=self.concentration_map)
            else:
                self.concentration_map.scatter(x_i, y_i, s=bee_size, color=bee_color)

            # Bee annotate
            if len(self.bees) < 14:
                self.concentration_map.annotate(bee_name,
                    color=bee_color,
                    xy=(x_i, y_i),
                    xytext=(x_i, y_i)
                )

            bee_string = "{}. {:10s}{:5s}{}".format(bee_i+1, bee_name, "", bee_label)
            self.information_plot.text(0.1, bee_i*-0.05+0.9, bee_string, color=bee_color, size=10)
            self.information_plot.set_xticks([])
            self.information_plot.set_yticks([])

            if bee.type == self.plot_bee:
                self.concentration_history_plot.plot(bee.concentration_history, 'cyan')
                self.concentration_history_plot.set_title("{}".format(bee_name))
                self.concentration_history_plot.set(xlabel='Timesteps', ylabel='Pheromone \nConcentration')


        # Distance Bar Plot
        # ----------------------------------------------------------------------------------------
        bee_distance_plot = sns.barplot(x="bees", y="bee_distances", data=self.bee_distance_df, color="salmon", ax=self.distance_plot)
        self.distance_plot.set_ylim(0, self.max_distance_from_center)
        for item in bee_distance_plot.get_xticklabels():
            item.set_rotation(45)

        self.concentration_map.set_title("Timestep {}: {}s".format(time_i, timestep))
        self.distance_plot.set(xlabel="", ylabel='Distance to Queen')
        # ----------------------------------------------------------------------------------------


        # Plot average distance to queen
        # ----------------------------------------------------------------------------------------
        ave_distances = [ele["average"] for ele in self.measurements["distance_from_queen"]]
        self.distance_history_plot.plot(ave_distances)
        self.distance_history_plot.set_title("Average Distance from Queen")
        self.distance_history_plot.set(xlabel='Timestep', ylabel='Average Distance')
        # ----------------------------------------------------------------------------------------

        plt.savefig("{}/environment_timestep_{}".format(self.plot_save_dir, time_i))

        if self.real_time_visualization:
            plt.pause(0.005)

        self.concentration_map.cla()
        self.information_plot.cla()
        self.distance_plot.cla()
