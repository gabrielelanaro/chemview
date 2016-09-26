
require([
    "jquery",
    "widgets/js/widget",
    'jqueryui',
    ],
function($, WidgetManager) {
    var FloatRangeWidget = IPython.DOMWidgetView.extend({
        render : function() {


            this.width = 600;
            this.height = 20;

            var model = this.model;

            this.min = this.model.get('min');
            this.max = this.model.get('max');
            this.value_min = this.model.get('value_min');
            this.value_max = this.model.get('value_max');
            this.step = this.model.get('step');
            
            this.description = this.model.get('description');
            // Create the ui elements
            // 
            
            var that = this;

            var indicator = $('<div/>');
            this.indicator = indicator;
            this.setIndicator(this.value_min, this.value_max);
            
            var desc = $('<div/>');
            this.desc = desc;

            desc.text(this.description);

            var slider = $( "<div/>" ).slider({
              range: true,
              min: that.min,
              max: that.max,
              step: that.step,
              values: [ that.value_min, that.value_max ],

              slide: function( event, ui ) {
                that.model.set('value_min', ui.values[ 0 ]);
                that.model.set('value_max', ui.values[ 1 ]);
                that.touch()
                that.setIndicator(ui.values[0], ui.values[1]);
              }
            });
            this.slider = slider;


            // We add an extra container for the slider just for the styling
            var sliderContainer = $("<div/>").css({ "margin": "16px 16px" ,
                                                    "flex-grow" : "1" });

            var container = $("<div/>").width(this.width).height(this.height)
                                       .css( { display: "flex" } );
            slider.appendTo(sliderContainer);

            desc.appendTo(container);
            sliderContainer.appendTo(container);
            indicator.appendTo(container);

            this.setElement(container);

        },


        update : function () {
            this.min = this.model.get('min');
            this.max = this.model.get('max');
            this.value_min = this.model.get('value_min');
            this.value_max = this.model.get('value_max');
            this.step = this.model.get('step');
            this.description = this.model.get('description');

            this.desc.text(this.description);

            this.setIndicator( this.value_min, this.value_max );
            return FloatRangeWidget.__super__.update.apply(this);
        },

        setIndicator : function (value_min, value_max) {
            this.indicator.text('[' + value_min + ' , ' + value_max + ']');
        },

    });

    WidgetManager.register_widget_view('FloatRangeWidget', FloatRangeWidget);
});