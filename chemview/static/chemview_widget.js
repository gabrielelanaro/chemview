require([
    "jquery",
    "widgets/js/widget",
    "chemview",
    "exporter",
    "filesaver",
    "contextmenu",
    "base64-arraybuffer", // provides decode
    'jqueryui',
    'ArcballControls',
    ],
function($, WidgetManager) {
    var HEIGHT = 600,
        WIDTH = 600,
        HEIGHT_PX = '600px',
        WIDTH_PX = '600px';

    var MolecularView = IPython.DOMWidgetView.extend({

        render : function() {

            console.log(this);
            var WIDTH = this.model.get('width'),
                HEIGHT = this.model.get('height');

            var model = this.model;
            var canvas = $("<canvas/>").height(HEIGHT).width(WIDTH);
            var mv = new MolecularViewer(canvas);
            this.mv = mv;

            var container = $('<div/>').height(HEIGHT).width(WIDTH) 
                .resizable({
                    aspectRatio: false,
                    resize: function(event, ui) {
                        mv.resize(ui.size.width, ui.size.height);
                        model.set('width', ui.size.width);
                        model.set('height', ui.size.height);

                    },
                    stop : function(event, ui) {
                        mv.render();
                    },
                });

            this.setupContextMenu(this);

            container.append(canvas);
            this.setElement(container);
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
            return MolecularView.__super__.update.apply(this);
        },

        setupFullScreen : function(canvas, container) {
            // currently only works in chrome. need other prefixes for firefox
            var mv = this.mv;
            var model = this.model;
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
                            var width = model.get('width'),
                                height = model.get('height');

                            container.width(width).height(height);
                            mv.resize(width, height);
                        }
                    });
            } else if ('mozCancelFullScreen' in document) {
                document.addEventListener("mozfullscreenchange", function() {
                        if (!document.mozIsFullScreen) {
                            var width = model.get('width'),
                                height = model.get('height');

                            container.width(width).height(height);
                            mv.resize(width, height);
                        }
                    });
            }
        },

        /* We receive custom messages from our python conterpart with DOMWidget.send */
        on_msg: function(msg) {
            if (msg.type == 'callMethod') {
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


            if (type == 'points') {
                var rep = new PointsRepresentation(options.coordinates, options.colors, options.sizes);
                this.mv.zoomInto(options.coordinates);
                this.mv.addRepresentation(rep, repId);
            } else if (type == 'lines') {
                var rep = new LineRepresentation(options.startCoords, options.endCoords, options.startColors, options.endColors);
                this.mv.zoomInto(options.startCoords);
                this.mv.addRepresentation(rep, repId);

            } else if (type == 'surface') {
                var rep = new SurfaceRepresentation(options.verts, options.faces, options.style);
                this.mv.addRepresentation(rep, repId);
            } else if (type == 'spheres') {
                var rep = new SphereRepresentation(options.coordinates, options.radii, options.colors, options.resolution);
                this.mv.addRepresentation(rep, repId);
                this.mv.zoomInto(options.coordinates);
            } else if (type == 'box') {
                var rep = new BoxRepresentation(options.start, options.end, options.color);
                this.mv.addRepresentation(rep, repId);
            } else if (type == 'smoothline') {
                var rep = new SmoothLineRepresentation(options.coordinates, options.color, options.resolution);
                this.mv.addRepresentation(rep, repId);
                this.mv.zoomInto(options.coordinates);
            } else if (type == 'smoothtube') {
                var rep = new SmoothTubeRepresentation(options.coordinates, options.radius, options.color, options.resolution);
                this.mv.addRepresentation(rep, repId);
            } else if (type == 'cylinders') {
                var rep = new CylinderRepresentation(options.startCoords, options.endCoords, options.radii, options.colors, options.resolution);
                this.mv.addRepresentation(rep, repId);
                this.mv.zoomInto(options.startCoords);
            }
            else {
                console.log("Undefined representation " + type);
            }

            this.mv.controls.handleResize();
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

            var rep = this.mv.getRepresentation(repId);
            rep.update(options);
            this.mv.render();
        },

        removeRepresentation: function (args) {
            this.mv.removeRepresentation(args.repId);
            this.mv.render();
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

        },

        setupContextMenu : function(viewer) {
            context.init({preventDoubleContext: true});
            this.on('exportImg', this._handle_export.bind(this));
            var menu = [{header: 'Inline Display'},
                    {text: 'PNG',
                    action: function () {
                        viewer.trigger("exportImg");
                    }
                },];
            context.attach('canvas', menu);

        },
        
        _handle_export: function(){
            // Handles when the displayimage menu is clicked
            var dataURL = this.mv.renderer.domElement.toDataURL('image/png');
            this.send({event: 'displayImg', dataUrl: dataURL});
        },

        _handle_serialize: function () {
            this.send({event: 'serialize', json: this.mv.serialize()});
        }
    });

    WidgetManager.register_widget_view('MolecularView', MolecularView);
});