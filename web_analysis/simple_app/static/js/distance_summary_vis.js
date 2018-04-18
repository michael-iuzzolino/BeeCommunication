function initVisPlot(experiment_data) {
    console.log(experiment_data);

    d3.select("#vis_div_svg").remove();

    var timesteps = experiment_data.timesteps;
    var max_timestep = d3.max(timesteps);

    var vis_div = d3.select('#vis_div').node().getBoundingClientRect();

    var div_window_width = vis_div.width * 0.8;
    var div_window_height = distance_summary_plot_height;
    margin = {top: 50, right: 50, bottom: 50, left: 50}
    width = div_window_width - margin.left - margin.right // Use the window's width
    height = div_window_height - margin.top - margin.bottom; // Use the window's height

    // Get max height of experiment data
    var heights = [];
    for (var experiment_id in EXPERIMENTS_DATA) {
        var data = EXPERIMENTS_DATA[experiment_id].averages;
        for (var j=0; j < data.length; j++) {
            heights.push(data[j]);
        }
    }
    var max_height = d3.max(heights);

    xScale = d3.scaleLinear()
        .domain([0, max_timestep]) // input
        .range([0, width]); // output

    colorScale = d3.scaleLinear()
        .domain([0, Object.keys(EXPERIMENTS_DATA).length])
        .range(COLORS);

    yScale = d3.scaleLinear()
        .domain([0, max_height]) // input
        .range([height, 0]); // output

    svg = d3.select("#vis_div").append("svg")
        .attr("id", "vis_div_svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x_axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale).ticks(5)); // Create an axis component with d3.axisBottom

    // text label for the x axis
    svg.append("text")
        .attr("transform", "translate(" + (width/2) + " ," + (height + margin.top*0.7) + ")")
        .style("text-anchor", "middle")
        .text("Timesteps (seconds)");


    svg.append("g")
        .attr("class", "y_axis")
        .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

    // text label for the y axis
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Average Worker Distance from Queen");


    line = d3.line()
        .x(function(d, i) { return xScale(d.x); }) // set the x values for the line generator
        .y(function(d) { return yScale(d.y); }) // set the y values for the line generator
        .curve(d3.curveMonotoneX) // apply smoothing to the line

    // Plot!
    for (var experiment_id in EXPERIMENTS_DATA) {
        plot_experiment_results(experiment_id, max_height)
    }
}

function plot_experiment_results(experiment_id) {

    // Load data from dict for current experiment
    var experiment_data = EXPERIMENTS_DATA[experiment_id];

    // Update plotted experiment ids with current id
    plotted_experiment_ids.push(experiment_id);

    // Get data from experiment
    var timesteps = experiment_data.timesteps;
    var average_distances = experiment_data.averages;


    // Build dataset for path
    var dataset = d3.range(timesteps.length).map(function(d, i) {
        var data_point = {
            "x" : timesteps[i],
            "y" : average_distances[i]
        }
        return data_point;
    });

    // data is created inside the function so it is always unique
    let animate_line = () => {
      var path = svg.append("path")
        .attr("d", line(dataset))
        .attr("class", "line")
        .attr('id', experiment_id)
        .on("mouseover", function() {
            mouseover_line(this.id);
        })
        .on("mouseout", function() {
            mouseout_line(this.id);
        })
        .on("click", function() {
            click_line(this.id);
        })
        .style("stroke", function() {
            var index = experiment_id.split("_")[1];
            return colorScale(index);
        });

      var totalLength = path.node().getTotalLength();

      path
        .attr("stroke-dasharray", totalLength + " " + totalLength)
        .attr("stroke-dashoffset", totalLength)
        .transition()
          .duration(3500)
          .ease(d3.easeLinear)
          .attr("stroke-dashoffset", 0);
    };
    animate_line();
}



function update_history_marker() {
    var current_vis_data = EXPERIMENTS_DATA[current_vis_id];

    var new_x = current_vis_data.timesteps[current_timestep];
    var new_y = current_vis_data.averages[current_timestep];

    d3.select("#timestep_marker")
        .transition().duration(250)
        .attr("cx", xScale(new_x))
        .attr("cy", yScale(new_y));

    d3.select("#timestep_marker").moveToFront();

}
