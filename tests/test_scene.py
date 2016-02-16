from __future__ import print_function
import numpy as np
from nose.tools import eq_, assert_raises
from chemview.scene import normalize_scene, ValidationError, POINTS_SCHEMA, SPHERES_SCHEMA, validate_schema

def test_normalize_scene():
    coordinates = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 2]], dtype='float32')
    scene = {'representations': [{"rep_id" : 1,
                                  "rep_type" : 'points',
                                  "options" : {"coordinates": coordinates}}]}
    
    nscene = normalize_scene(scene)

    eq_(nscene['camera']['aspect'], 1)
    eq_(nscene['camera']['vfov'], 90)
    eq_(nscene['camera']['location'], [0, 0, -1])
    eq_(nscene['camera']['quaternion'], [0, 0, 0, 1])
    eq_(nscene['camera']['target'], [0, 0, 0])

    eq_(nscene['representations'][0]['options']['colors'], [0xffffff, 0xffffff, 0xffffff])

def test_camera_validation():
    scene = {'camera': {"aspect" : -1}}
    
    with assert_raises(ValidationError):
        nscene = normalize_scene(scene)

def test_points_validation():
    coordinates = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 2]], dtype='float32')
    val = {"rep_id" : 1,
           "rep_type" : 'points',
           "options" : {"coordinates": coordinates}}
     
    nschema = validate_schema(val, POINTS_SCHEMA)
    eq_(nschema['options']['colors'], [0xffffff, 0xffffff, 0xffffff])
    eq_(nschema['options']['sizes'], [0.1, 0.1, 0.1])


def test_spheres_validation():
    coordinates = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 2]], dtype='float32')
    val = {"rep_id" : 1,
           "rep_type" : 'spheres',
           "options" : {"coordinates": coordinates}}
    
    nschema = validate_schema(val, SPHERES_SCHEMA)
    eq_(nschema['options']['colors'], [0xffffff, 0xffffff, 0xffffff])
    eq_(nschema['options']['radii'], [0.1, 0.1, 0.1])
    
