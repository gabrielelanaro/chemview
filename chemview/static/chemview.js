define(function(require) {

	var THREE = require('three');
	THREE.ArcballControls = require('arcball');
	var arraybuf = require('base64-arraybuffer');

	var decode = arraybuf.decode,
		encode = arraybuf.encode;

	var MolecularViewer = function($el) {
		/* A MolecularViewer displays and manages a set of representations for a chemical system.

		*/
		
		this.container = $el;
		this.container.widthInv = 1 / this.container.width();
		this.container.heightInv = 1 / this.container.height();
		this.container.whratio = this.container.width() / this.container.height();
		this.container.hwratio = this.container.height() / this.container.width();
		this.renderer = new THREE.WebGLRenderer({
			canvas: this.container.get(0),
			antialias: true,
			preserveDrawingBuffer: true,
		});
		this.effects = {
			// 'anaglyph': new THREE.AnaglyphEffect(this.renderer),
			// 'parallax barrier': new THREE.ParallaxBarrierEffect(this.renderer),
			// 'oculus rift': new THREE.OculusRiftEffect(this.renderer),
			// 'stereo': new THREE.StereoEffect(this.renderer),
			'none': this.renderer,
		};

		this.camera_z = -150;
		this.perspectiveCamera = new THREE.PerspectiveCamera(20, this.container.whratio,
			0.1, 800);
		this.perspectiveCamera.position.set(0, 0, this.camera_z);
		this.perspectiveCamera.lookAt(new THREE.Vector3(0, 0, 0));
		this.orthographicCamera = new THREE.OrthographicCamera();
		this.orthographicCamera.position.set(0, 0, this.camera_z);
		this.orthographicCamera.lookAt(new THREE.Vector3(0, 0, 0));
		this.cameras = {
			perspective: this.perspectiveCamera,
			orthographic: this.orthographicCamera,
		};
		this.camera = this.perspectiveCamera;

		this.slabNear = -50; // relative to the center of rot
		this.slabFar = +50;

		var background = 0x000000;
		this.renderer.setClearColor(background, 1);

		this.scene = new THREE.Scene();
		this.scene.fog = new THREE.FogExp2(background);

		var directionalLight1 = new THREE.DirectionalLight(0xFFFFFF, 1.2);
		directionalLight1.position.set(0.2, 0.2, -1).normalize();

		var directionalLight2 = new THREE.DirectionalLight(0xFFFFFF, 1.2);
		directionalLight2.position.set(0.2, 0.2, 1).normalize();

		var ambientLight = new THREE.AmbientLight(0x202020);

		this.scene.add(directionalLight1);
		this.scene.add(directionalLight2);
		this.scene.add(ambientLight);
		//this.scene.add(this.camera);

		//this.controls = new THREE.TrackballControls(this.camera, this.container);
		this.controls = new THREE.ArcballControls(this.camera, this.container.get(
			0));
		this.controls.zoomInto = function() {};
		this.controls.handleResize = function() {};

		this.controls.rotateSpeed = 0.4;
		this.controls.zoomSpeed = 1.2;
		this.controls.panSpeed = 0.8;
		this.controls.dynamicDampingFactor = 0.2;

		this.controls.keys = [65, 83, 68];
		this.controls.addEventListener('change', this.render.bind(this));

		this.representations = {};
		this.render();
	};

	MolecularViewer.prototype = {

		addRepresentation: function(representation, repId) {
			representation.addToScene(this.scene);
			this.representations[repId] = representation;
		},

		getRepresentation: function(repId) {
			return this.representations[repId];
		},

		removeRepresentation: function(repId) {
			var rep = this.getRepresentation(repId);
			rep.removeFromScene(this.scene);
		},

		render: function() {
			//if (this.controls.screen.width == 0 || this.controls.screen.height == 0)
			//	this.controls.handleResize();

			this.renderer.render(this.scene, this.camera);
		},

		animate: function() {
			this.requestId = window.requestAnimationFrame(this.animate.bind(this));
			this.controls.update();

		},

		zoomInto: function(coordinates) {
			/* TODO: this function may be out of place */

			// Calulate current geometric centre
			var cur_gc = new THREE.Vector3(0.0, 0.0, 0.0);
			for (var i = 0; i < coordinates.length / 3; i++) {
				cur_gc.x += coordinates[3 * i + 0];
				cur_gc.y += coordinates[3 * i + 1];
				cur_gc.z += coordinates[3 * i + 2];
			}
			cur_gc.divideScalar(coordinates.length / 3);

			var displacement = new THREE.Vector3().subVectors(cur_gc, this.controls.target);
			this.controls.target.copy(cur_gc);
			this.controls.object.position.add(displacement);
			this.controls.object.lookAt(this.controls.target);

			// Calculate the bounding sphere
			var bound = 0;
			for (var i = 0; i < coordinates.length / 3; i++) {
				var point = new THREE.Vector3(coordinates[3 * i + 0],
					coordinates[3 * i + 1],
					coordinates[3 * i + 2]);
				bound = Math.max(bound, point.distanceTo(cur_gc));
			}

			var fov_topbottom = this.camera.fov * Math.PI / 180.0;
			var dist = (bound + this.camera.near) / Math.tan(fov_topbottom * 0.5);

			// Calculate distance vector
			var c = new THREE.Vector3();
			c.subVectors(this.camera.position, this.controls.target);
			c.normalize();

			// move camera at a distance
			c.multiplyScalar(dist);
			this.camera.position.copy(new THREE.Vector3().addVectors(this.controls.target,
				c));
			//this.controls.update();
		},

		resize: function(width, height) {
			this.renderer.setSize(width, height);
			this.controls.handleResize();
			this.camera.aspect = width / height;
			this.camera.updateProjectionMatrix();

			for (var key in this.representations) {
				if (this.representations[key].onResize != undefined) {
					this.representations[key].onResize(width, height);
				}
			}

			this.render();
		},

		exportPng: function() {
			this.renderer.domElement.toDataUrl();
		},

		/**
		 * Return a serialized version of the RepresentationViewer in the JSON format
		 * @return {object} JSON format representation
		 */
		serialize: function() {
			var json = {};
			json.representations = [];

			for (var key in this.representations) {
				json.representations.push(this.representations[key].serialize());
			}

			return json;
		},

		/**
		 * Create a new molecular viewer from a serialized specification
		 * @param  {Object} json A json produced with the method MolecularViewer.serialize
		 * @return {MolecularViewer} a new MolecularViewer
		 */
		deserialize: function(json) {
			var representationMap = {
				points: PointsRepresentation,
				lines: LineRepresentation,
				cylinders: CylinderRepresentation,
				spheres: SphereRepresentation,
				smoothline: SmoothLineRepresentation,
				smoothtube: SmoothTubeRepresentation
			};


			for (var key in json.representations) {
				var rep = representationMap[json.representations[key].type].deserialize(
					json.representations[key]);
				this.addRepresentation(rep, key);
			};

			this.render();
		}
	};



	/**
	 * Flat points in space
	 *
	 * :param Float32Aarray coordinates: a (flattened) array of coordinates
	 * :param list colors: a list of colors (one for each point) expressed as hexadecimal numbers
	 * :param list sizes: a list of sizes for the points
	 */
	var PointsRepresentation = function(coordinates, colors, sizes, visible) {
		// Initialize stuff for serialization
		this.type = "points";
		this.options = {
			'coordinates': coordinates,
			'colors': colors,
			'sizes': sizes
		};


		var DEFAULT_SIZE = 0.15,
			DEFAULT_COLOR = 0xffffff;

		// pre-processing for optional arguments
		if (sizes == undefined) {
			var sizes = [];
			for (var i = 0; i < coordinates.length / 3; i++) {
				sizes.push(DEFAULT_SIZE);
			}
		}

		if (colors == undefined) {
			var colors = [];
			for (var i = 0; i < coordinates.length / 3; i++) {
				colors.push(DEFAULT_COLOR);
			}
		}


		if (visible == undefined) {
			var visible = [];
			for (var i = 0; i < coordinates.length / 3; i++) {
				visible.push(1);
			}
		}

		// That is the points part
		var geo = new THREE.BufferGeometry();
		this.geometry = geo;

		var colorsVert = new Float32Array(colors.length * 3);
		for (var i = 0; i < colors.length; i++) {
			var c = new THREE.Color(colors[i]);
			colorsVert[3 * i] = c.r;
			colorsVert[3 * i + 1] = c.g;
			colorsVert[3 * i + 2] = c.b;
		}

		geo.addAttribute('position', new THREE.BufferAttribute(coordinates, 3));
		geo.addAttribute('color', new THREE.BufferAttribute(colorsVert, 3));
		geo.addAttribute('pointSize', new THREE.BufferAttribute(new Float32Array(
			sizes), 1));
		geo.addAttribute('visible', new THREE.BufferAttribute(new Float32Array(
			visible), 1));

		var vertex_shader =
			"\
	           uniform float scale;\
	           attribute vec3 color;\
	   		attribute float visible;\
	           attribute float pointSize;\
	           varying vec3 vColor;\
	           \
	           void main() {\
	               vColor = color;\
	               vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );\
	               gl_PointSize = visible * pointSize * ( scale / length( mvPosition.xyz ));\
	               gl_Position = projectionMatrix * mvPosition;\
	           }\
	       ";

		var fragment_shader =
			"\
	           varying vec3 vColor;\
	           \
	           void main() {\
	   		vec3 outlineColor = vec3(0.3, 0.3, 0.3);\
	           if (length(gl_PointCoord*2.0 - 1.0) > 1.0)\
	               discard;\
	   		else if (length(gl_PointCoord*2.0 - 1.0) > 0.9)\
	   		    gl_FragColor = vec4(outlineColor, 1.0);\
	   		else\
	           	gl_FragColor = vec4( vColor,  1.0);\
	       }\
	       ";


		var shaderMaterial = new THREE.ShaderMaterial({
			uniforms: {
				'scale': {
					'type': 'f',
					'value': 250
				}
			},
			vertexShader: vertex_shader,
			fragmentShader: fragment_shader,
			transparent: false
		});
		this.material = shaderMaterial;
		// This is a parameter we need to scale things properly
		// https://github.com/mrdoob/three.js/blob/2d59713328c421c3edfc3feda1b116af13140b94/src/renderers/WebGLRenderer.js
		// uniforms.scale.value = _canvas.height / 2.0;


		this.particleSystem = new THREE.Points(this.geometry, shaderMaterial);

		this.update = function(options) {
			var coordinates = options.coordinates;

			if (options.coordinates != undefined) {
				this.geometry.attributes.position.array = coordinates;
				this.geometry.attributes.position.needsUpdate = true;
			}

			if (options.colors != undefined) {
				this.geometry.attributes.color.array = hexColorsToArray(options.colors);
				this.geometry.attributes.color.needsUpdate = true;
			}

			if (options.sizes != undefined) {
				this.geometry.attributes.pointSize.array = new Float32Array(options.sizes);
				this.geometry.attributes.pointSize.needsUpdate = true;
			}

			if (options.visible != undefined) {
				this.geometry.attributes.visible.array = new Float32Array(options.visible);
				this.geometry.attributes.visible.needsUpdate = true;
			}
		};

		this.addToScene = function(scene) {
			scene.add(this.particleSystem);
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.particleSystem);
		};

		this.onResize = function(width, height) {
			this.material.uniforms.scale.value = height / 2.0;
		};

		this.serialize = function() {
			var json = {};
			json.type = 'points';
			json.options = {
				coordinates: {
					type: "float32",
					data: encode(this.options.coordinates.buffer)
				},
				colors: {
					type: "uint32",
					data: encode(new Uint32Array(this.options.colors).buffer)
				},
				sizes: {
					type: "float32",
					data: encode(new Float32Array(this.options.sizes).buffer)
				}
			};
			return json;
		};
	};

	PointsRepresentation.deserialize = function(json) {
		return new PointsRepresentation(deserialize_array(json.options.coordinates),
			deserialize_array(json.options.colors),
			deserialize_array(json.options.sizes));
	};

	/** Flat lines in space given a start and end coordinate of each line.
	 *
	 *  :param Float32Array startCoords: A flattened array of the coordinates where the lines start.
	 *  :param Float32Array endCoords: The end coordinates
	 *  :param list startColors: The colors of the start coordinate
	 *  :param list endColors: The end color of the end coordinate
	 */
	var LineRepresentation = function(startCoords, endCoords, startColors,
		endColors) {
		// Initialize stuff for serialization
		this.type = "lines";
		this.options = {
			startCoords: startCoords,
			endCoords: endCoords,
			startColors: startColors,
			endColors: endColors
		};


		var geo = new THREE.Geometry();
		for (var i = 0; i < startCoords.length / 3; i++) {
			geo.vertices.push(new THREE.Vector3(startCoords[3 * i + 0],
				startCoords[3 * i + 1],
				startCoords[3 * i + 2]));
			geo.colors.push(new THREE.Color(startColors[i]));

			geo.vertices.push(new THREE.Vector3(endCoords[3 * i + 0],
				endCoords[3 * i + 1],
				endCoords[3 * i + 2]));
			geo.colors.push(new THREE.Color(endColors[i]));
		}

		var material = new THREE.LineBasicMaterial({
			color: 0xffffff,
			vertexColors: THREE.VertexColors,
		});

		this.lines = new THREE.LineSegments(geo, material);
		this.lines.geometry.dynamic = true;

		this.update = function(options) {
			if (options.startCoords != undefined || options.endCoords != undefined) {
				var geo = this.lines.geometry,
					startCoords = options.startCoords,
					endCoords = options.endCoords;

				for (var i = 0; i < startCoords.length / 3; i++) {
					geo.vertices[2 * i].set(startCoords[3 * i + 0],
						startCoords[3 * i + 1],
						startCoords[3 * i + 2]);

					geo.vertices[2 * i + 1].set(endCoords[3 * i + 0],
						endCoords[3 * i + 1],
						endCoords[3 * i + 2]);
				}
				geo.verticesNeedUpdate = true;
			}
		};

		this.addToScene = function(scene) {
			scene.add(this.lines);
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.lines);
		};

		this.serialize = function() {
			var json = {};
			json.type = 'lines';
			json.options = {
				startCoords: {
					type: "float32",
					data: encode(this.options.startCoords.buffer)
				},
				endCoords: {
					type: "float32",
					data: encode(this.options.endCoords.buffer)
				},
				startColors: {
					type: "uint32",
					data: encode(new Uint32Array(this.options.startColors).buffer)
				},
				endColors: {
					type: "uint32",
					data: encode(new Uint32Array(this.options.endColors).buffer)
				}
			};
			return json;
		};
	};

	LineRepresentation.deserialize = function(json) {
		return new LineRepresentation(deserialize_array(json.options.startCoords),
			deserialize_array(json.options.endCoords),
			deserialize_array(json.options.startColors),
			deserialize_array(json.options.endColors));
	};


	/**
	 *  SurfaceRepresentation displays a surface
	 */
	var SurfaceRepresentation = function(verts, faces, style, color) {
		// Initialize stuff for serialization
		this.type = "surface";
		this.options = {
			verts: verts,
			faces: faces,
			style: style,
			color: color,
		};


		var DEFAULT_STYLE = "wireframe";
		var DEFAULT_COLOR = 0Xffffff;

		var style = style != undefined ? style : DEFAULT_STYLE;
		var color = color != undefined ? color : DEFAULT_COLOR;

		if (style == "solid") {
			var material = new THREE.MeshPhongMaterial({
				color: color,
				specular: 0xffffff,
				shininess: 1
			});
		}

		if (style == "wireframe") {
			var material = new THREE.MeshBasicMaterial({
				wireframe: true,
				color: color
			});
		}

		if (style == "transparent") {
			var material = new THREE.MeshBasicMaterial({
				color: color,
				transparent: true,
				opacity: 0.5,
				blending: THREE.AdditiveBlending
			})
		}

		var geometry = new THREE.Geometry();

		for (var i = 0; i < verts.length / 3; i++) {
			geometry.vertices.push(new THREE.Vector3(verts[i * 3 + 0],
				verts[i * 3 + 1],
				verts[i * 3 + 2]));
		}

		for (var i = 0; i < faces.length / 3; i++) {
			geometry.faces.push(new THREE.Face3(faces[i * 3 + 0],
				faces[i * 3 + 1],
				faces[i * 3 + 2]));
		}

		geometry.mergeVertices();
		geometry.computeFaceNormals();
		geometry.computeVertexNormals();
		this.mesh = new THREE.Mesh(geometry, material);

		this.addToScene = function(scene) {
			scene.add(this.mesh);
		};

		this.update = function(data) {
			// Nothing
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.mesh);
		};

	};

	/** Spheres
	 */
	var SphereRepresentation = function(coordinates, radii, colors, resolution) {
		// Initialize stuff for serialization
		this.type = "spheres";
		this.options = {
			coordinates: coordinates,
			radii: radii,
			colors: colors,
			resolution: resolution
		};

		if (resolution == undefined)
			resolution = 16;

		var sphereTemplate = new THREE.SphereGeometry(1, resolution, resolution); // Our template

		// We want to have a single geometry to be updated, for speed reasons
		var geometry = new THREE.Geometry();
		for (var i = 0; i < coordinates.length / 3; i++) {
			for (var j = 0; j < sphereTemplate.vertices.length; j++) {
				var vertex = new THREE.Vector3();

				vertex.copy(sphereTemplate.vertices[j]);
				vertex.multiplyScalar(radii[i]);
				vertex.add(new THREE.Vector3(coordinates[3 * i + 0],
					coordinates[3 * i + 1],
					coordinates[3 * i + 2]));
				geometry.vertices.push(vertex);
				geometry.colors.push(new THREE.Color(colors[i]));
			}

			for (var j = 0; j < sphereTemplate.faces.length; j++) {
				var face = sphereTemplate.faces[j].clone();
				face.a += sphereTemplate.vertices.length * i;
				face.b += sphereTemplate.vertices.length * i;
				face.c += sphereTemplate.vertices.length * i;
				face.color.setHex(colors[i]);
				geometry.faces.push(face);
			}

		}

		var material = new THREE.MeshPhongMaterial({
			color: 0xffffff,
			vertexColors: THREE.VertexColors
		});
		this.mesh = new THREE.Mesh(geometry, material);

		this.addToScene = function(scene) {
			scene.add(this.mesh);
		}

		this.update = function(options) {
			if (options.coordinates != undefined) {
				var coordinates = options.coordinates;

				for (var i = 0; i < coordinates.length / 3; i++) {
					for (var j = 0; j < sphereTemplate.vertices.length; j++) {
						var vertex = new THREE.Vector3();

						vertex.copy(sphereTemplate.vertices[j]);
						vertex.multiplyScalar(radii[i]);
						vertex.add(new THREE.Vector3(coordinates[3 * i + 0],
							coordinates[3 * i + 1],
							coordinates[3 * i + 2]));

						var offset = i * sphereTemplate.vertices.length;
						geometry.vertices[offset + j].copy(vertex);
					}
				}
				geometry.verticesNeedUpdate = true;
			}
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.mesh);
		};
	};

	/** Draw a single box in the viewer (useful for bounding boxes and alike) */
	var BoxRepresentation = function(start, end, color) {
		var geometry = new THREE.Geometry();
		var vS = new THREE.Vector3(start[0], start[1], start[2]);
		var vE = new THREE.Vector3(end[0], end[1], end[2]);

		geometry.vertices.push(vS);
		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vS.z));

		geometry.vertices.push(vS);
		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vS.z));

		geometry.vertices.push(vS);
		geometry.vertices.push(new THREE.Vector3(vS.x, vS.y, vE.z));

		geometry.vertices.push(vE);
		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vE.z));

		geometry.vertices.push(vE);
		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vE.z));

		geometry.vertices.push(vE);
		geometry.vertices.push(new THREE.Vector3(vE.x, vE.y, vS.z));

		geometry.vertices.push(new THREE.Vector3(vE.x, vE.y, vS.z));
		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vS.z));

		geometry.vertices.push(new THREE.Vector3(vE.x, vE.y, vS.z));
		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vS.z));

		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vE.z));
		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vS.z));

		geometry.vertices.push(new THREE.Vector3(vE.x, vS.y, vE.z));
		geometry.vertices.push(new THREE.Vector3(vS.x, vS.y, vE.z));

		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vE.z));
		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vS.z));

		geometry.vertices.push(new THREE.Vector3(vS.x, vE.y, vE.z));
		geometry.vertices.push(new THREE.Vector3(vS.x, vS.y, vE.z));

		var material = new THREE.LineBasicMaterial({
			color: color
		});
		var cube = new THREE.Line(geometry, material, THREE.LinePieces);
		this.cube = cube;

		this.addToScene = function(scene) {
			scene.add(this.cube);
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.cube);
		};

		this.update = function(options) {};
	};


	var SmoothLineRepresentation = function(coordinates, color, resolution) {
		// Initialize stuff for serialization
		this.type = "smoothline";
		this.options = {
			coordinates: coordinates,
			color: color,
			resolution: resolution
		};


		var resolution = (resolution != undefined) ? resolution : 16;
		var color = (color != undefined) ? color : 0xffffff;
		this.resolution = resolution;
		// We could use our friendly splite provided by threejs
		var points = []
		for (var i = 0; i < coordinates.length / 3; i++) {
			points.push(new THREE.Vector3(coordinates[3 * i + 0],
				coordinates[3 * i + 1],
				coordinates[3 * i + 2]));
		}
		var path = new THREE.CatmullRomCurve3(points);

		var geometry = new THREE.Geometry();
		geometry.vertices = path.getPoints(resolution * points.length);

		var material = new THREE.LineBasicMaterial({
			color: color,
			fog: true
		});

		this.geometry = geometry;
		this.material = material;

		this.line = new THREE.Line(geometry, material);

		this.addToScene = function(scene) {
			scene.add(this.line);
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.line);
		};

		this.update = function(options) {

			if (options.coordinates != undefined) {
				var coordinates = options.coordinates;

				// Regenerate the spline geometry
				var points = [];
				for (var i = 0; i < coordinates.length / 3; i++) {
					points.push(new THREE.Vector3(coordinates[3 * i + 0],
						coordinates[3 * i + 1],
						coordinates[3 * i + 2]));
				}
				var path = new THREE.CatmullRomCurve3(points);
				this.geometry.vertices = path.getPoints(resolution * points.length);
				this.geometry.verticesNeedUpdate = true;
			}
		};
	};

	var SmoothTubeRepresentation = function(coordinates, radius, color,
		resolution) {
		// Initialize stuff for serialization
		this.type = "smoothtube";
		this.options = {
			coordinates: coordinates,
			radius: radius,
			color: color,
			resolution: resolution
		};


		var resolution = (resolution != undefined) ? resolution : 4;
		var color = (color != undefined) ? color : 0xffffff;
		this.resolution = resolution;
		var CIRCLE_RESOLUTION = 8;

		// We could use our friendly splite provided by threejs
		var points = []
		for (var i = 0; i < coordinates.length / 3; i++) {
			points.push(new THREE.Vector3(coordinates[3 * i + 0],
				coordinates[3 * i + 1],
				coordinates[3 * i + 2]));
		}
		var path = new THREE.CatmullRomCurve3(points);

		var geometry = new THREE.TubeGeometry(path, resolution * points.length,
			radius, CIRCLE_RESOLUTION, false);
		var material = new THREE.MeshPhongMaterial({
			color: color,
			fog: true
		});

		this.geometry = geometry;
		this.material = material;

		this.mesh = new THREE.Mesh(geometry, material);

		this.addToScene = function(scene) {
			scene.add(this.mesh);
		};

		this.removeFromScene = function(scene) {
			scene.remove(this.mesh);
		};

		this.update = function(options) {

			if (options.coordinates != undefined) {
				var coordinates = options.coordinates;

				// Regenerate the spline geometry
				var points = []
				for (var i = 0; i < coordinates.length / 3; i++) {
					points.push(new THREE.Vector3(coordinates[3 * i + 0],
						coordinates[3 * i + 1],
						coordinates[3 * i + 2]));
				}
				var path = new THREE.SplineCurve3(points);

				var geometry = new THREE.TubeGeometry(path, resolution * points.length,
					radius, CIRCLE_RESOLUTION, false);
				this.geometry.vertices = geometry.vertices;
				this.geometry.verticesNeedUpdate = true;
			}
		};

		this.serialize = function() {
			var json = {};
			json.type = 'smoothtube';
			json.options = {
				coordinates: {
					type: "float32",
					data: encode(this.options.coordinates.buffer)
				},
				radius: this.options.radius,
				color: this.options.color,
				resolution: this.options.resolution
			};
			return json;
		};
	};

	SmoothTubeRepresentation.deserialize = function(json) {
		return new SmoothTubeRepresentation(deserialize_array(json.options.coordinates),
			json.options.radius,
			json.options.color,
			json.options.resolution);
	};

	/**
	 * Draw a series of solid cylinders given their start/end coordinates, radii and colors.
	 *
	 * This is to be used sparingly (max ~100 cylinders because it's inefficient). If you need to render bonds, use
	 * the LineRepresentation class, much much faster.
	 *
	 * :param Float32Array startCoords:
	 * :param Float32Array endCoords:
	 * :param list radii:
	 * :param list colors:
	 */
	var CylinderRepresentation = function(startCoords, endCoords, radii, colors,
		resolution) {
		// Initialize stuff for serialization
		this.type = "cylinders";
		this.options = {
			startCoords: startCoords,
			endCoords: endCoords,
			radii: radii,
			colors: colors,
			resolution: resolution
		};

		var resolution = (resolution != undefined) ? resolution : 16;
		var cylinders = [];

		for (var i = 0; i < startCoords.length / 3; i++) {
			var startVec = new THREE.Vector3(startCoords[3 * i + 0],
				startCoords[3 * i + 1],
				startCoords[3 * i + 2]);

			var endVec = new THREE.Vector3(endCoords[3 * i + 0],
				endCoords[3 * i + 1],
				endCoords[3 * i + 2]);

			var length = startVec.distanceTo(endVec);

			var geometry = new THREE.CylinderGeometry(radii[i], radii[i], length,
				resolution);
			var material = new THREE.MeshPhongMaterial({
				color: colors[i]
			});

			// Rotate the geometry vertices to align the cylinder with the z-axis
			var orientation = new THREE.Matrix4();
			orientation.makeRotationFromEuler(new THREE.Euler(-Math.PI * 0.5, 0, 0,
				'XYZ')); //rotate on X 90 degrees
			orientation.setPosition(new THREE.Vector3(0, 0, 0.5 * length)); //move half way on Z, since default pivot is at centre
			geometry.applyMatrix(orientation); //apply transformation for geometry

			// Position the cylinder normally
			var cylinder = new THREE.Mesh(geometry, material);
			cylinder.position.copy(startVec);
			cylinder.lookAt(endVec);

			cylinders.push(cylinder);
		}

		this.addToScene = function(scene) {
			for (var i = 0; i < cylinders.length; i++) {
				scene.add(cylinders[i]);
			}
		};

		this.removeFromScene = function(scene) {
			for (var i = 0; i < cylinders.length; i++) {
				scene.remove(cylinders[i]);
			}
		};

		this.update = function(options) {

			if (options.startCoords != undefined || options.endCoords != undefined) {
				var startCoords = options.startCoords;
				var endCoords = options.endCoords;

				for (var i = 0; i < startCoords.length / 3; i++) {
					var startVec = new THREE.Vector3(startCoords[3 * i + 0],
						startCoords[3 * i + 1],
						startCoords[3 * i + 2]);

					var endVec = new THREE.Vector3(endCoords[3 * i + 0],
						endCoords[3 * i + 1],
						endCoords[3 * i + 2]);
					var cylinder = cylinders[i];
					cylinder.position.copy(startVec);
					cylinder.lookAt(endVec);
					cylinder.geometry.verticesNeedUpdate = true;
				}
			}
		};

		this.serialize = function() {
			var json = {};
			json.type = 'cylinders';
			json.options = {
				startCoords: {
					type: "float32",
					data: encode(this.options.startCoords.buffer)
				},
				endCoords: {
					type: "float32",
					data: encode(this.options.endCoords.buffer)
				},
				radii: {
					type: "float32",
					data: encode(new Float32Array(this.options.radii).buffer)
				},
				colors: {
					type: "uint32",
					data: encode(new Uint32Array(this.options.colors).buffer)
				},
				resolution: this.options.resolution
			};
			return json;
		};

	};

	CylinderRepresentation.deserialize = function(json) {
		return new CylinderRepresentation(deserialize_array(json.options.startCoords),
			deserialize_array(json.options.endCoords),
			deserialize_array(json.options.radii),
			deserialize_array(json.options.colors),
			json.options.resolution);
	};


	var RibbonRepresentation = function(coords, normals, color, resolution,
		width, height,
		arrow) {
		// Get arrays of THREE.Vector3 objects 
		coords = arrayToThreeVecs(coords);
		normals = arrayToThreeVecs(normals);
		if (width == undefined)
			width = 0.2

		if (color == undefined)
			color = 0xffffff

		if (height == undefined)
			height = 0.05

		if (arrow == undefined)
			arrow = false

		var numPoints = resolution * coords.length;

		// Make splines
		var pSpline = new THREE.CatmullRomCurve3(coords);
		var nSpline = new THREE.CatmullRomCurve3(normals);

		// Interpolate points and normals
		var iPoints = pSpline.getPoints(numPoints);
		var iNormals = nSpline.getPoints(numPoints);

		// Renormalize normals 
		iNormals.map(function(x) {
			x.normalize()
		});
		realignNormals(iNormals);


		// We need to add an extra point to make room for the arrow transition
		// TODO: normal is not right
		// if (arrow) {
		// 	var arrowHeadStartIndex = iPoints.length - resolution + 1;
		// 	iPoints.splice(arrowHeadStartIndex, 0, iPoints[arrowHeadStartIndex]);
		// 	iNormals.splice(arrowHeadStartIndex, 0, iNormals[arrowHeadStartIndex]);
		// 	
		// }

		// iPoints[iPoints.length] = iPoints[iPoints.length - 1];
		// iNormals[iNormals.length] = iNormals[iNormals.length - 1];

		var geometry = new THREE.Geometry();

		// Generate vertices
		for (var i = 0; i < iPoints.length - 1; i++) {

			if (arrow) {
				//  We interpolate the width to 0

				var offset = i + resolution - iPoints.length;
				var iWidth = offset < 0 ? width : width * 2.0;
				iWidth = iWidth * (1 - Math.max(0, offset) / resolution);
			} else {
				var iWidth = width;
			}

			var tangent = new THREE.Vector3().subVectors(iPoints[i + 1], iPoints[i]).normalize();
			var sideDirection = orthogonalVec(tangent, iNormals[i]).normalize().multiplyScalar(
				iWidth / 2);
			var r1 = new THREE.Vector3().addVectors(iPoints[i], sideDirection);
			var l1 = new THREE.Vector3().subVectors(iPoints[i], sideDirection);

			var upDirection = orthogonalVec(sideDirection, tangent).multiplyScalar(
				height);
			var r2 = new THREE.Vector3().addVectors(r1, upDirection);
			var l2 = new THREE.Vector3().addVectors(l1, upDirection);

			// Bottom ribbon
			geometry.vertices.push(r1, l1);

			// Top ribbon
			geometry.vertices.push(r2, l2)
		}

		var trianglesTpl = [
			[0, 5, 4],
			[0, 1, 5], // Bottom face
			[3, 7, 2],
			[2, 7, 6], // Top face
			[1, 7, 3],
			[1, 5, 7], // Left
			[0, 6, 2],
			[0, 4, 6], // Right
		];
		// Connect the previously generated vertices through a triangle strip
		for (var i = 0; i < iPoints.length * 4 - 16; i += 2) {
			// geometry.faces.push(new THREE.Face3(i, i+2, i+1, iNormals[i]));
			// geometry.faces.push(new THREE.Face3(i+1, i+2, i+3, iNormals[i]));
			for (var t of trianglesTpl)
				geometry.faces.push(new THREE.Face3(i + t[0], i + t[1], i + t[2]));
		}

		geometry.computeFaceNormals();
		geometry.computeVertexNormals();
		var material = new THREE.MeshPhongMaterial({
			color: color,
			side: THREE.DoubleSide
		});
		var mesh2 = new THREE.Mesh(geometry, material);

		this.addToScene = function(scene) {
			// Display normals
			// for (var i=0; i < coords.length; i++) {
			// 	scene.add(new THREE.ArrowHelper(normals[i], coords[i], 0.1));
			// }

			// scene.add(mesh);
			scene.add(mesh2);
		};

		this.removeFromScene = function(scene) {
			scene.remove(mesh);
		};

		this.update = function(options) {

		};
	};


	var orthogonalVec = function(a, b) {
		return new THREE.Vector3().crossVectors(a.clone().normalize(), b.clone().normalize());
	};

	var threeVecsToArray = function(vectors) {
		var coords = [];
		for (var v of vectors) {
			coords.push(v.x, v.y, v.z);
		}
		return new Float32Array(coords);
	};

	var arrayToThreeVecs = function(array) {
		var retVal = [];

		for (var i = 0; i < array.length / 3; i++) {
			retVal.push(new THREE.Vector3(array[3 * i + 0],
				array[3 * i + 1],
				array[3 * i + 2]));
		}

		return retVal;
	};

	var hexColorsToArray = function(colors) {
		var colorsVert = new Float32Array(colors.length * 3);
		for (var i = 0; i < colors.length; i++) {
			var c = new THREE.Color(colors[i]);
			colorsVert[3 * i] = c.r;
			colorsVert[3 * i + 1] = c.g;
			colorsVert[3 * i + 2] = c.b;
		}
		return colorsVert;
	};

	var realignNormals = function(normals) {
		for (var i = 0; i < normals.length - 1; i++) {

			if (normals[i].dot(normals[i + 1]) < 0) {
				normals[i + 1].negate();
			}
		}
	};

	// Utilities
	var deserialize_array = function(json) {
		var buffer = decode(json.data);
		if (json.type == 'uint8') {
			return new Uint8Array(buffer);
		} else if (json.type == 'float32') {
			return new Float32Array(buffer);
		} else if (json.type == 'uint32') {
			return new Uint32Array(buffer);
		}


	};
	return {
		MolecularViewer: MolecularViewer,
		PointsRepresentation: PointsRepresentation,
		LineRepresentation: LineRepresentation,
		SurfaceRepresentation: SurfaceRepresentation,
		SphereRepresentation: SphereRepresentation,
		BoxRepresentation: BoxRepresentation,
		SmoothLineRepresentation: SmoothLineRepresentation,
		SmoothTubeRepresentation: SmoothTubeRepresentation,
		CylinderRepresentation: CylinderRepresentation,
		RibbonRepresentation: RibbonRepresentation
	};
});
