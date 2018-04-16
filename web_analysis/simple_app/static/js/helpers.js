d3.selection.prototype.moveToFront = function() {
      return this.each(function(){
        this.parentNode.appendChild(this);
      });
    };
d3.selection.prototype.moveToBack = function() {
    return this.each(function() {
        var firstChild = this.parentNode.firstChild;
        if (firstChild) {
            this.parentNode.insertBefore(this, firstChild);
        }
    });
};

function save_plot() {
    var sendDict = {
        "save_data"         : EXPERIMENTS_DATA[current_vis_id],
        "experiment_name"   : current_vis_id
    }

    $.ajax({
        url: "/save_plot",
        method: "POST",
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(sendDict),
        success: function(python_result){
            console.log("Save successful: " + python_result["successful"])

            var fill_color = (python_result["successful"]) ? "#e6ffe6" : "#ff8080";
            var text = (python_result["successful"]) ? "Save Successful!" : "Save Failed!";

            d3.select("#save_plot_button").transition().duration(250)
            .attr("value", text)
                .style("background-color", fill_color);

            setTimeout(function() {
                d3.select("#save_plot_button").transition().duration(250)
                    .attr("value", "Save Selected Plot as CSV")
                    .style("background-color", "#fff");
            }, 1000);
        }
    });
}
