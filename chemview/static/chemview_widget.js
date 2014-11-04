require([
    "jquery",
    "widgets/js/widget",
    "chemview",
    "exporter",
    "filesaver",
    "contextmenu",
    "base64-arraybuffer", // provides decode
    'jqueryui',
    'TrackballControls',
    'marchingcubes',
    ],
function($, WidgetManager) {
    var HEIGHT = 600,
        WIDTH = 600,
        HEIGHT_PX = '600px',
        WIDTH_PX = '600px';

    var MolecularView = IPython.DOMWidgetView.extend({

        render : function() {
            console.log(this);
            var canvas = $("<canvas/>").height(HEIGHT).width(WIDTH);
            var mv = new MolecularViewer(canvas);
            this.mv = mv;

            var container = $('<div/>').css({width: HEIGHT_PX, height: WIDTH_PX})
                .resizable({
                    aspectRatio: false,
                    resize: function(event, ui) {
                        mv.resize(ui.size.width, ui.size.height);
                    },
                    stop : function(event, ui) {
                        mv.render();
                    },
                });

            container.append(canvas);
            this.setElement(container);


            // var coords = this.model.get('_coordinates');
            // var topology = this.model.get('topology');
 
            // var rep = new PointLineRepresentation(this.ndarrayToTypedArray(coords),
            //                                       topology.bonds, 
            //                                       this.model.get('color_scheme'));
            // mv.addRepresentation(rep);

            // var surface = this.model.get('surface');

            // var surf = new SurfaceRepresentation(this.ndarrayToTypedArray(surface.vertices),
            //                                      this.ndarrayToTypedArray(surface.faces));
            // mv.addRepresentation(surf);

            // this.update();
            
            // this.pointRepresentation = rep;

            // mv.zoomInto(this.ndarrayToTypedArray(coords));
            mv.renderer.setSize(WIDTH, HEIGHT);

            this.setupFullScreen(canvas, container);
            // That was pretty hard.
            // The widget is added at THE VERY END, and this event gets called.
            this.model.on('displayed', function () {
                mv.animate();
                mv.controls.handleResize();
            });
            mv.render();
        },

        update : function () {

            console.log('MolecularView.update');

            return MolecularView.__super__.update.apply(this);
        },

        setupFullScreen : function(canvas, container) {
            // currently only works in chrome. need other prefixes for firefox
            var mv = this.mv;
            canvas.dblclick(function () {
                if ('webkitCancelFullScreen' in document) {
                    if (!document.webkitIsFullScreen) {
                        canvas[0].webkitRequestFullScreen();
                        mv.resize(screen.width, screen.height);
                        mv.render();
                    }
                } else if ('mozCancelFullScreen' in document) {
                    if (!document.mozIsFullScreen) {
                        canvas[0].webkitRequestFullScreen();
                        mv.resize(screen.width, screen.height);
                        mv.render();
                    }
                }
            });

            if ('webkitCancelFullScreen' in document) {
                document.addEventListener("webkitfullscreenchange", function() {
                        if (!document.webkitIsFullScreen) {
                            container.width(WIDTH).height(HEIGHT);
                            canvas.width(WIDTH).height(HEIGHT);
                            container.trigger('resize');
                        }
                    });
            } else if ('mozCancelFullScreen' in document) {
                document.addEventListener("mozfullscreenchange", function() {
                        if (!document.mozIsFullScreen) {
                            container.css({width: HEIGHT_PX, height: WIDTH_PX});
                            canvas.css({width: HEIGHT_PX, height: WIDTH_PX});
                            mv.resize(HEIGHT_PX, WIDTH_PX);
                        }
                    });
            }
        },

        /** We receive custom messages from our conterpart */
        on_msg: function(msg) {
            console.log('receivedMsg');
            console.log(msg);

            if (msg.type == 'callMethod') {
                console.log(msg.args);
                this[msg.methodName].call(this, msg.args);
            }

            return MolecularView.__super__.update.apply(this);
        },

        addRepresentation : function (args) {
            var type = args.type,
                repId = args.repId,
                options = args.options;
            // Pre-process the options to convert numpy arrays or 
            // other data structures
            var that = this;
            _.each(options, function(value, key) {
                                if (typeof value == 'object' && 'data' in value) {
                                    // This is a numpy array
                                    options[key] = that.ndarrayToTypedArray(value);
                                }
                            });


            if (type == 'point') {
                var rep = new PointLineRepresentation(options.coordinates, [], options.colors);
                this.mv.zoomInto(options.coordinates);
                this.mv.controls.handleResize();
                this.mv.addRepresentation(rep, repId);
            } else if (type == 'surface') {
                var rep = new SurfaceRepresentation(options.verts, options.faces);
                this.mv.addRepresentation(rep, repId);
                this.mv.controls.handleResize();
            } else if (type == 'spheres') {
                var rep = new SphereRepresentation(options.coordinates, options.radii, options.resolution);
                this.mv.addRepresentation(rep, repId);
            } 
            else {
                console.log("Undefined representation " + type);
            }

            
            this.mv.render();      
        },

        updateRepresentation : function (args) {
            // Updates a previously created representation
            var repId = args.repId,
                options = args.options;

            // Pre-process for numpy arrays
            var that = this;
            _.each(options, function(value, key) {
                    if (typeof value == 'object' && 'data' in value) {
                        // This is a numpy array
                        options[key] = that.ndarrayToTypedArray(value);
                    }
                });

            console.log(repId);
            console.log(repId);
            var rep = this.mv.getRepresentation(repId);
            rep.update(options);
            this.mv.render();
        },

        removeRepresentation: function (repId) {
            // TODO: implement removal so we are complete
        },

        ndarrayToTypedArray: function (array) {
            var buffer = decode(array['data']);

            if (array['type'] == 'float32') {
                return new Float32Array(buffer);
            }
            else if (array['type'] == 'int32') {
                return new Int32Array(buffer);
            }
            else {
                console.log('Type ' + array['type'] + ' is not supported');
            }

        }

    });


    WidgetManager.register_widget_view('MolecularView', MolecularView);
});