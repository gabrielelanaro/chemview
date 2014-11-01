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


            var coords = this.model.get('_coordinates');
            var topology = this.model.get('topology');
 
            var rep = new PointLineRepresentation(this.ndarrayToTypedArray(coords),
                                                  topology.bonds, 
                                                  this.model.get('color_scheme'));
            mv.addRepresentation(rep);

            var surface = this.model.get('surface');

            var surf = new SurfaceRepresentation(this.ndarrayToTypedArray(surface.vertices),
                                                 this.ndarrayToTypedArray(surface.faces));
            mv.addRepresentation(surf);

            this.update();
            
            this.pointRepresentation = rep;
            mv.zoomInto(this.ndarrayToTypedArray(coords));
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
            this.mv.controls.handleResize();
            if (this.model.hasChanged('_coordinates')) {

                var coords = this.model.get('_coordinates');

                this.pointRepresentation.update({coordinates: this.ndarrayToTypedArray(coords)});
                this.mv.render();
                console.log('Representation updated');
            }

            if (this.model.hasChanged('topology')) {
                var bonds = this.model.get('topology').bonds;
                this.pointRepresentation.update({bonds: bonds});
            }

            if (this.model.hasChanged('point_size')) {
                this.pointRepresentation.update({point_size: this.model.get('point_size')});
                this.mv.render();
            }

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
            return MolecularView.__super__.update.apply(this);
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