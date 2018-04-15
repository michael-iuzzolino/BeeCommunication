var EXPERIMENTS_DATA;
var SELECTED_EXPERIMENTS = [];
var COLORS = ["#b3b3ff", "#ffcc66"];
var plotted_experiment_ids = [];
var xScale, yScale;
var max_distance;
var svg;
var xScale, yScale, colorScale;
var margin, width, height;
var line;
var current_timestep = 0;
var num_timesteps = 5;
var current_vis_id;

function updateConcentrationVis(concentration_results) {
    d3.select("#concentration_div").selectAll("*").remove();

    // https://www.patrick-wied.at/static/heatmapjs/
    concentration_map = concentration_results["concentration_map_history"]

    var heatmap_container = document.querySelector('#concentration_div');
    // Initialize the size (reshape later with css)
    heatmap_container.style.height =  800 + "px";
    heatmap_container.style.width =  800 + "px";

    // var heatmap_container = document.querySelector('body');

    var heatmapInstance = h337.create({
      // only container is required, the rest will be defaults
      container: heatmap_container
    });

    max_concentration = 0
    concentration_map.forEach(function(d) {
        if (d.value > max_concentration) {
            max_concentration = d.value
        }
    });

    // heatmap data format
    var data = {
        max   : max_concentration,
        data  : concentration_map
    };

    // for data initialization
    heatmapInstance.setData(data);
}

function nextTimestep() {
    var sendDict = {
        "experiment_id" : current_vis_id,
        "timestep"      : current_timestep
    }

    $.ajax({
        url: "/load_experiment",
        method: "POST",
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(sendDict),
        success: function(python_result){
            var concentration_results = python_result;
            updateConcentrationVis(concentration_results);

            current_timestep++;
            current_timestep %= num_timesteps;
            nextTimestep();
        }
    });
}

function initConcentrationVis(concentration_results) {

    d3.select("#concentration_div").selectAll("*").remove();

    // https://www.patrick-wied.at/static/heatmapjs/
    concentration_map = concentration_results["concentration_map_history"]

    var heatmap_container = document.querySelector('#concentration_div');
    // Initialize the size (reshape later with css)
    heatmap_container.style.height =  800 + "px";
    heatmap_container.style.width =  800 + "px";

    // var heatmap_container = document.querySelector('body');

    var heatmapInstance = h337.create({
      // only container is required, the rest will be defaults
      container: heatmap_container
    });

    max_concentration = 0
    concentration_map.forEach(function(d) {
        if (d.value > max_concentration) {
            max_concentration = d.value
        }
    });

    // heatmap data format
    var data = {
        max   : max_concentration,
        data  : concentration_map
    };

    // for data initialization
    heatmapInstance.setData(data);

    // Play button
    d3.select("#vises")
        .append("input")
        .attr("id", "play_button")
        .attr("type", "button")
        .attr("value", "play")
        .html("play")
        .on("click", function() {
            nextTimestep();
        });
}

function load_experiment_data(experiment_id, timestep) {

    current_vis_id = experiment_id;

    var sendDict = {
        "experiment_id" : current_vis_id,
        "timestep"      : timestep
    }


    $.ajax({
        url: "/load_experiment",
        method: "POST",
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(sendDict),
        success: function(python_result){
            var concentration_results = python_result;
            initConcentrationVis(concentration_results);
            current_timestep++;
        }
    });

}

function plot_experiment_results(experiment_data, index) {
    var experiment_plot_id = "experiment_" + index;

    if (plotted_experiment_ids.includes(experiment_plot_id)) {
        return;
    }

    var timesteps = experiment_data.timesteps;
    var average_distances = experiment_data.averages;
    var new_max_distance = d3.max(average_distances);

    if (new_max_distance > max_distance) {
        yScale.domain([0, new_max_distance]);
        svg.select(".y_axis")
            .transition()
            .call(d3.axisLeft(yScale));

        for (var i=0; i < plotted_experiment_ids.length; i++) {
            var previous_plot_id = plotted_experiment_ids[i];
            d3.select("#"+previous_plot_id).transition().attr("d", line);
        }

        max_distance = new_max_distance;
    }

    var dataset = d3.range(timesteps.length).map(function(d, i) {
        var data_point = {
            "x" : timesteps[i],
            "y" : average_distances[i]
        }
        return data_point;
    });

    plotted_experiment_ids.push(experiment_plot_id);

    svg.append("path")
        .datum(dataset)
        .attr("class", "line")
        .attr('id', experiment_plot_id)
        .attr("d", line)
        .style("stroke", function() {
            return colorScale(index);
        })
        .on("mouseover", function() {
            d3.select(this).style('stroke', "red");
        })
        .on("mouseout", function() {
            var plot_index = this.id.split("_")[1];
            d3.select(this).style('stroke', colorScale(plot_index));
        })
        .on("click", function() {
            load_experiment_data(this.id, 0);
        })
        .on("contextmenu", function() {
            d3.select(this).remove();
            plotted_experiment_ids = remove_element_from_list(plotted_experiment_ids, this.id)
        });
}

function remove_element_from_list(list, ele) {
    new_list = []
    for (var i=0; i < list.length; i++) {
        if (list[i] != ele) {
            new_list.push(list[i]);
        }
    }
    return new_list;
}

function initVisPlot(experiment_data) {

    var timesteps = experiment_data.timesteps;
    var max_timestep = d3.max(timesteps);

    var vis_div = d3.select('#vis_div').node().getBoundingClientRect();

    var div_window_width = vis_div.width / 2;
    var div_window_height = 300;
    margin = {top: 50, right: 50, bottom: 50, left: 50}
    width = div_window_width - margin.left - margin.right // Use the window's width
    height = div_window_height - margin.top - margin.bottom; // Use the window's height


    xScale = d3.scaleLinear()
        .domain([0, max_timestep]) // input
        .range([0, width]); // output

    colorScale = d3.scaleLinear()
        .domain([0, Object.keys(EXPERIMENTS_DATA).length])
        .range(COLORS);

    var average_distances = experiment_data.averages;
    max_distance = d3.max(average_distances);

    yScale = d3.scaleLinear()
        .domain([0, max_distance]) // input
        .range([height, 0]); // output

    svg = d3.select("#vis_div").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x_axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale).ticks(5)); // Create an axis component with d3.axisBottom

    svg.append("g")
        .attr("class", "y_axis")
        .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

    line = d3.line()
        .x(function(d, i) { return xScale(d.x); }) // set the x values for the line generator
        .y(function(d) { return yScale(d.y); }) // set the y values for the line generator
        .curve(d3.curveMonotoneX) // apply smoothing to the line
}

function setup_experiment_selection() {
    var experiment_keys = Object.keys(EXPERIMENTS_DATA);

    d3.select("#exeriment_selection").on("change", function(d, i) {
        var selected_options = this.selectedOptions;

        for (var i=0; i < selected_options.length; i++) {
            var ele = selected_options[i];
            var index = ele.value;
            var selected_experiment = EXPERIMENTS_DATA[experiment_keys[index]];

            // Check if selected experiment already in selected experiments
            SELECTED_EXPERIMENTS.push(selected_experiment);

            plot_experiment_results(selected_experiment, index);
        }
    });

    d3.select("#exeriment_selection").selectAll("option")
        .data(experiment_keys).enter()
        .append("option")
        .attr("value", function(d, i) {
            return i;
        })
        .text(function(d) {
            var params = EXPERIMENTS_DATA[d].params;
            var diffusion_coefficient = params.diffusion_coefficient;
            var queen_bee_concentration = params.queen_bee_concentration;
            var worker_bee_concentration = params.worker_bee_concentration;
            return "D_C: " + diffusion_coefficient + " -- Q_C: " + queen_bee_concentration + " -- W_C: " + worker_bee_concentration;
        });
}
function callPythonBackend() {
    $.ajax({
        url: "/load_data",
        method: "POST",
        contentType: 'application/json',
        success: function(python_result){
            EXPERIMENTS_DATA = python_result["results"];
            setup_experiment_selection();
            initVisPlot(EXPERIMENTS_DATA["experiment_1"]);
        }
    });
}

function initializerUserInterface() {
    var body = d3.select("body");
    callPythonBackend();
}

$(function() {
    initializerUserInterface();
});
