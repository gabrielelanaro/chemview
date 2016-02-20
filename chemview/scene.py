'''Scene validation utilities'''
import operator
import numpy as np
import six


class Validator(object):

    def validate(self, value):
        pass

    def cast(self, value):
        pass

    def default(self, inp=None):
        return self._default


class BoundedScalar(Validator):

    def __init__(self, start, end, type, ginclusive=True, linclusive=True, default=None):
        self.start = start
        self.end = end
        self.ginclusive = ginclusive
        self.linclusive = linclusive
        self.type = type
        self._default = default

    def validate(self, value):
        lo = operator.le if self.linclusive else operator.lt
        go = operator.ge if self.ginclusive else operator.gt

        return go(value, self.start) and lo(value, self.end), 'should be between {} and {}'.format(self.start, self.end)

    def cast(self, value):
        return self.type(value)


class TypedList(Validator):

    def __init__(self, type, length=None, match_length=None, default_item=None, default=None):
        self.type = type
        self.length = length
        self.match_length = match_length
        self.default_item = default_item
        self._default = default

    def default(self, inp=None):
        if self._default is not None:
            return self._default

        if self.match_length is not None and self.default_item is not None:
            return [self.default_item] * len(inp[self.match_length])
        else:
            raise ValueError("This field is required")

    def validate(self, value):
        # We check the first element only
        length_condition = True if self.length is None else len(
            value) == self.length

        if len(value) == 0:
            type_condition = True
        else:
            type_condition = isinstance(value[0], self.type)

        return length_condition and type_condition, 'should be a list with elements of type {}'.format(self.type)

    def cast(self, value):
        return [self.type(v) for v in value]


class UniqueID(Validator):

    def default(self, inp=None):
        raise ValueError("No default for this field")

    def validate(self, value):
        return isinstance(value, int), 'UUid not valid'

    def cast(self, value):
        return value


class Array(Validator):

    def __init__(self, shape, type):
        self.shape = shape
        self.type = type

    def default(self, inp=None):
        raise ValueError("No default for this field")

    def validate(self, value):
        return True, ''

    def cast(self, value):
        return np.array(value, dtype=self.type)


class Keyword(Validator):

    def __init__(self, value):
        self.value = value

    def default(self, inp=None):
        raise ValueError("No default for this field")

    def validate(self, value):
        return value == self.value, 'should be {}'.format(self.value)

    def cast(self, value):
        return six.u(value)


class Boolean(Validator):

    def __init__(self, default=None):
        self._default = default

    def validate(self, value):
        return isinstance(value, bool), 'should be a boolean, got {}'.format(value)

    def cast(self, value):
        return bool(value)


class MatchSchema(object):

    def __init__(self, matchers, field):
        self.field = field
        self.matchers = {m[field].value: m for m in matchers}

    def match(self, value):
        return self.matchers[value[self.field]]


class ValidationError(Exception):
    pass

from collections import OrderedDict

POINTS_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("points"),
    "options":
        OrderedDict({'coordinates': Array(shape=(-1, 3), type=np.float32),
                     'colors': TypedList(int, match_length='coordinates', default_item=0xffffff),
                     'sizes': TypedList(float, match_length='coordinates', default_item=0.1),
                     'visible': TypedList(float, match_length='coordinates', default_item=1.0)})
}

SPHERES_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("spheres"),
    "options":
        OrderedDict({'coordinates': Array(shape=(-1, 3), type=np.float32),
                     'colors': TypedList(int, match_length='coordinates', default_item=0xffffff),
                     'radii': TypedList(float, match_length='coordinates', default_item=0.1),
                     'alpha': TypedList(float, match_length='coordinates', default_item=1.0)})
}


CYLINDERS_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("cylinders"),
    "options":
        OrderedDict({'startCoords': Array(shape=(-1, 3), type=np.float32),
                     'endCoords': Array(shape=(-1, 3), type=np.float32),
                     'colors': TypedList(int, match_length='startCoords', default_item=0xffffff),
                     'radii': TypedList(float, match_length='startCoords', default_item=0.1),
                     'alpha': TypedList(float, match_length='startCoords', default_item=1.0)})
}

LINES_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("lines"),
    "options":
        OrderedDict({'startCoords': Array(shape=(-1, 3), type=np.float32),
                     'endCoords': Array(shape=(-1, 3), type=np.float32),
                     'startColors': TypedList(int, match_length='startCoords', default_item=0xffffff),
                     'endColors': TypedList(float, match_length='endCoords', default_item=1.0)})
}

SURFACE_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("surface"),
    "options":
        OrderedDict({'verts': Array(shape=(-1, 3), type=np.float32),
                     'faces': Array(shape=(-1, 3), type=np.uint32),
                     'colors': TypedList(int, match_length='verts', default_item=0xffffff),
                     'alpha': TypedList(float, match_length='verts', default_item=1.0)})
}

SMOOTHTUBE_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("smoothtube"),
    "options":
    OrderedDict({'coordinates': Array(shape=(-1, 3), type=np.float32),
                 'radius': BoundedScalar(0.0, float('inf'), float, default=1.0),
                 'color': BoundedScalar(0, 0xffffff, int, default=0xffffff),
                 'resolution': BoundedScalar(2, float('inf'), int, default=16)})
}

RIBBON_SCHEMA = {
    "rep_id": UniqueID(),
    "rep_type": Keyword("ribbon"),
    "options":
    OrderedDict({'coordinates': Array(shape=(-1, 3), type=np.float32),
                 'normals': Array(shape=(-1, 3), type=np.float32),
                 'color': BoundedScalar(0, 0xffffff, int, default=0xffffff),
                 'width': BoundedScalar(0.0, float('inf'), float, default=0.2),
                 'arrow': Boolean(default=False)})
}


SCHEMA = {
    'camera': {'aspect': BoundedScalar(0.0, float('inf'), float, default=1.0, ginclusive=False),
               'vfov': BoundedScalar(0.0, 180.0, float, default=90.0),
               'location': TypedList(float, 3, default=[0.0, 0.0, -1.0]),
               'quaternion': TypedList(float, 4, default=[0.0, 0.0, 0.0, 1.0]),
               'target': TypedList(float, 3, default=[0.0, 0.0, 0.0])},

    'representations': MatchSchema([POINTS_SCHEMA,
                                    SPHERES_SCHEMA,
                                    LINES_SCHEMA,
                                    CYLINDERS_SCHEMA,
                                    SURFACE_SCHEMA,
                                    SMOOTHTUBE_SCHEMA], 'rep_type')
}


def validate_schema(value, schema):
    retval = {}
    for key, validator in schema.items():

        if isinstance(validator, dict):
            inp = value.get(key, {}).copy()
            validated_inp = validate_schema(inp, validator)
            retval[key] = validated_inp

        elif isinstance(validator, MatchSchema):
            inp = value.get(key, [])[:]  # copy

            validated_inp = []
            for val in inp:
                sub_schema = validator.match(val)
                validated_inp.append(validate_schema(val, sub_schema))

            retval[key] = validated_inp

        elif isinstance(validator, Validator):
            if key not in value:
                try:
                    retval[key] = validator.default(value)
                except ValueError:
                    raise ValidationError(
                        'Problem: "{}" is required.'.format(key))
            else:
                try:
                    cast = validator.cast(value[key])
                except ValueError:
                    raise ValidationError(
                        'Problem: "{}" is {}, cannot cast'.format(key, value[key]))

                ok, msg = validator.validate(cast)
                if not ok:
                    raise ValidationError(
                        'Problem: "{}" is {} but {}'.format(key, value[key], msg))
                retval[key] = cast
        else:
            raise ValueError("schema not valid")

    return retval


def normalize_scene(scene):
    """Normalize incomplete scene with sane defaults"""
    retval = scene.copy()

    return validate_schema(scene, SCHEMA)
