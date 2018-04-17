
function mouseover_line(this_id) {
    d3.select("#"+this_id).moveToFront();

    if (selected_id === this_id) {
        return;
    }

    d3.select("#"+this_id).style('stroke', mouseover_line_color);

    var select = document.getElementById("exeriment_selection");
    for (var i=0; i < select.options.length; i++){
        if (select.options[i].value === this_id.split("_")[1]){
            select.options[i].selected = true;
        }
        else {
            select.options[i].selected = false;
        }
    }
}

function mouseout_line(this_id) {
    if (selected_id === this_id) {
        return;
    }
    var plot_index = this_id.split("_")[1];
    d3.select("#"+this_id).style('stroke', colorScale(plot_index));

    var select = document.getElementById("exeriment_selection");
    for (var i=0; i < select.options.length; i++){
        if (selected_id && select.options[i].value === selected_id.split("_")[1]){
            select.options[i].selected = true;
        }
        else {
            select.options[i].selected = false;
        }
    }
}



function click_line(this_id) {

    // Lower Opacity on all other lines
    for (var i=0; i < plotted_experiment_ids.length; i++) {
        var plot_i = plotted_experiment_ids[i];
        if (plot_i === this_id) {
            continue;
        }
        d3.select("#"+plot_i).style("stroke-width", "2px").style("opacity", 0.4);
    }

    reset_line_style();

    continue_plotting = false;
    var self = d3.select("#"+this_id);

    self.moveToFront();
    if (selected_id === this_id) {
        d3.selectAll(".heatmap-canvas, #bee_svg, #timestep_label, #timestep_marker")
            .transition()
            .duration(500)
            .style("opacity", 0.0);

        setTimeout(function() {
            d3.selectAll(".heatmap-canvas, #bee_svg, #timestep_label, #timestep_marker").remove();
            selected_id = undefined;
            current_vis_id = undefined;

            var select = document.getElementById("exeriment_selection");
            for (var i=0; i < select.options.length; i++){
                select.options[i].selected = false;
            }

            // Normalize Opacity on all other lines
            for (var i=0; i < plotted_experiment_ids.length; i++) {
                var plot_i = plotted_experiment_ids[i];
                d3.select("#"+plot_i).style("stroke-width", "4px").style("opacity", 1.0);
            }
        }, 650);
    }
    else if (selected_id === undefined) {

        // Highlight this one
        selected_id = this_id;
        current_vis_id = this_id;

        self.transition().duration(500)
            .style('stroke', selected_line_color)
            .style("stroke-width", "6px");

        var select = document.getElementById("exeriment_selection");
        for (var i=0; i < select.options.length; i++){
            if (select.options[i].value == this_id.split("_")[1]){
                select.options[i].selected = true;
            }
            else {
                select.options[i].selected = false;
            }
        }

        load_experiment_data(this_id, 0);
    }
    else {
        var selection_ids = ".heatmap-canvas, #bee_svg, #timestep_label, #timestep_marker";
        d3.selectAll(selection_ids)
            .transition()
            .duration(500)
            .style("opacity", 0.0);

        setTimeout(function() {
            d3.selectAll(selection_ids).remove();

            // Highlight this one
            selected_id = this_id;
            current_vis_id = this_id;

            // Normalize Opacity on all other lines
            for (var i=0; i < plotted_experiment_ids.length; i++) {
                var plot_id = plotted_experiment_ids[i];
                var opacity = (plot_id === this_id) ? 1.0 : 0.4;
                var stroke_width = (plot_id === this_id) ? "6px" : "2px";
                var stroke = (plot_id === this_id) ? selected_line_color : colorScale(i);
                d3.select("#"+plot_id)
                    .style("stroke", stroke)
                    .style("stroke-width", stroke_width)
                    .style("opacity", opacity);
            }

            load_experiment_data(this_id, 0);
        }, 650);
    }


}
