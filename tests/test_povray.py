# Testing povray backend
import numpy as np
from chemview.render import render_povray
from chemview.scene import normalize_scene
from nose.tools import eq_
# We need some scene normalization

def test_points():
    coordinates = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 2]], dtype='float32')
    
    scene = {'representations': [{"rep_id" : 1,
                                  "rep_type" : 'points',
                                  "options" : {"coordinates": coordinates}}]}
    scene = normalize_scene(scene)
    render_povray(scene, 'tmp.png')

def test_lines():
    pass

def test_spheres():
    pass
