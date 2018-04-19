var EXPERIMENTS_DATA;
var EXPERIMENT_FOLDERS;
var SELECTED_EXPERIMENT_FOLDER;
var PLAYBACK_RATE = 500;
var COLORS = ["#ffcc00", "#cc66ff"];
var plotted_experiment_ids = [];
var xScale, yScale;
var svg;
var xScale, yScale, colorScale;
var margin, width, height;
var line;
var current_timestep = 0;
var num_timesteps;
var current_vis_id;
var max_concentration;

var min_spatial_x;
var max_spatial_x;
var PLAYING = false;
var PLAY_COLOR = "#ccff99";
var STOP_COLOR = "#ffffff";
var distance_summary_plot_height = 300;

var heatmap_size = 600;

var beeXScale, beeYScale;
var heatmapInstance;
var selected_id;
var continue_plotting = false;
var selected_line_color = "#00e600";
var mouseover_line_color = "#0000ff";

var worker_bee_icon_size = 25;
var queen_bee_icon_size = 55;

var bee_ids = [];

var beeBarXScale, beeBarYScale;
var BEE_DISTANCES = {};
var bee_bar_width = 5;
var bee_bar_graph_height = 300;
var bee_bar_graph_width = 700;
var DEFAULT_BAR_COLOR = "#eee6ff";
var BEE_BAR_SELECT_COLOR = "#ff4da6";
var BEE_LINE_COLOR = "#5c5cd6";

var BEE_CONCENTRATION_HISTORIES = {};
var beeConcentrationXScale, beeConcentrationYScale;


var COLORMAPS = {
    "rwb" : {
        "background"    : 'rgba(0,0,0,.95)',
        "gradient"      : {
            // enter n keys between 0 and 1 here
            // for gradient color customization
            '.4'  : 'blue',
            '.75' : 'red',
            '.95' : 'white'
        },
        "queen"         : "static/icons/queen_bee_white.png",
        "worker"        : "static/icons/worker_bee_white.png",
        "worker_active" : "static/icons/worker_bee_active.png"
    },
    "gyr" : {
        "background"    : 'rgba(255,255,255,.95)',
        "gradient"      : {
            // enter n keys between 0 and 1 here
            // for gradient color customization
            '.4'  : 'green',
            '.75' : '#ffeb99',
            '.95' : '#ff0000'
        },
        "queen"         : "static/icons/queen_bee.png",
        "worker"        : "static/icons/worker_bee.png",
        "worker_active" : "static/icons/worker_bee_active.png"
    }
}

var SELECTED_COLORMAP_KEY = Object.keys(COLORMAPS)[0];
var SELECTED_COLORMAP = COLORMAPS[SELECTED_COLORMAP_KEY];
