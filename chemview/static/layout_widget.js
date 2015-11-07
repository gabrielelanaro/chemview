// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// npm compatibility
if (typeof define !== 'function') { var define = require('./requirejs-shim')(module); }

require.config({
   "paths": {
     "jquery": "//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min",
     "jqueryui": "nbextensions/jquery-ui.min",
    //  "jqueryfullscreen": "nbextensions/jquery.fullscreen-min"
    },
    "shim": {
      "nbextensions/jquery.fullscreen": {
          "deps": ["jquery"]
      } 
    },
});

define([
    "widgets/js/widget",
    "base/js/utils",
    "jqueryui",
    "underscore",
    "bootstrap",
    "nbextensions/jquery.fullscreen"
], function(widget, utils, $, _) {
    "use strict";
    
    var BoxModel = widget.WidgetModel.extend({}, {
        serializers: _.extend({
            children: {deserialize: widget.unpack_models}
        }, widget.WidgetModel.serializers)
    });

    var BoxView = widget.DOMWidgetView.extend({
        initialize: function() {
            /**
             * Public constructor
             */
            console.log("Constructor init");
            BoxView.__super__.initialize.apply(this, arguments);
            var that = this;
            
            this.children_views = new widget.ViewList(this.add_child_model, null, this);
            this.listenTo(this.model, 'change:children', function(model, value) {
                this.children_views.update(value);
            }, this);
            this.listenTo(this.model, 'change:overflow_x', this.update_overflow_x, this);
            this.listenTo(this.model, 'change:overflow_y', this.update_overflow_y, this);
            this.listenTo(this.model, 'change:box_style', this.update_box_style, this);
            // Event capturing: now we do the whole element as fullscreen in spite
            // of single elements
            this.$el.get(0).addEventListener("dblclick", function (event) {
                event.stopPropagation();
                that.$el.fullScreen(true);
                that.$el.width(screen.width).height(screen.height);
                
                // For each view we do a resize
                for (let viewPromise of that.children_views.views) {
                    viewPromise.then(function (view) { 
                        view.resize(screen.width, screen.height)
                    });
                
                
                }
            }, true);
            
            $(document).on("fullscreenchange", function (event) {
                if (that.$el.fullScreen())
                    return;
                    
                // Coming back from fullscreen we simply reset width and height
                var width = that.model.get('width'),
                    height = that.model.get('height');
                that.$el.width(width).height(height);
                // For each view we do a resize
                for (let viewPromise of that.children_views.views) {
                    viewPromise.then(function (view) { 
                        view.resize(width, height)
                    });
                }
            });
        },

        update_attr: function(name, value) {
            /**
             * Set a css attr of the widget view.
             */
            this.$box.css(name, value);
        },

        render: function() {
            /**
             * Called when view is rendered.
             */
            this.$el.addClass("ipy-widget widget-container widget-box");
            this.$box = this.$el;
            this.children_views.update(this.model.get('children'));
            this.update_overflow_x();
            this.update_overflow_y();
            this.update_box_style('');
        },

        update_overflow_x: function() {
            /**
             * Called when the x-axis overflow setting is changed.
             */
            this.$box.css('overflow-x', this.model.get('overflow_x'));
        },

        update_overflow_y: function() {
            /**
             * Called when the y-axis overflow setting is changed.
             */
            this.$box.css('overflow-y', this.model.get('overflow_y'));
        },

        update_box_style: function(previous_trait_value) {
            var class_map = {
                success: ['alert', 'alert-success'],
                info: ['alert', 'alert-info'],
                warning: ['alert', 'alert-warning'],
                danger: ['alert', 'alert-danger']
            };
            this.update_mapped_classes(class_map, 'box_style', previous_trait_value, this.$box[0]);
        },

        add_child_model: function(model) {
            /**
             * Called when a model is added to the children list.
             */
            var that = this;
            var dummy = $('<div/>');
            that.$box.append(dummy);
            return this.create_child_view(model).then(function(view) {
                // Here we want to add some settings
                dummy.replaceWith(view.el);
                
                // Trigger the displayed event of the child view.
                that.displayed.then(function() {
                    view.trigger('displayed');
                }).then(function () { // Change the size
                    view.resize(that.model.get("width"), that.model.get("height"));
                });
                
                return view;
            }).catch(utils.reject("Couldn't add child view to box", true));
        },

        remove: function() {
            /**
             * We remove this widget before removing the children as an optimization
             * we want to remove the entire container from the DOM first before
             * removing each individual child separately.
             */
            BoxView.__super__.remove.apply(this, arguments);
            this.children_views.remove();
        },
    });

    return {
        BoxModel: BoxModel,
        Layout: BoxView
    };
});
