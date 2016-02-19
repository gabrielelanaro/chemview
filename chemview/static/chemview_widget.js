/* This is a require js module :) */
require.config({
    paths: {
        'three': '/nbextensions/three.min',
        'arcball': '/nbextensions/ArcballControls',
        'base64-arraybuffer': '/nbextensions/base64-arraybuffer'
    },
    shim: {

        'three': {
            exports: 'THREE'
        },

        'arcball': {
            deps: ['three'],
            exports: 'THREE.ArcballControls'
        },

        '/nbextensions/jquery-ui.min': {
            exports: "$"
        },

    }
})

define(['widgets/js/widget',
        '/nbextensions/chemview.js',
        '/nbextensions/scales.js'
    ],
    function(widget, chemview, ColorScale) {
        var HEIGHT = 600,
            WIDTH = 600,
            HEIGHT_PX = HEIGHT + 'px',
            WIDTH_PX = WIDTH + 'px';

        var MolecularView = widget.DOMWidgetView.extend({
            
            render: function() {
                
                var WIDTH = this.model.get('width'),
                    HEIGHT = this.model.get('height');

                var that = this;
                var model = this.model;
                var canvas = $("<canvas/>"); // .height(HEIGHT).width(WIDTH);
                var mv = new chemview.MolecularViewer(canvas);
                console.log("Created molecularviewer");
                console.log(this);
                this.mv = mv;
                this.mv.resize(WIDTH, HEIGHT);

                this.model.on("msg:custom", function(msg) {
                    that.on_msg(msg);
                });

                var container = $('<div/>').height(HEIGHT).width(
                        WIDTH)
                    .resizable({
                        aspectRatio: false,
                        resize: function(event, ui) {
                            mv.resize(ui.size.width, ui
                                .size.height);
                            model.set('width', ui.size.width);
                            model.set('height', ui.size
                                .height);
                            that.touch();
                        },
                        stop: function(event, ui) {
                            mv.render();
                        },
                    });
                this.container = container;

                container.append(canvas);
                this.setElement(container);
                mv.renderer.setSize(WIDTH, HEIGHT);

                this.setupFullScreen(canvas, container);
                // That was pretty hard.
                // The widget is added at THE VERY END, and this event gets called.
                this.on('displayed', function() {
                    mv.animate();
                    mv.controls.handleResize();
                });

                // Update the camera when the controls are changed
                var model = this.model;


                // We update the camera info at all times
                that.mv.controls.staticMoving = this.model.get(
                    'static_moving');
                this.model.on('change:static_moving', function() {
                    that.mv.controls.staticMoving =
                        this.model.get('static_moving');
                });

                // Save camera info
                that.model.set({
                    'camera_str': JSON.stringify({
                        cid: that.cid,
                        position: that.mv.camera
                            .position,
                        quaternion: that.mv.camera
                            .quaternion,
                        aspect: that.mv.camera.aspect,
                        fov: that.mv.camera.fov,
                        target: that.mv.controls
                            .target
                    })
                });

                mv.controls.addEventListener('change',
                    function() {
                        that.model.set({
                            'camera_str': JSON.stringify({
                                cid: that.cid,
                                position: that
                                    .mv.camera
                                    .position,
                                quaternion: that
                                    .mv.camera
                                    .quaternion,
                                aspect: that
                                    .mv.camera
                                    .aspect,
                                fov: that.mv
                                    .camera
                                    .fov,
                                target: that
                                    .mv.controls
                                    .target
                            })
                        });

                        that.touch();
                    }
                );


                // We listen for changes in the camera
                this.model.on("change:camera_str", function(
                    context) {
                    var camera_spec = JSON.parse(that.model
                        .get('camera_str'));

                    // This function is only for external updates to the camera.
                    // Avoid updating yourself in an infinite loop
                    if (camera_spec.cid != that.cid) {
                        var q = camera_spec.quaternion,
                            p = camera_spec.position;

                        that.mv.controls.lastPosition.set(
                            p.x, p.y, p.z);
                        that.mv.camera.position.set(p.x,
                            p.y, p.z);

                        that.mv.controls.lastQuaternion
                            .set(q._x, q._y, q._z, q._w);
                        that.mv.camera.quaternion.set(q
                            ._x, q._y, q._z, q._w);

                        that.mv.render();
                    }

                });

                mv.render();

                this.model.set('loaded', true);
                this.touch();
            },
            resize: function(width, height) {
                this.model.set("width", width);
                this.model.set("height", height);

                this.mv.resize(width, height);
                this.container.width(width).height(height);
                this.mv.render();
                this.touch();
            },

            update: function() {
                return MolecularView.__super__.update.apply(
                    this);
            },

            setupFullScreen: function(canvas, container) {
                // currently only works in chrome. need other prefixes for firefox
                var mv = this.mv;
                var model = this.model;
                var that = this;

                canvas.dblclick(function() {
                    // model.trigger("fullscreen", that);
                    console.log("Mv going fullscreen");
                    that.send({
                        event: "fullscreen"
                    });

                    if ('webkitCancelFullScreen' in
                        document) {
                        if (!document.webkitIsFullScreen) {
                            canvas[0].webkitRequestFullScreen();
                            mv.resize(screen.width,
                                screen.height);
                            mv.render();
                        }
                    } else if ('mozCancelFullScreen' in
                        document) {
                        if (!document.mozIsFullScreen) {
                            canvas[0].webkitRequestFullScreen();
                            mv.resize(screen.width,
                                screen.height);
                            mv.render();
                        }
                    }
                });

                if ('webkitCancelFullScreen' in document) {
                    document.addEventListener(
                        "webkitfullscreenchange",
                        function() {
                            if (!document.webkitIsFullScreen) {
                                var width = model.get(
                                        'width'),
                                    height = model.get(
                                        'height');

                                container.width(width).height(
                                    height);
                                mv.resize(width, height);
                            }
                        });
                } else if ('mozCancelFullScreen' in document) {
                    document.addEventListener(
                        "mozfullscreenchange",
                        function() {
                            if (!document.mozIsFullScreen) {
                                var width = model.get(
                                        'width'),
                                    height = model.get(
                                        'height');

                                container.width(width).height(
                                    height);
                                mv.resize(width, height);
                            }
                        });
                }
            },

            /* We receive custom messages from our python conterpart with DOMWidget.send */
            on_msg: function(msg) {
                console.log('Receving message');
                if (msg.type == 'callMethod') {
                    this[msg.methodName].call(this, msg.args);
                }

                return MolecularView.__super__.update.apply(
                    this);
            },

            remove: function() {
                // Cleanup
                // console.log("Cleaning up" + this.mv.requestId);
                console.log("calling remove");
                window.cancelAnimationFrame(this.mv.requestId);

            },

            addRepresentation: function(args) {
                var type = args.type,
                    repId = args.repId,
                    options = args.options;
                // Pre-process the options to convert numpy arrays or
                // other data structures
                var that = this;
                _.each(options, function(value, key) {
                    if (typeof value == 'object' &&
                        value != null && ('data' in
                            value)) {
                        // This is a numpy array
                        options[key] = that.ndarrayToTypedArray(
                            value);
                    }
                });


                var c = chemview;

                if (type == 'points') {
                    var rep = new c.PointsRepresentation(
                        options.coordinates, options.colors,
                        options.sizes, options.visible);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'lines') {
                    var rep = new c.LineRepresentation(options.startCoords,
                        options.endCoords, options.startColors,
                        options.endColors);
                    this.mv.addRepresentation(rep, repId);

                } else if (type == 'surface') {
                    var rep = new c.SurfaceRepresentation(
                        options.verts, options.faces,
                        options.style, options.color);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'spheres') {
                    var rep = new c.SphereRepresentation(
                        options.coordinates, options.radii,
                        options.colors, options.resolution);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'box') {
                    var rep = new c.BoxRepresentation(options.start,
                        options.end, options.color);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'smoothline') {
                    var rep = new c.SmoothLineRepresentation(
                        options.coordinates, options.color,
                        options.resolution);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'smoothtube') {
                    var rep = new c.SmoothTubeRepresentation(
                        options.coordinates, options.radius,
                        options.color, options.resolution);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'cylinders') {
                    var rep = new c.CylinderRepresentation(
                        options.startCoords, options.endCoords,
                        options.radii, options.colors,
                        options.resolution);
                    this.mv.addRepresentation(rep, repId);
                } else if (type == 'ribbon') {
                    var rep = new c.RibbonRepresentation(
                        options.coordinates, options.normals,
                        options.color,
                        options.resolution, options.width,
                        options.height, options.arrow);
                    this.mv.addRepresentation(rep, repId);
                } else {
                    console.log("Undefined representation " +
                        type);
                }

                this.mv.controls.handleResize();
                this.mv.render();
            },

            updateRepresentation: function(args) {
                // Updates a previously created representation
                var repId = args.repId,
                    options = args.options;

                // Pre-process for numpy arrays
                var that = this;
                _.each(options, function(value, key) {
                    if (typeof value == 'object' &&
                        value != null && 'data' in
                        value) {
                        // This is a numpy array
                        options[key] = that.ndarrayToTypedArray(
                            value);
                    }
                });

                var rep = this.mv.getRepresentation(repId);
                rep.update(options);
                this.mv.render();
            },

            removeRepresentation: function(args) {
                this.mv.removeRepresentation(args.repId);
                this.mv.render();
            },

            zoomInto: function(args) {

                // Cast if necessary
                if ('data' in args.coordinates)
                    args.coordinates = this.ndarrayToTypedArray(
                        args.coordinates)

                this.mv.zoomInto(args.coordinates);
                this.mv.render();
            },

            addColorScale: function(args) {
                var colorScaleDiv = $("<div\>")
                    .css("position", "absolute")
                    .css("bottom", 0)
                    .css("right", 0);
                var colorScale = new ColorScale(colorScaleDiv,
                    args.colors, args.values);
                this.$el.append(colorScaleDiv);
            },

            ndarrayToTypedArray: function(array) {
                var buffer = decode(array['data']);

                if (array['type'] == 'float32') {
                    return new Float32Array(buffer);
                } else if (array['type'] == 'int32') {
                    return new Int32Array(buffer);
                } else {
                    console.log('Type ' + array['type'] +
                        ' is not supported');
                }

            },

            _handle_export: function() {
                // Handles when the displayimage menu is clicked
                var dataURL = this.mv.renderer.domElement.toDataURL(
                    'image/png');
                this.send({
                    event: 'displayImg',
                    dataUrl: dataURL
                });
            },

            _handle_serialize: function() {
                this.send({
                    event: 'serialize',
                    json: this.mv.serialize()
                });
            }
        });


        return {
            MolecularView: MolecularView
        };
    });
