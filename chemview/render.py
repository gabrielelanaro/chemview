'''Utilities for rendering'''
from __future__ import division, print_function
from .scene import normalize_scene

import numpy as np
import math
import json

try:
    import vapory as vp
    vapory_available = True
except ImportError:
    ImportWarning("Vapory is not available. Rendering publication quality images "
                  "will not work.")
    vapory_available = False



__all__ = ['render_povray']

def render_povray(scene, filename='ipython', width=600, height=600,
                  antialiasing=0.01, extra_opts={}):
    '''Render the scene with povray for publication.

    :param dict scene: The scene to render
    :param string filename: Output filename or 'ipython' to render in the notebook.
    :param int width: Width in pixels.
    :param int height: Height in pixels.
    :param dict extra_opts: Dictionary to merge/override with the passed scene.
    '''
    if not vapory_available:
        raise Exception("To render with povray, you need to have the vapory"
                        " package installed.")

    # Adding extra options
    scene = normalize_scene(scene)
    scene.update(extra_opts)

    # Camera target
    aspect = scene['camera']['aspect']
    up = np.dot(rmatrixquaternion(scene['camera']['quaternion']), [0, 1, 0])
    v_fov = scene['camera']['vfov']  / 180.0 * np.pi
    h_fov = 2.0 * np.arctan(np.tan(v_fov/2.0) * aspect) / np.pi * 180
    # Setup camera position
    camera = vp.Camera( 'location', scene['camera']['location'],
                        'direction', [0, 0, -1],
                        'sky', up,
                        'look_at', scene['camera']['target'],
                        'angle', h_fov )

    global_settings = []
    # Setup global illumination
    if scene.get('radiosity', False):
        # Global Illumination
        radiosity = vp.Radiosity(
                    'brightness', 2.0,
                    'count', 100,
                    'error_bound', 0.15,
                    'gray_threshold', 0.0,
                    'low_error_factor', 0.2,
                    'minimum_reuse', 0.015,
                    'nearest_count', 10,
                    'recursion_limit', 1, #Docs say 1 is enough
                    'adc_bailout', 0.01,
                    'max_sample', 0.5,
                    'media off',
                    'normal off',
                    'always_sample', 1,
                    'pretrace_start', 0.08,
                    'pretrace_end', 0.01)

        light_sources = []
        global_settings.append(radiosity)
    else:
        # Lights
        light_sources = [
                        vp.LightSource( np.array([2,4,-3]) * 1000, 'color', [1,1,1] ),
                        vp.LightSource( np.array([-2,-4,3]) * 1000, 'color', [1,1,1] ),
                        vp.LightSource( np.array([-1,2,3]) * 1000, 'color', [1,1,1] ),
                        vp.LightSource( np.array([1,-2,-3]) * 1000, 'color', [1,1,1] )
        ]

    # Background -- white for now
    background = vp.Background([1, 1, 1])

    # Things to display
    stuff = _generate_objects(scene['representations'])

    scene = vp.Scene( camera, objects = light_sources + stuff + [background],
                      global_settings=global_settings)

    return scene.render(filename, width=width, height=height,
                        antialiasing = antialiasing)

    

def _generate_objects(representations):
    objects = []

    for rep in representations:
        if rep['rep_type'] == 'spheres':
            for i, (x, y, z) in enumerate(rep['options']['coordinates']):
                r = rep['options']['radii'][i]
                c = rep['options']['colors'][i]
                # Generate the shape
                sphere = vp.Sphere( [x,y,z] , r, vp.Texture( vp.Pigment( 'color', hex2rgb(c)) ))
                objects.append(sphere)

        elif rep['rep_type'] == 'points':
            # Render points as small spheres
            for i, (x, y, z) in enumerate(rep['options']['coordinates']):
                c = rep['options']['colors'][i]
                s = rep['options']['sizes'][i]
                if not 'alpha' in rep['options']:
                    t = 1.0
                else:
                    t = rep['options']['alpha'][i]

                # Point = sphere with a small radius
                sphere = vp.Sphere( [x,y,z] , s * 0.15,
                                    vp.Texture( vp.Pigment( 'color', 'rgbf', hex2rgb(c) + (1-t,))),
                                    vp.Interior('ior', 1.0))
                objects.append(sphere)

        elif rep['rep_type'] == 'surface':
            verts = rep['options']['verts']
            faces = rep['options']['faces']
            color = rep['options']['color']
            triangles = verts.take(faces, axis=0)

            for v1, v2, v3 in triangles:
                povt = vp.Triangle(v1.tolist(),
                                   v2.tolist(),
                                   v3.tolist(),
                                   vp.Texture(vp.Pigment('color', hex2rgb(color))))
                objects.append(povt)

        elif rep['rep_type'] == 'cylinders':
            start = rep['options']['startCoords']
            end = rep['options']['endCoords']
            colors = rep['options']['colors']

            for i, (s, e) in enumerate(zip(start, end)):
                r = rep['options']['radii'][i]
                c = rep['options']['colors'][i]
                t = _get_transparency(rep['options'], i)

                cylinder = vp.Cylinder(s.tolist(), e.tolist(), r,
                                       vp.Texture(vp.Pigment('color', 'rgbf', hex2rgb(c) + (1 - t,))))
                objects.append(cylinder)

        elif rep['rep_type'] == 'lines':
            start = rep['options']['startCoords']
            end = rep['options']['endCoords']
            colors = rep['options']['startColors']

            for i, (s, e) in enumerate(zip(start, end)):
                #r = rep['options']['radii'][i]
                r = 0.02
                c = colors[i]
                t = _get_transparency(rep['options'], i)

                cylinder = vp.Cylinder(s.tolist(), e.tolist(), r,
                                       vp.Texture(vp.Pigment('color', 'rgbf', hex2rgb(c) + (1 - t,))))
                objects.append(cylinder)

        else:
            raise ValueError("No support for representation rep_type: %s" % rep['rep_type'])

    return objects

def _get_transparency(opts, i):
    t = opts.get('transparency', 1.0)
    if hasattr(t, "__len__"): # Array test
        t = t[i]
    return t

def hex2rgb(hex):
    return ((hex >> 16) & 0xff)/255, ((hex >> 8) & 0xff)/255, (hex & 0x0000ff)/255

def rmatrixquaternion(q):
    """Create a rotation matrix from q quaternion rotation.
    Quaternions are typed as Numeric Python numpy.arrays of length 4.
    """
    assert np.allclose(math.sqrt(np.dot(q,q)), 1.0)

    x, y, z, w = q

    xx = x*x
    xy = x*y
    xz = x*z
    xw = x*w
    yy = y*y
    yz = y*z
    yw = y*w
    zz = z*z
    zw = z*w

    r00 = 1.0 - 2.0 * (yy + zz)
    r01 =       2.0 * (xy - zw)
    r02 =       2.0 * (xz + yw)

    r10 =       2.0 * (xy + zw)
    r11 = 1.0 - 2.0 * (xx + zz)
    r12 =       2.0 * (yz - xw)

    r20 =       2.0 * (xz - yw)
    r21 =       2.0 * (yz + xw)
    r22 = 1.0 - 2.0 * (xx + yy)

    R = np.array([[r00, r01, r02],
               [r10, r11, r12],
               [r20, r21, r22]], float)

    assert np.allclose(np.linalg.det(R), 1.0)
    return R
