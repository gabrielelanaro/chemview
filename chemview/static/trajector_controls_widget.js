/**
 * Trajectory control Widget for IPython
 *
 */

require([
    "jquery",
    "widgets/js/widget",
    'jqueryui',
    'ArcballControls',
    ],
function($, WidgetManager) {

    var TrajectoryControls = IPython.DOMWidgetView.extend({
        var FPS = 30;
        render : function() {
            // Create the ui elements
            // 
            // we need
            // min, max
            
            var model = this.model;

            var tc = $('<div/>');
            var slider = $('<div/>').slider({
                value: 0,
                change: function(event, ui) {
                    model.set('frame', ui.value);
                },
            });

            var playButton = $('<button/>').button({
                text: false,
                icons: { primary: "ui-icon-play" },
                click: function( event, ui ) {

                },
            });

            playButton.appendTo(tc);
            slider.appendTo(tc);

            this.setElement(tc);
        },


        update : function () {
            return TrajectoryControls.__super__.update.apply(this);
        },

        play : function () {
            var slider = this.slider;
            this.playCallbackId = setInterval( function () {
                
                if (slider.value() < slider.max())
                    slider.value(slider.value() + 1);

            }, 1000/FPS);

        },

        pause : function () {
            clearInterval(this.playCallbackId);
        },

        /* We receive custom messages from our python conterpart with DOMWidget.send */
        on_msg: function(msg) {
            if (msg.type == 'callMethod') {
                this[msg.methodName].call(this, msg.args);
            }

            return TrajectoryControls.__super__.update.apply(this);
        },

    });

    WidgetManager.register_widget_view('TrajectoryControls', TrajectoryControls);
});