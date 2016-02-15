from __future__ import print_function
import numpy as np
from nose.tools import eq_, assert_raises
from chemview.scene import normalize_scene, ValidationError

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

    
def test_camera_validation():
    scene = {'camera': {"aspect" : -1}}
    
    with assert_raises(ValidationError):
        nscene = normalize_scene(scene)
