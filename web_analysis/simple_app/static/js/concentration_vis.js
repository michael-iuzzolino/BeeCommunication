// Reference: https://www.patrick-wied.at/static/heatmapjs/

function initConcentrationVis(backend_results) {

    d3.selectAll(".heatmap-canvas, #play_button").remove();

    num_timesteps = EXPERIMENTS_DATA[current_vis_id].timesteps.length;

    // Create heatmap instance
    var config = {
        container: document.getElementById('concentration_div'),
        radius: 10,
        maxOpacity: .7,
        minOpacity: 0,
        blur: .75
    };

    heatmapInstance = h337.create(config);

    // Find max concentration
    // --------------------------------------------------------
    var data = backend_results["concentration_map_history"];
    var values = []
    for (var i=0; i < data.length; i++) {
        values.push(data[i].value);
    }
    max_concentration = d3.max(values) * 2;
    // --------------------------------------------------------

    // heatmap data format
    var data = {
        max   : max_concentration,
        data  : backend_results["concentration_map_history"]
    };

    // for data initialization
    heatmapInstance.setData(data);

    // Label
    var current_time = EXPERIMENTS_DATA[current_vis_id].timesteps[current_timestep]
    d3.select("#concentration_div").append("div").attr("id", "timestep_label").append("label").html("Timestep: " + current_timestep + " -- " + current_time.toFixed(2) + " (s)");

    // Init history timestep marker
    d3.select("#vis_div").select("svg").select("g")
        .append("circle")
        .attr("id", "timestep_marker")
        .attr('r', 8)
        .style("fill", selected_line_color)
        .style("fill-opacity", 0.2)
        .style("stroke", "#000");

    continue_plotting = true;
    update_history_marker();


    // Play button
    PLAYING = false;
    d3.select("#concentration_div")
        .append("input")
        .attr("id", "play_button")
        .attr("type", "button")
        .attr("value", "play")
        .html("play")
        .on("click", function() {
            nextTimestep();

            PLAYING = !PLAYING;

            var color = (PLAYING) ? PLAY_COLOR : STOP_COLOR;
            var text = (PLAYING) ? "Playing" : "Play";
            d3.select(this)
                .attr("value", text)
                .style("background-color", color);
        });
}



function updateConcentrationVis(concentration_results) {
    var bee_heatmap_canvas = document.getElementsByClassName("heatmap-canvas")[0];

    // https://www.patrick-wied.at/static/heatmapjs/
    concentration_map = concentration_results["concentration_map_history"]

    // Find max concentration
    // --------------------------------------------------------
    var data = concentration_map;
    var values = []
    for (var i=0; i < data.length; i++) {
        values.push(data[i].value);
    }
    temp_max_concentration = d3.max(values) * 2;
    if (temp_max_concentration > max_concentration) {
        max_concentration = temp_max_concentration;
    }
    // --------------------------------------------------------

    // heatmap data format
    var data = {
        max   : max_concentration,
        data  : concentration_map
    };

    // for data initialization
    heatmapInstance.setData(data);

    // Label
    var current_time = EXPERIMENTS_DATA[current_vis_id].timesteps[current_timestep]
    d3.select("#timestep_label").select("label").html("Timestep: " + current_timestep + " -- " + current_time.toFixed(2) + " (s)");
}
