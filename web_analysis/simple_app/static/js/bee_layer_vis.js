function initBeeLayer(backend_results) {
    var init_bee_positions = backend_results["bees_position_history"];

    var init_bee_data = [];
    var x_values = [];
    var y_values = [];
    for (var bee_key in init_bee_positions) {
        bee_i = init_bee_positions[bee_key];
        init_bee_data.push({
            "bee_id"    : bee_key,
            "x"         : bee_i.x,
            "y"         : bee_i.y,
        });
        x_values.push(bee_i.x);
        y_values.push(bee_i.y);
    }

    // Init tooltip
    d3.select('body').append("div").attr("id", "bee_name_tooltip_div");
    d3.select('body').append("div").attr("id", "distance_tooltip_div");


    // Create SVG overlay
    var bee_svg = d3.select("#concentration_div").append("svg")
        .attr("id", "bee_svg")
        .attr("height", heatmap_size)
        .attr("width", heatmap_size);

    beeXScale = d3.scaleLinear()
        .domain([-3.0, 3.0])
        .range([0, heatmap_size]);

    beeYScale = d3.scaleLinear()
        .domain([-3.0, 3.0])
        .range([0, heatmap_size]);

    bee_ids = [];
    for (var j=0; j < init_bee_data.length; j++) {
        bee_ids.push(init_bee_data[j].bee_id);
    }

    bee_svg.selectAll('image.bees')
        .data(init_bee_data).enter()
        .append('image')
        .attr("class", "bees")
        .attr("id", function(d) {
            return d.bee_id;
        })
        .attr('xlink:href', function(d) {
            return (d.bee_id.split("_")[0] === "worker") ? worker_img_path_1 : queen_img_path_1;
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

            var distance_to_queen = Math.sqrt((d.x)**2 + (d.y)**2);

            var bee_name_tooltip_div = d3.select("#bee_name_tooltip_div");
            bee_name_tooltip_div.transition()
                .duration(200)
                .style("opacity", .9);

            bee_name_tooltip_div.html(function() {
                    return d.bee_id.replace("_", " ");
                })
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");


            var distance_tooltip_div = d3.select("#distance_tooltip_div");
            distance_tooltip_div.transition()
                .duration(200)
                .style("opacity", .9);

            distance_tooltip_div.html(function() {
                    return distance_to_queen.toFixed(4);
                })
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY) + "px");


            d3.select("#"+d.bee_id+"_line").transition().style("opacity", 1.0);

        })
        .on("mouseout", function() {
            d3.select("#bee_name_tooltip_div").transition()
                .duration(500)
                .style("opacity", 0);

            d3.select("#distance_tooltip_div").transition()
                .duration(500)
                .style("opacity", 0);

            for (var j=0; j < bee_ids.length; j++) {
                d3.select("#"+bee_ids[j]+"_line").transition().style("opacity", 0.0);
            }
        });


    var lines_g = bee_svg.selectAll("g.bee_to_queen")
        .data(init_bee_data).enter()
        .append("g")
        .attr("class", "bee_to_queen_g");

    lines_g.append("line")
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
        .style("fill", "black")
        .style("stroke", "black")
        .style("opacity", 0.0);
}

function updateBeeLayer(backend_results) {
    var updated_bee_positions = backend_results["bees_position_history"];

    var updated_bee_data = [];
    for (var bee_key in updated_bee_positions) {
        bee_i = updated_bee_positions[bee_key];
        updated_bee_data.push({
            "bee_id"    : bee_key,
            "x"         : bee_i.x,
            "y"         : bee_i.y,
        });
    }

    d3.selectAll(".bees")
        .data(updated_bee_data)  // Update with new data
        .transition()  // Transition from old to new
        .attr("x", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeXScale(d.x) - icon_size/2.0;
        })
        .attr("y", function(d) {
            var icon_size = (d.bee_id.split("_")[0] === "worker") ? worker_bee_icon_size : queen_bee_icon_size;
            return beeYScale(d.y) - icon_size/2.0;
        });

    d3.selectAll(".bee_to_queen_g").select("line")
        .data(updated_bee_data) .transition()
        .attr("x2", function(d) {
            return beeXScale(d.x);
        })
        .attr("y2", function(d) {
            return beeYScale(d.y);
        });
}
