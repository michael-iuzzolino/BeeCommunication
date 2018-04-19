// Reference: https://www.patrick-wied.at/static/heatmapjs/


function updateHeatmapInstance() {

    // Create heatmap instance
    var new_config = {
        backgroundColor : SELECTED_COLORMAP.background,
        gradient        : SELECTED_COLORMAP.gradient
    };

    heatmapInstance.configure(new_config);
}

function initConcentrationVis(backend_results) {

    d3.selectAll(".heatmap-canvas, #play_button").remove();

    num_timesteps = EXPERIMENTS_DATA[current_vis_id].timesteps.length;


    // Create heatmap instance
    var config = {
        container       : document.getElementById('concentration_div'),
        radius          : 10,
        maxOpacity      : 0.7,
        minOpacity      : 0,
        blur            : 0.75,
        backgroundColor : SELECTED_COLORMAP.background,
        gradient        : SELECTED_COLORMAP.gradient
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

    // Setup colormap controls
    initColorMapControls();

}

function initColorMapControls() {

    var colormap_controls_div = d3.select("body").append("div").attr("id", "colormap_controls_div");

    // Color Map Select
    var color_form = colormap_controls_div.append("div").attr('id', "color_form_div").append("label").html("Colormap")
        .append("form")
        .attr("id", "color_form");

    var color_select = color_form.append("select")
        .on("change", function() {
            var optionSelected = $("option:selected", this);
            var valueSelected = this.value;
            SELECTED_COLORMAP_KEY = valueSelected;
            SELECTED_COLORMAP = COLORMAPS[SELECTED_COLORMAP_KEY]
            updateHeatmapInstance();
            updateBeeImages();
            // updateSliders();
        });

    color_select.selectAll("option")
        .data(Object.keys(COLORMAPS)).enter()
        .append("option")
        .attr("value", function(d) {
            return d;
        })
        .text(function(d) {
            return d;
        });

    // // Gradient options
    // var gradient_options = Object.keys(SELECTED_COLORMAP.gradient);
    //
    // var slider_divs = colormap_controls_div.selectAll("div.sliders")
    //     .data(gradient_options).enter()
    //     .append("div")
    //     .attr("class", "sliders")
    //     .attr("id", function(i) { return "color_" + i + "_div"; })
    //
    // slider_divs.append("label")
    //     .attr("for", function(d, i) {
    //         return "color_" + i + "_slider";
    //     })
    //     .attr('id', function(d, i) {
    //         return "color_" + i + "_label";
    //     })
    //     .attr("class", "color_slider_labels")
    //     .html(function(d) {
    //         return parseInt(parseFloat(d) * 100) + "%";
    //     });
    //
    // slider_divs.append("input")
    //     .attr("type", "range")
    //     .attr('id', function(d, i) {
    //         return "color_" + i + "_slider";
    //     })
    //     .attr("class", "color_sliders")
    //     .attr('value', function(d) {
    //         return parseFloat(d)*100;
    //     })
    //     .attr("min", 0)
    //     .attr("max", 100)
    //     .on("input", function(d, i) {
    //         // Constrain selected value
    //         var gradient_values = Object.keys(SELECTED_COLORMAP.gradient);
    //         var this_val = "" + this.value;
    //         if (gradient_values.includes(this_val)) {
    //             return;
    //         }
    //         var new_label = parseFloat(+this.value) + "%";
    //         d3.select("#color_" + i +"_label").html(new_label);
    //         updateColorMapGradient(this.id, +this.value);
    //         updateHeatmapInstance();
    //     });
}

function updateSliders() {
    var gradient_options = Object.keys(SELECTED_COLORMAP.gradient);
    d3.selectAll(".color_sliders")
    .attr('value', function(d, i) {
        return parseFloat(gradient_options[i]) * 100;
    });

    d3.selectAll(".color_slider_labels")
    .html(function(d, i) {
        return parseInt(parseFloat(gradient_options[i]) * 100) + "%";
    });

}

function updateColorMapGradient(id, new_key_raw) {

    var index = id.split("_")[1];
    var old_key = Object.keys(SELECTED_COLORMAP.gradient)[index];
    var old_val = Object.values(SELECTED_COLORMAP.gradient)[index];

    var new_key = "" + new_key_raw / 100;
    delete SELECTED_COLORMAP.gradient[old_key];
    SELECTED_COLORMAP.gradient[new_key] = old_val;
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
