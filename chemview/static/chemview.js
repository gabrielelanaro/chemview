

var MolecularViewer = function ($el) {
	/* A MolecularViewer displays and manages a set of representations for a chemical system.

	*/

	this.container = $el;
	this.container.widthInv  = 1 / this.container.width();
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
	this.perspectiveCamera = new THREE.PerspectiveCamera(20, this.container.whratio, 1, 800);
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
	this.slabFar  = +50;

	var background = 0x000000;
	this.renderer.setClearColor(background, 1);

	this.scene = new THREE.Scene();
	this.scene.fog = new THREE.Fog(background, 10, 200);

	var directionalLight = new THREE.DirectionalLight(0xFFFFFF, 1.2);
	directionalLight.position.set(0.2, 0.2, -1).normalize();
	var ambientLight = new THREE.AmbientLight(0x202020);
	
	this.scene.add(directionalLight);
	this.scene.add(ambientLight);
	//this.scene.add(this.camera);

	this.controls = new THREE.TrackballControls(this.camera, this.container);
	this.controls.rotateSpeed = 1.0;
	this.controls.zoomSpeed = 1.2;
	this.controls.panSpeed = 0.8;

	this.controls.noZoom = false;
	this.controls.noPan = false;
	this.controls.norRotate = false;

	this.controls.staticMoving = false;
	this.controls.dynamicDampingFactor = 0.2;

	this.controls.keys = [ 65, 83, 68 ];
	this.controls.addEventListener( 'change', this.render.bind(this));

    this.representations = {};
	this.render();
};

MolecularViewer.prototype = {
    
    addRepresentation: function (representation, repId) {
    	representation.addToScene(this.scene);
        this.representations[repId] = representation;
    },

    getRepresentation: function (repId) {
        return this.representations[repId];
    },

    removeRepresentation: function (repId) {
        var rep = this.getRepresentation(repId);
        rep.removeFromScene(this.scene);
    },

    render: function () {
    	if (this.controls.screen.width == 0 || this.controls.screen.height == 0)
    		this.controls.handleResize();

    	this.renderer.render(this.scene, this.camera);
    },

    animate: function () {
    	//console.log(this);

		window.requestAnimationFrame(this.animate.bind(this));
		this.controls.update();

	},

	zoomInto: function (coordinates) {
		/* TODO: this function may be out of place */

		// Calulate current geometric centre
		var cur_gc = new THREE.Vector3(0.0, 0.0, 0.0);
		for (var i = 0; i < coordinates.length/3; i++) {
			cur_gc.x += coordinates[3*i + 0];
			cur_gc.y += coordinates[3*i + 1];
			cur_gc.z += coordinates[3*i + 2];
		}
		cur_gc.divideScalar(coordinates.length/3);

		this.controls.target.copy(cur_gc);


		// Calculate the bounding sphere
		var bound = 0;
		for (var i = 0; i < coordinates.length/3; i++) {
			var point = new THREE.Vector3( coordinates[3*i + 0],
									 coordinates[3*i + 1],
									 coordinates[3*i + 2]);
			bound = Math.max(bound, point.distanceTo(cur_gc));
		}

		var fov_topbottom = this.camera.fov*Math.PI/180.0;
		var dist = (bound + this.camera.near)/Math.tan(fov_topbottom * 0.5);
        
        // Calculate distance vector
        var c = new THREE.Vector3();
        c.subVectors(this.camera.position, this.controls.target);
        c.normalize();

        // move camera at a distance
        c.multiplyScalar(dist);
        this.camera.position.copy(c);
		this.controls.update();
	},

	resize: function (width, height) {
		this.renderer.setSize(width, height);
		this.controls.handleResize();
		this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.render();
	},
};

/** 
 * Represents a set of coordinates as points.
 * 
 * @param coordinates: a (flattened) Float32Array of coordinates in 3D space
 * @param bonds: a (flattened) Int32Array of bonds, represented as 
 *                indices that connects two coordinates
 * @param colors: a list of colors (one for each point) expressed as hexadecimal numbers
 * @param sizes: a list of sizes for the points
 */
var PointLineRepresentation = function (coordinates, bonds, colors, sizes) {

    var DEFAULT_SIZE = 0.15,
        DEFAULT_COLOR = 0xffffff;

    // pre-processing for optional arguments
    if (sizes == undefined) {
        var sizes = [];
        for (var i=0; i < coordinates.length/3; i++) {
            sizes.push(DEFAULT_SIZE);
        }
    }

    if (colors == undefined) {
        var colors = [];
        for (var i=0; i < coordinates.length/3; i++) {
            colors.push(DEFAULT_COLOR);
        }
    }

    if (bonds == undefined) {
        var bonds = [];
    }

	// That is the points part
	var geo = new THREE.Geometry();
    this.geometry = geo;

	var attributes = {

        color: { type: 'c', value: []},
        pointSize: { type: 'f', value: sizes},

    };


	for (var p = 0; p < coordinates.length/3; p++) {
		var particle = new THREE.Vector3(coordinates[3 * p + 0],
										 coordinates[3 * p + 1],
										 coordinates[3 * p + 2]);
		geo.vertices.push(particle);
		attributes.color.value.push(new THREE.Color(colors[p]));
	}

	
	var vertex_shader = "\
	    attribute vec3 color;\
        attribute float pointSize;\
	    varying vec3 vColor;\
    	\
    	void main() {\
       		vColor = color;\
        	vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );\
        	gl_PointSize = pointSize * ( 150.0 / length( mvPosition.xyz ));\
        	gl_Position = projectionMatrix * mvPosition;\
    	}\
    ";

    var fragment_shader = "\
    	varying vec3 vColor;\
    	\
    	void main() {\
    	if (length(gl_PointCoord*2.0 - 1.0) > 1.0)\
    		discard;\
        gl_FragColor = vec4( vColor,  1.0);\
    }\
    ";



    var shaderMaterial = new THREE.ShaderMaterial( {
        attributes:     attributes,
        vertexShader:   vertex_shader,
        fragmentShader: fragment_shader,
        transparent:    false
    });
    this.material = shaderMaterial;

	this.particleSystem = new THREE.PointCloud(this.geometry, shaderMaterial);


	// That is the lines part
   	var geo = new THREE.Geometry();
   	for (var b = 0; b < bonds.length; b++) {
   		var start = this.geometry.vertices[bonds[b][0]];
   		var end = this.geometry.vertices[bonds[b][1]];

   		geo.vertices.push(start);
   		geo.vertices.push(end);
   	}
   	    
   	var material = new THREE.LineBasicMaterial({
        color: 0x0000ff
    });

   	this.lines = new THREE.Line(geo, material, THREE.LinePieces);
   	this.lines.geometry.dynamic = true;

};


PointLineRepresentation.prototype = {

    /** Update the representation with other data
     * Updates supported:
     * - coordinates
     * - sizes
     */
    update: function (data) {

    	var coordinates = data.coordinates;

    	if (data.coordinates != undefined) {
    		// There has been no update in coordinates
	    	for (var p=0; p < coordinates.length/3; p++) {
	    		this.geometry.vertices[p].x = coordinates[3 * p + 0];
	    		this.geometry.vertices[p].y = coordinates[3 * p + 1];
	    		this.geometry.vertices[p].z = coordinates[3 * p + 2];
	    	}

	    	this.particleSystem.geometry.verticesNeedUpdate = true;
	    	this.lines.geometry.verticesNeedUpdate = true;

	    }

	    if (data.sizes != undefined) {
            this.particleSystem.material.attributes.pointSize.value = data.sizes;
            this.particleSystem.material.attributes.pointSize.needsUpdate = true;  
	    }

    },

   	addToScene: function(scene) {
   		scene.add(this.particleSystem);
   		scene.add(this.lines);
   	},

    removeFromScene: function(scene) {
        scene.remove(this.particleSystem);
        scene.remove(this.lines);
    },
};

\/**
  *  SurfaceRepresentation displays a surface
  */
var SurfaceRepresentation = function (verts, faces, style) {

    var DEFAULT_STYLE = "wireframe";
    var style = style != undefined ? style : DEFAULT_STYLE;

    if (style == "solid") {
        var material = new THREE.MeshPhongMaterial( { color: 0Xffffff, 
                                                      specular: 0xffffff, 
                                                      shininess: 1});
    }

    if (style == "wireframe") {
        var material = new THREE.MeshBasicMaterial({wireframe:true, color: 0xffffff});
    }

	var geometry = new THREE.Geometry();

	for (var i = 0; i < verts.length/3; i++) {
		geometry.vertices.push(new THREE.Vector3(verts[i * 3 + 0],
												 verts[i * 3 + 1], 
												 verts[i * 3 + 2]));
	}

	for (var i = 0; i < faces.length/3; i++) {
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

	this.update = function (data) {
		// Nothing
	};

    this.removeFromScene = function(scene) {
        scene.remove(this.mesh);
    };

};


var SphereRepresentation = function (coordinates, radii, resolution) {

    if (resolution == undefined)
        resolution = 16;

    var sphereTemplate = new THREE.SphereGeometry(1, resolution, resolution); // Our template

    // We want to have a single geometry to be updated, for speed reasons
    var geometry = new THREE.Geometry();
    for (var i=0; i < coordinates.length/3; i ++) {
        for (var j=0; j < sphereTemplate.vertices.length; j++){
            var vertex = new THREE.Vector3();

            vertex.copy(sphereTemplate.vertices[j]);
            vertex.multiplyScalar(radii[i]);
            vertex.add(new THREE.Vector3(coordinates[3 * i + 0],
                                         coordinates[3 * i + 1],
                                         coordinates[3 * i + 2]));
            geometry.vertices.push(vertex);
            //geometry.normals.push(sphereTemplate.vertices[j]);
        }

        for (var j=0; j < sphereTemplate.faces.length; j++) {
            var face = sphereTemplate.faces[j].clone();
            face.a += sphereTemplate.vertices.length * i;
            face.b += sphereTemplate.vertices.length * i;
            face.c += sphereTemplate.vertices.length * i;

            geometry.faces.push(face);
        }
            
    }
    geometry.computeFaceNormals();
    geometry.computeVertexNormals();

    var material = new THREE.MeshBasicMaterial({wireframe: true, color: 0x00ffff});
    this.mesh = new THREE.Mesh(geometry, material);

    this.addToScene = function (scene) {
        scene.add(this.mesh);
    }

    this.update = function(options) {
        // nothing
    };

    this.removeFromScene = function(scene) {
        scene.remove(this.mesh);
    };
}