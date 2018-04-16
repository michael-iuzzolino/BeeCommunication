


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



function setup_experiment_selection() {
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
            return diffusion_coefficient.toFixed(2) + " " + queen_bee_concentration.toFixed(2) + " " + worker_bee_concentration.toFixed(3);
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
