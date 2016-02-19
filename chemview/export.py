'''Static export for viewing in  nbviewer (or the web)'''
import json
import os
import numpy as np

from .scene import normalize_scene
from .utils import encode_numpy

def export_html(export_dir, scene):
    raise NotImplementedError()
    
    # We validate the input to make it complete
    scene = normalize_scene(scene)
    
    # The scene gets json-serialized
    scene_js = json.dumps(serialize_to_dict(scene))
    
    os.mkdir(export_dir)
    with open(os.path.join(export_dir, 'scene.js'), 'w') as fd:
        fd.write(scene_js)
    
    template = '''
    
    '''
    

def serialize_to_dict(dictionary):
    '''Make a json-serializable dictionary from input dictionary by converting
    non-serializable data types such as numpy arrays.'''
    retval = {}
    
    for k, v in dictionary.items():
        if isinstance(v, dict):
            retval[k] = serialize_to_dict(v)
        else:
            # This is when custom serialization happens
            if isinstance(v, np.ndarray):
                if v.dtype == 'float64':
                    # We don't support float64 on js side
                    v = v.astype('float32')

                retval[k] = encode_numpy(v)
            else:
                retval[k] = v
    
    return retval
