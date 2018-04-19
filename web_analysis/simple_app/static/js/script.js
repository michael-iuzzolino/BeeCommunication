


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
            updateConcentrationVis(python_result);
            updateBeeLayer(python_result)
            current_timestep++;
            current_timestep %= num_timesteps;

            if (continue_plotting) {
                setTimeout(function() {
                    update_history_marker();
                    nextTimestep();
                }, PLAYBACK_RATE);
            }
        }
    });
}





function load_experiment_data(experiment_id, timestep) {

    current_timestep = 0;
    d3.select(".heatmap-canvas").remove();


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
            initConcentrationVis(python_result);
            initBeeLayer(python_result);
            current_timestep++;

            d3.selectAll(".heatmap-canvas, #bee_svg")
                .transition().duration(750)
                .style("opacity", 1.0);
        }
    });

}

function reset_line_style() {
    // Clear all others
    for (var i=0; i < plotted_experiment_ids.length; i++) {
        d3.select("#"+plotted_experiment_ids[i])
            .transition().duration(500)
            .style("stroke", function() {
                var plot_index = plotted_experiment_ids[i].split("_")[1];
                return colorScale(plot_index);
            })
            .style("stroke-width", function() {
                return (selected_id) ? "4px" : "2px";
            });
    }
}

function removeVisualizations() {
    console.log("HERE");
    var remove_tags = ".heatmap-canvas, #bee_svg, #timestep_label, #timestep_marker, #bee_distance_svg, #play_button";
    d3.selectAll(remove_tags)
        .transition()
        .duration(750)
        .style("opacity", 0.0);

    setTimeout(function() {
        d3.selectAll(remove_tags).remove();
        selected_id = undefined;
        current_vis_id = undefined;
    }, 800);
}

function setup_experiment_folder_selection() {

    d3.select("#exeriment_folder_selection")
        .on("change", function(d) {
            var optionSelected = $("option:selected", this);
            var valueSelected = this.value;
            SELECTED_EXPERIMENT_FOLDER = valueSelected;

            removeVisualizations();

            // Ajax call to load data for setup_experiment_selection()
            loadExperimentFolderData();
        });

    d3.select("#exeriment_folder_selection").selectAll("option")
        .data(EXPERIMENT_FOLDERS).enter()
        .append("option")
        .attr("class", "option_text")
        .attr("value", function(d) {
            return d;
        })
        .text(function(d) {
            var last_index = (d.split("/")).length - 1;
            return d.split("/")[last_index];
        });
}

function setup_experiment_selection() {

    d3.select("#save_plot_button").remove();

    var experiment_keys = Object.keys(EXPERIMENTS_DATA);

    d3.select("#exeriment_selection")
        .on("change", function(d, i) {
            var optionSelected = $("option:selected", this);
            var valueSelected = this.value;

            var this_id = "experiment_"+valueSelected;
            click_line(this_id);
        });

    d3.select("#exeriment_selection").selectAll("option")
        .data(experiment_keys).enter()
        .append("option")
        .attr("class", "option_text")
        .attr("value", function(d, i) {
            return i;
        })
        .text(function(d) {
            var params = EXPERIMENTS_DATA[d].params;
            var diffusion_coefficient = params.diffusion_coefficient;
            var queen_bee_concentration = params.queen_bee_concentration;
            var worker_bee_concentration = params.worker_bee_concentration;
            var worker_bee_threshold = params.worker_bee_threshold;
            return diffusion_coefficient.toFixed(2) + " " + queen_bee_concentration.toFixed(2) + " " + worker_bee_concentration.toFixed(3) + " " + worker_bee_threshold.toFixed(3);
        })
        .on("mouseover", function(d) {
            var this_id = "experiment_"+this.value;
            mouseover_line(this_id);
        })
        .on("mouseout", function(d) {
            var this_id = "experiment_"+this.value;
            mouseout_line(this_id);
        })
        .on("click", function(d) {
            var this_id = "experiment_"+this.value;
            click_line(this_id);
        });

    // Button to save plot
    d3.select("#params_div").append("input")
        .attr("type", "button")
        .attr("id", "save_plot_button")
        .attr("value", "Save Selected Plot as CSV")
        .on("click", function() {
            if (current_vis_id !== undefined) {
                d3.select(this).transition().duration(250)
                    .attr("value", "Saving " + current_vis_id.replace("_", " ") + " ...")
                    .style("background-color", "#ffeecc");

                setTimeout(function() {
                    save_plot();
                }, 1000);

            }
        });
}


function getExperimentFolders() {
    $.ajax({
        url: "/init_experiment_folders",
        method: "POST",
        contentType: 'application/json',
        success: function(python_result){
            EXPERIMENT_FOLDERS = python_result["experiment_folders"];
            SELECTED_EXPERIMENT_FOLDER = EXPERIMENT_FOLDERS[0];

            setup_experiment_folder_selection();

            // Initial setup
            loadExperimentFolderData();
        }
    });
}

function setParams(params) {
    min_spatial_x = params["min_x"];
    max_spatial_x = params["max_x"];
}

function loadExperimentFolderData() {
    var sendDict = {
        "folder_path" : SELECTED_EXPERIMENT_FOLDER
    }

    $.ajax({
        url: "/load_data",
        method: "POST",
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(sendDict),
        success: function(python_result){
            EXPERIMENTS_DATA = python_result["results"];
            setParams(python_result["params"])
            setup_experiment_selection();
            var init_experiment = EXPERIMENTS_DATA[Object.keys(EXPERIMENTS_DATA)[0]];
            initVisPlot(init_experiment);
        }
    });
}

function initializerUserInterface() {
    var body = d3.select("body");
    getExperimentFolders();
}

$(function() {
    initializerUserInterface();
});
