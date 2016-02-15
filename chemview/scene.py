'''Scene validation utilities'''
import operator

class Validator(object):
    
    def validate(self, value):
        pass
    
    def cast(self, value):
        pass


class BoundedScalar(Validator):
    
    def __init__(self, start, end, type, ginclusive=True, linclusive=True):
        self.start = start
        self.end = end
        self.ginclusive = ginclusive
        self.linclusive = linclusive
        self.type = type
        
    def validate(self, value):
        lo = operator.le if self.linclusive else operator.lt
        go = operator.ge if self.ginclusive else operator.gt
        
        return go(value, self.start) and lo(value, self.end), 'should be between {} and {}'.format(self.start, self.end)
    
    def cast(self, value):
        return self.type(value)

class ListOf(Validator):
    
    def __init__(self, type, length=None):
        self.type = type
        self.length = length
    
    def validate(self, value):
        # We check the first element only
        length_condition = True if self.length is None else len(value) == self.length
        
        if len(value) == 0:
            type_condition = True
        else:
            type_condition = isinstance(value[0], self.type)
        
        return length_condition and type_condition, 'should be a list with elements of type {}'.format(self.type)
    
    def cast(self, value):
        return [self.type(t) for v in value]




class ValidationError(Exception):
    pass


# TODO: we can use a default value
CAMERA_TEMPLATE = {'aspect': (1.0, BoundedScalar(0.0, float('inf'), float, ginclusive=False)),
                   'vfov': (90.0, BoundedScalar(0.0, 180.0, float)),
                   'location': ([0.0, 0.0, -1.0], ListOf(float, 3)),
                   'quaternion': ([0.0, 0.0, 0.0, 1.0], ListOf(float, 3)),
                   'target': ([0.0, 0.0, 0.0], ListOf(float, 3))}
                   
                   
# POINTS_OPTIONS_TEMPLATE = {'coordinates': (None, ArrayOf(shape=(-1, 3), type=np.float32))}
def normalize_scene(scene):
    """Normalize incomplete scene with sane defaults"""
    retval = scene.copy()
    camera = scene.get('camera', {}).copy()
    
    for key, (default_value, validator) in CAMERA_TEMPLATE.items():
        if key not in camera:
            camera[key] = default_value
        else:
            value = camera[key]
            
            try:
                cast = validator.cast(value)
            except ValueError:
                raise ValidationError('camera problem: "{}" is {}, cannot cast'.format(key, value))
                
                
            ok, msg = validator.validate(cast)
            if not ok:
                raise ValidationError('camera problem: "{}" is {} but {}'.format(key, value, msg))
                
            camera[key] = cast
    
    scene['camera'] = camera
    
    return scene
