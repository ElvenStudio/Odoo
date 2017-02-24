
function form_line_chart (instance) {

    instance.elvenstudio_form_widget_chart.FormLineChartWidget = instance.web.form.AbstractField.extend({

        start: function() {

            this.field_id = this.node.attrs.id;
            this.field_style = this.node.attrs.style;
            this.field_value = null;
            this._super();
        },


        render_value: function() {

            // refresh data
            var new_value = JSON.parse(this.get('value'));
            var field_id = this.node.attrs.id;
            var field_style = this.node.attrs.style;

            // exit if no data exist
            if (new_value==false)
                return;

            // clean the old svg element and create a new one
            d3.selectAll("#" + field_id ).remove();

            this.$el.append($('<svg id="' + field_id + '" class="oe_graph oe_line" style="' + field_style + '" >'));
            this.svg = '#' + field_id;

            // update data and redraw the chart
            this.field_value = new_value;

            var tooltips                    = JSON.parse(this.node.attrs.tooltips);
            var useinteractiveguideline     = JSON.parse(this.node.attrs.useinteractiveguideline);
            var transitionduration          = JSON.parse(this.node.attrs.transitionduration);
            var showlegend                  = JSON.parse(this.node.attrs.showlegend);
            var showyaxis                   = JSON.parse(this.node.attrs.showyaxis);
            var showxaxis                   = JSON.parse(this.node.attrs.showxaxis);

            this.line(this.field_value, tooltips, useinteractiveguideline, transitionduration, showlegend, showyaxis, showxaxis);

        },


        line: function (data,tooltips, useinteractiveguideline, transitionduration, showlegend, showyaxis, showxaxis) {
            var self = this;

            nv.addGraph(function() {
                var chart = nv.models.lineChart()
                        //.margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                        //.x( function(d) { return  d; } )
                        .tooltips(tooltips)
                        .useInteractiveGuideline(useinteractiveguideline)
                        .transitionDuration(transitionduration)
                        .showLegend(showlegend)
                        .showYAxis(showyaxis)
                        .showXAxis(showxaxis)
                ;

                chart.xAxis     //Chart x-axis settings
                    //.tickValues([1462147200000,1462233600000])
                //  .axisLabel('Time (ms)')
                  .tickFormat(function(d) {
                        return d3.time.format("%d/%m")(new Date(d*1000))
                    });

                //
                //chart.yAxis     //Chart y-axis settings
                //  .axisLabel('Voltage (v)')
                //  .tickFormat(d3.format('.02f'));

                d3.select(self.svg)      //Select the <svg> element you want to render the chart in.
                  .datum(data)           //Populate the <svg> element with chart data...
                  .call(chart);          //Finally, render the chart!

                //Update the chart when window resizes.
                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

    });

    instance.web.form.widgets.add("form_line_chart", "instance.elvenstudio_form_widget_chart.FormLineChartWidget");


}
