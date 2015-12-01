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
            this.$box = this.$el;
            
            this.children_views = new widget.ViewList(this.add_child_model, null, this);
            console.log(this.children_views.views);
            this.listenTo(this.model, 'change:children', function(model, value) {
                this.children_views.update(value);
            }, this);
            this.listenTo(this.model, 'change:overflow_x', this.update_overflow_x, this);
            this.listenTo(this.model, 'change:overflow_y', this.update_overflow_y, this);
            this.listenTo(this.model, 'change:box_style', this.update_box_style, this);
            
            // This is a vertical flexbox
            this.update_attr("display", "flex");
            this.update_attr("flex-direction", "column");
            
            // Event capturing: now we do the whole element as fullscreen in spite
            // of single elements
            this.$el.get(0).addEventListener("dblclick", this._on_dblclick.bind(this), true);
            
            this._prev_size = {};
        },

        _on_dblclick: function (event) {
            event.stopPropagation();
            $(document).on("fullscreenchange", this._on_fullscreenchange.bind(this));
            
            this.$el.fullScreen(true);
            console.log(this);
            this._prev_size[this.cid] = [this.model.get("width"), this.model.get("height")];
            
            this.$el.width(screen.width).height(screen.height);
            
            var that = this;
            // We save previous values of width and height
            for (var viewPromise of this.children_views.views) {
                viewPromise.then( function (view) {
                    that._prev_size[view.cid] = [view.model.get("width"), view.model.get("height")];
                });
            }
            //
            
            // TODO UGLY this is just to force it to work, Ideally the Layout
            // should be calculated
            this.children_views.views[0].then(function (view) { view.resize(screen.width, screen.height - 35); });
            this.children_views.views[1].then(function (view) { view.resize(screen.width, screen.height);});
        },
        
        _on_fullscreenchange: function(event) {
            
            console.log("Fullscreen " + this.$el.fullScreen());
            var that = this;
            if (this.$el.fullScreen()) {
                return;
            }
            // The container box itself get shrunk to its initial dimension
            var box_width = this._prev_size[this.cid][0],
                box_height = this._prev_size[this.cid][1];
            this.model.set("width", box_width);
            this.model.set("height", box_height);
            this.$el.width(box_width).height(box_height);
            this.touch();
            //
            
            // For each view we do a resize to its previous value
            for (var viewPromise of this.children_views.views) {
                viewPromise.then(function (view) { 
                    var width = that._prev_size[view.cid][0],
                        height = that._prev_size[view.cid][1];
                    view.resize(width, height);
                });
            }
            //
            
            // We disconnect the event handler from the document
            $(document).off("fullscreenchange", this._on_fullscreenchange.bind(this));
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
                }).then(function () {
                    that.child_after_displayed(view);
                });
                
                return view;
            }).catch(utils.reject("Couldn't add child view to box", true));
        },

        child_after_displayed : function (view) {
            /**
             * Callback that gets execuded when views are displayed
             */
            console.log("Displayed hello");
        },
        
        remove: function() {
            /**
             * We remove this widget before removing the children as an optimization
             * we want to remove the entire container from the DOM first before
             * removing each individual child separately.
             */
            BoxView.__super__.remove.apply(this, arguments);
            this.children_views.remove();
            $(document).off("fullscreenchange", this._on_fullscreenchange.bind(this));
        },
    });

    return {
        BoxModel: BoxModel,
        Layout: BoxView
    };
});
