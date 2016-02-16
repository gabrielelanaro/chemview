# Testing povray backend
import numpy as np
from chemview.render import render_povray
from chemview.scene import normalize_scene
from nose.tools import eq_, assert_raises
# We need some scene normalization

coordinates = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 2]], dtype='float32')
def test_points():
    scene = {'representations': [{"rep_id" : 1,
                                  "rep_type" : 'points',
                                  "options" : {"coordinates": coordinates}}]}
    render_povray(scene, 'tmp.png')


def test_spheres():
    scene = {'representations': [{"rep_id" : 1,
    "rep_type" : 'spheres',
    "options" : {"coordinates": coordinates}}]}
    render_povray(scene, 'tmp.png')

def test_lines():
    scene = {'representations': [{"rep_id" : 1,
    "rep_type" : 'lines',
    "options" : {"startCoords": coordinates,
    "endCoords": coordinates + 1}}]}
    render_povray(scene, 'tmp.png')
        
def test_cylinders():
    scene = {'representations': [{"rep_id" : 1,
    "rep_type" : 'cylinders',
    "options" : {"startCoords": coordinates,
    "endCoords": coordinates + 1}}]}
    render_povray(scene, 'tmp.png')

def test_smoothtube():
    scene = {'representations': [{"rep_id" : 1,
    "rep_type" : 'smoothtube',
    "options" : {"coordinates": coordinates}}]}
    
    with assert_raises(ValueError):
        render_povray(scene, 'tmp.png')
