openerp.elvenstudio_form_widget_chart = function (instance) {


    if(typeof form_discrete_bar_chart === 'function' ) {
        form_discrete_bar_chart(instance);
    }


    if(typeof form_multi_bar_chart === 'function' ) {
        form_multi_bar_chart(instance);
    }


    if(typeof form_line_chart === 'function' ) {
        form_line_chart(instance);
    }

};