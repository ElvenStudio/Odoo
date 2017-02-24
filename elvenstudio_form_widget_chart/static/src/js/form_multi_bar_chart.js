
function form_multi_bar_chart (instance) {

    instance.elvenstudio_form_widget_chart.FormMuliBarGraphWidget = instance.web.form.AbstractField.extend({


        start: function() {
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
            d3.selectAll("#refresh_button").remove();

            this.$el.append($('<svg id="' + field_id + '" class="oe_graph oe_multi_bar" style="' + field_style + '" >'));
            this.svg = '#' + field_id;

            // update data and redraw the chart
            this.field_value = new_value;

            var transitionDuration      = JSON.parse(this.node.attrs.transitionduration);
            var labelAngle              = JSON.parse(this.node.attrs.labelangle);
            var showControls            = JSON.parse(this.node.attrs.showcontrols);
            var groupSpacing            = JSON.parse(this.node.attrs.groupspacing);

            var xAxisTickFormat         = this.node.attrs.xAxisTickFormat;
            var yAxisTickFormat         = this.node.attrs.yAxisTickFormat;

            //window.dispatchEvent(new Event('resize'));
            this.multi_bar(this.field_value, transitionDuration, labelAngle, showControls, groupSpacing, xAxisTickFormat, yAxisTickFormat);
        },


        multi_bar: function (data, transitionDuration, labelAngle, showControls, groupSpacing, xAxisTickFormat, yAxisTickFormat) {
            if (typeof(transitionDuration)==='undefined')        transitionDuration = true;
            if (typeof(labelAngle)==='undefined')                labelAngle = 0;
            if (typeof(showControls)==='undefined')              showControls = true;
            if (typeof(groupSpacing)==='undefined')              groupSpacing = 0.2;

            var self = this;

            nv.addGraph(function () {
                var chart = nv.models.multiBarChart()
                    .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
                    .transitionDuration(transitionDuration)
                    .rotateLabels(labelAngle)      //Angle to rotate x-axis labels.
                    .showControls(showControls)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
                    .groupSpacing(groupSpacing)    //Distance between each group of bars.

                    .x(function(d) { return d.label })    //Specify the data accessors.
                    .y(function(d) { return d.value })

                    //.staggerLabels(staggerLabels)
                    //.tooltips(tooltips)
                    //.showValues(showValues)
                    //
                    //.showYAxis(showYAxis)
                    //.showXAxis(showXAxis)
                ;

                if (! (typeof(xAxisTickFormat)==='undefined')) {
                    chart.xAxis.tickFormat(d3.format(xAxisTickFormat));
                }

                if (! (typeof(yAxisTickFormat)==='undefined')) {
                    chart.yAxis.tickFormat(d3.format(yAxisTickFormat));
                }

                d3.select(self.svg)
                    .datum(data)
                    .call(chart);
                nv.utils.windowResize(chart.update);
                return chart;
            });
        },


    });

    instance.web.form.widgets.add("form_multi_bar_chart", "instance.elvenstudio_form_widget_chart.FormMuliBarGraphWidget");

}
