var bee_click_tracker = {};

function initBeeLayer(backend_results) {
    var init_bee_positions = backend_results["bees_position_history"];
    BEE_CONCENTRATION_HISTORIES = backend_results["bee_concentration_history"];

    var init_bee_data = [];
    var x_values = [];
    var y_values = [];
    for (var bee_key in init_bee_positions) {
        bee_i = init_bee_positions[bee_key];

        init_bee_data.push({
            "bee_id"                : bee_key,
            "x"                     : bee_i.x,
            "y"                     : bee_i.y,
            "found_queen_direction" : bee_i.found_queen_direction
        });
        x_values.push(bee_i.x);
        y_values.push(bee_i.y);

        BEE_DISTANCES[bee_key] = Math.sqrt((bee_i.x)**2 + (bee_i.y)**2);

        // Init list of bees
        bee_click_tracker[bee_key] = false;
    }

    // Init bee distance vis
    initBeeDistanceVis();

    // Init individual bee concentration history
    // init_bee_concentration_history_vis();

    // Init tooltip
    d3.select('body').append("div").attr("id", "bee_name_tooltip_div");
    d3.select('body').append("div").attr("id", "distance_tooltip_div");

    // Create SVG overlay
    var bee_svg = d3.select("#concentration_div").append("svg")
        .attr("id", "bee_svg")
        .attr("height", heatmap_size)
        .attr("width", heatmap_size);

    beeXScale = d3.scaleLinear()
        .domain([min_spatial_x, max_spatial_x])
        .range([0, heatmap_size]);

    beeYScale = d3.scaleLinear()
        .domain([min_spatial_x, max_spatial_x])
        .range([0, heatmap_size]);

    bee_svg.selectAll('image.bees')
        .data(init_bee_data).enter()
        .append('image')
        .attr("class", "bees")
        .attr("id", function(d) {
            return d.bee_id;
        })
        .attr("xlink:href", function(d) {
            var worker_path = (d.found_queen_direction) ? SELECTED_COLORMAP.worker_active : SELECTED_COLORMAP.worker
            return (d.bee_id.split("_")[0] === "worker") ? worker_path : SELECTED_COLORMAP.queen;
        })
        .attr("x", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeXScale(d.x) - icon_size/2.0;
        })
        .attr("y", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeYScale(d.y) - icon_size/2.0;
        })
        .attr("width", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return icon_size;
        })
        .attr("height", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return icon_size;
        })
        .on("mouseover", function(d) {
            var bee_name_tooltip_div = d3.select("#bee_name_tooltip_div");
            var distance_tooltip_div = d3.select("#distance_tooltip_div");
            bee_name_tooltip_div.transition()
                .duration(200)
                .style("opacity", .9);

            bee_name_tooltip_div.html(function() {
                    return d.bee_id.replace("_", " ");
                })
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");

            distance_tooltip_div.transition()
                .duration(200)
                .style("opacity", .9);

            distance_tooltip_div.html(function() {
                    var distance_to_queen = BEE_DISTANCES[d.bee_id];
                    return distance_to_queen.toFixed(4);
                })
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY) + "px");
        })
        .on("mouseout", function(d) {
            var bee_name_tooltip_div = d3.select("#bee_name_tooltip_div");
            var distance_tooltip_div = d3.select("#distance_tooltip_div");
            bee_name_tooltip_div.transition()
                .duration(200)
                .style("opacity", 0.0);

            distance_tooltip_div.transition()
                .duration(200)
                .style("opacity", 0.0);
        })
        .on("click", function(d) {

            bee_click_tracker[d.bee_id] = !bee_click_tracker[d.bee_id];

            if (bee_click_tracker[d.bee_id]) {


                d3.select("#"+d.bee_id+"_line").transition().style("opacity", 1.0);
                d3.select("#"+d.bee_id+"_bar").transition().style("fill", BEE_BAR_SELECT_COLOR);
            }
            else {


                d3.select("#"+d.bee_id+"_line").transition().style("opacity", 0.0);
                d3.select("#"+d.bee_id+"_bar").transition().style("fill", DEFAULT_BAR_COLOR);
            }
        });

    var lines_g = bee_svg.selectAll("g.bee_to_queen")
        .data(init_bee_data).enter()
        .append("g")
        .attr("class", "bee_to_queen_g");

    lines_g.append("line")
        .attr("class", "bee_line")
        .attr("id", function(d) {
            return d.bee_id + "_line";
        })
        .attr("x1", function(d) {
            return beeXScale(0);
        })
        .attr("x2", function(d) {
            return beeXScale(d.x);
        })
        .attr("y1", function(d) {
            return beeYScale(0);
        })
        .attr("y2", function(d) {
            return beeYScale(d.y);
        })
        .style("stroke", BEE_LINE_COLOR)
        .style("opacity", 0.0);
}

function updateBeeLayer(backend_results) {
    var updated_bee_positions = backend_results["bees_position_history"];

    var updated_bee_data = [];
    for (var bee_key in updated_bee_positions) {
        bee_i = updated_bee_positions[bee_key];
        updated_bee_data.push({
            "bee_id"                : bee_key,
            "x"                     : bee_i.x,
            "y"                     : bee_i.y,
            "found_queen_direction" : bee_i.found_queen_direction
        });

        BEE_DISTANCES[bee_key] = Math.sqrt((bee_i.x)**2 + (bee_i.y)**2)
    }

    // update bee distance vis
    updateBeeDistanceVis();

    d3.selectAll(".bees")
        .data(updated_bee_data)  // Update with new data
        .transition()  // Transition from old to new
        .attr("xlink:href", function(d) {
            var worker_path = (d.found_queen_direction) ? SELECTED_COLORMAP.worker_active : SELECTED_COLORMAP.worker
            return (d.bee_id.split("_")[0] === "worker") ? worker_path : SELECTED_COLORMAP.queen;
        })
        .attr("x", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeXScale(d.x) - icon_size/2.0;
        })
        .attr("y", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeYScale(d.y) - icon_size/2.0;
        });

    d3.selectAll(".bee_line")
        .data(updated_bee_data).transition()
        .attr("x2", function(d) {
            return beeXScale(d.x);
        })
        .attr("y2", function(d) {
            return beeYScale(d.y);
        });
}

function updateBeeImages() {
    d3.selectAll(".bees")
        .transition()  // Transition from old to new
        .attr("xlink:href", function(d) {
            var worker_path = (d.found_queen_direction) ? SELECTED_COLORMAP.worker_active : SELECTED_COLORMAP.worker
            return (d.bee_id.split("_")[0] === "worker") ? worker_path : SELECTED_COLORMAP.queen;
        });
}

function initBeeDistanceVis() {

    d3.select("#bee_distance_svg").remove();

    var margin = {top: 50, right: 100, bottom: 50, left: 100};
    var width = bee_bar_graph_width - margin.left - margin.right;
    var height = bee_bar_graph_height - margin.top - margin.bottom;

    // prep data
    var bee_data = [];
    for (var bee_key in BEE_DISTANCES) {
        if (bee_key === "queen") {
            continue;
        }
        bee_data.push({
            "distance"  : BEE_DISTANCES[bee_key],
            "bee_key"   : bee_key
        });
    }

    beeBarXScale = d3.scaleBand()
        .domain(bee_data.map(function(d) { return d.bee_key; }))
        .range([0, width])
        .padding(0.1);

    beeBarYScale = d3.scaleLinear()
        .domain([0, 3])
        .range([height, 0]);

    var bee_distance_svg = d3.select("#bee_distance_div").append("svg")
        .attr("id", "bee_distance_svg")
        .attr("height", bee_bar_graph_height)
        .attr("width", bee_bar_graph_width);

    var bee_distance_g = bee_distance_svg.append("g")
        .attr("id", "bee_distance_g")
        .attr("transform", "translate(70, -20)");

    // Add barchart bars
    bee_distance_g.selectAll("rect.bee_bar")
        .data(bee_data).enter()
        .append("rect")
        .attr("class", "bee_bar")
        .attr('id', function(d) {
            return d.bee_key + "_bar";
        })
        .attr("x", function(d) {
            return beeBarXScale(d.bee_key);
        })
        .attr("width", beeBarXScale.bandwidth())
        .attr("y", function(d) {
            return beeBarYScale(d.distance);
        })
        .attr("height", function(d) {
            return height - beeBarYScale(d.distance);
        })
        .style("fill", DEFAULT_BAR_COLOR);

    // add the x Axis
    bee_distance_g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(beeBarXScale))
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.15em")
            .attr("x", "-1.0em")
            .attr("dy", "-.5em")
            .attr("transform", function(d) {
                return "rotate(-90)"
            });

    // add the y Axis
    bee_distance_g.append("g")
        .call(d3.axisLeft(beeBarYScale));

    // y axis text
    bee_distance_g.append("text")
        .attr("transform", "rotate(-90)")
        .attr('x', 0 - margin.left*1.1)
        .attr('y', 0 - 50)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Distance from Queen");

    d3.select("#bee_distance_div").transition(1000).style("opacity", 1.0);
}

function updateBeeDistanceVis() {
    // prep data
    var bee_data = [];
    for (var bee_key in BEE_DISTANCES) {
        if (bee_key === "queen") {
            continue;
        }
        bee_data.push({
            "distance"  : BEE_DISTANCES[bee_key],
            "bee_key"   : bee_key
        });
    }

    d3.selectAll("rect.bee_bar").data(bee_data)
        .transition()
        .attr("y", function(d) {
            return beeBarYScale(d.distance);
        })
        .attr("height", function(d) {
            return height - beeBarYScale(d.distance);
        });
}

function init_bee_concentration_history_vis() {
    console.log(BEE_CONCENTRATION_HISTORIES);
    d3.select("#bee_concentration_history_svg").remove();

    var bee_concentration_history_width = 500;
    var bee_concentration_history_height = 500;

    margin = {top: 100, right: 100, bottom: 100, left: 100}
    width = bee_concentration_history_width - margin.left - margin.right // Use the window's width
    height = bee_concentration_history_height - margin.top - margin.bottom; // Use the window's height

    // Setup data and Get max concentrations
    concentration_history_data = [];
    concentrations = [];
    for (var bee_key in BEE_CONCENTRATION_HISTORIES) {
        if (bee_key === "queen") {
            continue;
        }
        var concentration = BEE_CONCENTRATION_HISTORIES[bee_key]["concentration_history"];
        concentration_history_data.push({"bee_key" : bee_key, "concentration" : concentration});
        for (var j=0; j < concentration.length; j++) {
            concentrations.push(concentration[j]);
        }
    }
    var max_history_concentration = d3.max(concentrations);
    var max_timestep = BEE_CONCENTRATION_HISTORIES["worker_1"].length;

    beeConcentrationXScale = d3.scaleLinear()
        .domain([0, max_timestep]) // input
        .range([0, width]); // output

    beeConcentrationYScale = d3.scaleLinear()
        .domain([0, max_history_concentration*1.2]) // input
        .range([height, 0]); // output

    var bee_concentration_history_svg = d3.select("#bee_concentration_history_div").append("svg")
        .attr("id", "bee_concentration_history_svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    bee_concentration_history_svg.append("g")
        .attr("class", "x_axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(beeConcentrationXScale).ticks(5)); // Create an axis component with d3.axisBottom

    // text label for the x axis
    bee_concentration_history_svg.append("text")
        .attr("transform", "translate(" + (width/2) + " ," + (height + margin.top*0.7) + ")")
        .style("text-anchor", "middle")
        .text("Timesteps (seconds)");

    bee_concentration_history_svg.append("g")
        .attr("class", "y_axis")
        .call(d3.axisLeft(beeConcentrationYScale)); // Create an axis component with d3.axisLeft

    // text label for the y axis
    bee_concentration_history_svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("x", 0)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Average Worker Distance from Queen");


    // Plot!
    // for (var experiment_id in EXPERIMENTS_DATA) {
    //     plot_experiment_results(experiment_id, max_height)
    // }

    plot_concentration_history(concentration_history_data);
}


function plot_concentration_history(dataset) {

    bee_history_line = d3.line()
        .x(function(d, i) { return beeConcentrationXScale(i); }) // set the x values for the line generator
        .y(function(d) { return beeConcentrationYScale(d); }) // set the y values for the line generator
        .curve(d3.curveMonotoneX) // apply smoothing to the line

    var bee_concentration_history_svg = d3.select("#bee_concentration_history_svg");

    for (var i=0; i < dataset.length; i++) {

        var data = dataset[i].concentration;
        bee_concentration_history_svg.append("path")
          .data(data)
          .attr("class", "line")
          .attr("d", bee_history_line);
    }

}
