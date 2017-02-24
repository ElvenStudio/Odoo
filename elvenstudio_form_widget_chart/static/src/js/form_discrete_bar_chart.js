
function form_discrete_bar_chart (instance) {

    instance.elvenstudio_form_widget_chart.FormDiscreteBarGraphWidget = instance.web.form.AbstractField.extend({


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

            this.$el.append($('<svg id="' + field_id + '" class="oe_graph oe_discrete_bar" style="' + field_style + '" >'));
            this.svg = '#' + field_id;

            // update data and redraw the chart
            this.field_value = new_value;

            var staggerlabels       = JSON.parse(this.node.attrs.staggerlabels);
            var tooltips            = JSON.parse(this.node.attrs.tooltips);
            var showvalues          = JSON.parse(this.node.attrs.showvalues);
            var transitionduration  = JSON.parse(this.node.attrs.transitionduration);
            var showyaxis           = JSON.parse(this.node.attrs.showyaxis);
            var showxaxis           = JSON.parse(this.node.attrs.showxaxis);

            window.dispatchEvent(new Event('resize'));
            this.bar(this.field_value, staggerlabels, tooltips, showvalues, transitionduration, showyaxis, showxaxis);
            window.dispatchEvent(new Event('resize'));
        },


        bar: function (data, staggerLabels, tooltips, showValues, transitionDuration, showYAxis, showXAxis) {
            if (typeof(staggerLabels)==='undefined')            staggerLabels = true;
            if (typeof(tooltips)==='undefined')                 tooltips = true;
            if (typeof(showValues)==='undefined')               showValues = true;
            if (typeof(transitionDuration)==='undefined')       transitionDuration = true;
            if (typeof(showYAxis)==='undefined')                showYAxis = true;
            if (typeof(showXAxis)==='undefined')                showXAxis = true;

            var self = this;

            nv.addGraph(function () {
                var chart = nv.models.discreteBarChart()
                    .x(function(d) { return d.label })    //Specify the data accessors.
                    .y(function(d) { return d.value })
                    .staggerLabels(staggerLabels)
                    .tooltips(tooltips)
                    .showValues(showValues)
                    .transitionDuration(transitionDuration)
                    .showYAxis(showYAxis)
                    .showXAxis(showXAxis)
                ;

                //chart.xAxis     //Chart x-axis settings
                //    .ticks(5)

                d3.select(self.svg)
                    .datum(data)
                    .call(chart);
                nv.utils.windowResize(chart.update);
                return chart;
            });
        },

    });

    instance.web.form.widgets.add("form_discrete_bar_chart", "instance.elvenstudio_form_widget_chart.FormDiscreteBarGraphWidget");

}
