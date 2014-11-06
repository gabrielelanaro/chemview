from __future__ import absolute_import
import base64
from itertools import groupby
from uuid import uuid4

import numpy as np


from IPython.display import display, Javascript
from IPython.html.widgets import DOMWidget, IntSliderWidget, ContainerWidget
from IPython.utils.traitlets import (Unicode, Bool, Bytes, CInt, Any,
                                     Dict, Enum, CFloat, List)

__all__ = ['RepresentationViewer', 'MolecularViewer']


class RepresentationViewer(DOMWidget):

    # Name of the javascript class which this widget syncs against on the
    # browser side. To work correctly, this javascript class has to be
    # registered and loaded in the browser before this widget is constructed
    # (that's what enable_notebook() does)
    _view_name = Unicode('MolecularView', sync=True)


    def __init__(self):
        '''
        RepresentationViewer is a general purpose 3D viewer. It acceps a 
        variety of representations that are useful (but not limited to)
        to display molecular systems.

        '''
        super(RepresentationViewer, self).__init__()
        self.displayed = False

        # Things to be called when the js harnessing is intialized
        self._displayed_callbacks = []
        def callback(widget):
            for cb in widget._displayed_callbacks:
                cb(widget)
        self.on_displayed(callback)

    def _coordinates_changed(self, name, old, new):
        self._coordinates = encode_numpy(new)

    def _topology_changed(self, name, old, new):
        self.color_scheme = [get_atom_color(atom_type) 
                             for atom_type in new['atom_types']]

    def add_representation(self, rep_type, options):
        '''Add a 3d representation to the viewer.

        Representations:

        'point':
            accepts coordinates, colors, bonds

        'surface':
            accepts a triangles and faces

        '''
        # Add our unique id to be able to refer to the representation
        rep_id = uuid4().hex
        self._remote_call('addRepresentation', type=rep_type, repId=rep_id, options=options)
        return rep_id

    def remove_representation(self, rep_id):
        self._remote_call('removeRepresentation', repId=rep_id)

    def update_representation(self, rep_id, options):
        self._remote_call('updateRepresentation', repId=rep_id, options=options)

    def _remote_call(self, method_name, **kwargs):
        '''Call a method remotely on the javascript side'''
        msg = {}
        msg['type'] = 'callMethod'
        msg['methodName'] = method_name
        msg['args'] = self._recursive_serialize(kwargs)

        if self.displayed is True:
            self.send(msg) # This will be received with View.on_msg
        else:
            # We should prepare a callback to be 
            # called when widget is displayed
            def callback(widget, msg=msg):
                widget.send(msg)
                widget.on_displayed(callback, remove=True) # Auto-unbind

            self._displayed_callbacks.append(callback)

    def _recursive_serialize(self, dictionary):
        '''Serialize a dictionary inplace'''
        for k, v in dictionary.iteritems():
            if isinstance(v, dict):
                self._recursive_serialize(v)
            else:
                # This is when custom serialization happens
                if isinstance(v, np.ndarray):
                    dictionary[k] = encode_numpy(v)
        return dictionary

    def _ipython_display_(self, **kwargs):
        super(RepresentationViewer, self)._ipython_display_(**kwargs)
        self.displayed = True


class MolecularViewer(RepresentationViewer):

    
    def __init__(self, coordinates, atom_types, representations=['point']):
        super(MolecularViewer, self).__init__()

        self.representations_id = []
        self.representation_types = []

        self.coordinates = coordinates
        self.atom_types = atom_types
        
        self.add_points()

    def add_points(self):
        rep_id = self.add_representation('point', {'coordinates': self.coordinates.astype('float32'),
                                                   'colors': [get_atom_color(a) for a in self.atom_types],
                                                   'sizes': [0.5] * len(self.atom_types)})
        self.representations_id.append(rep_id)
        self.representation_types.append('point')

    def add_vdw_surface(self, resolution=32):
        # Let's try the surface
        from .marchingcubes import marching_cubes
        radii = [0.15] * len(self.atom_types)

        # We contain the whole thing
        area_min = self.coordinates.min(axis=0) - 0.5
        area_max = self.coordinates.max(axis=0) + 0.5

        x = np.linspace(area_min[0], area_max[0], resolution)
        y = np.linspace(area_min[1], area_max[1], resolution)
        z = np.linspace(area_min[2], area_max[2], resolution)
        
        xv, yv, zv = np.meshgrid(x, y, z)
        
        blobbiness = -1
        # First we create the metaballs
        f = np.zeros((x.shape[0], y.shape[0], y.shape[0]))
        for r, c in zip(radii, self.coordinates):
            f += np.exp(blobbiness * 
                (((xv-c[0])**2 + (yv-c[1])**2 + (zv-c[2])**2)/r**2 - 1))
        
        spacing = tuple((area_max - area_min)/resolution)
        triangles = marching_cubes(f - 1, 0)
        
        faces = []
        verts = []
        for i, t in enumerate(triangles):
            faces.append([i * 3, i * 3 +1, i * 3 +2])
            verts.extend(t)
        
        faces = np.array(faces)
        verts = area_min + np.array(verts)*spacing
        rep_id = self.add_representation('surface', {'verts': verts.astype('float32'),
                                                     'faces': faces.astype('int32')})

        self.vdw_id = rep_id
        self.representations_id.append(rep_id)
        self.representation_types.append('surface')

    def remove_vdw_surface(self):
        if hasattr(self, 'vdw_id'):
            self.remove_representation(self.vdw_id)

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

        for rep_id in self.representations_id:
            self.update_representation(rep_id, {'coordinates': value.astype('float32')})


class AnimationViewer(MolecularViewer):
    '''
    Animate those frames
    '''

    def __init__(self, coordinates, atom_types, frames):
        super(AnimationViewer, self).__init__(coordinates, atom_types)
        self.frames = range(frames)

        self.slider = IntSliderWidget(min=0, max=len(self.frames)-1, step=1)
        self.frame = 0
        self.slider.on_trait_change(self._on_frame_changed, 'value')

    def update(self, frame):
        # To override
        pass

    @property
    def frame(self):
        return self.slider.value

    @frame.setter
    def frame(self, value):
        self.slider.value = value

    def _on_frame_changed(self, name, old, new):
        self.update(self.slider.value)

    def _ipython_display_(self):
        super(AnimationViewer, self)._ipython_display_()
        display(self.slider)

# Utility functions

def encode_numpy(array):
    '''Encode a numpy array as a base64 encoded string. Returns a dictionary containing the fields:

    - *data*: the base64 string
    - *type*: the array type
    - *shape*: the array shape

    '''
    return {'data' : base64.b64encode(array.data),
            'type' : array.dtype.name,
            'shape': array.shape}

def get_atom_color(atom_name):
    atomColors = {
        "H": 0xFFFFFF,
        "HE": 0xD9FFFF,
        "LI": 0xCC80FF,
        "BE": 0xC2FF00,
        "B": 0xFFB5B5,
        "C": 0x909090,
        "N": 0x3050F8,
        "O": 0xFF0D0D,
        "F": 0x90E050,
        "NE": 0xB3E3F5,
        "NA": 0xAB5CF2,
        "MG": 0x8AFF00,
        "AL": 0xBFA6A6,
        "SI": 0xF0C8A0,
        "P": 0xFF8000,
        "S": 0xFFFF30,
        "CL": 0x1FF01F,
        "AR": 0x80D1E3,
        "K": 0x8F40D4,
        "CA": 0x3DFF00,
        "SC": 0xE6E6E6,
        "TI": 0xBFC2C7,
        "V": 0xA6A6AB,
        "CR": 0x8A99C7,
        "MN": 0x9C7AC7,
        "FE": 0xE06633,
        "CO": 0xF090A0,
        "NI": 0x50D050,
        "CU": 0xC88033,
        "ZN": 0x7D80B0,
        "GA": 0xC28F8F,
        "GE": 0x668F8F,
        "AS": 0xBD80E3,
        "SE": 0xFFA100,
        "BR": 0xA62929,
        "KR": 0x5CB8D1,
        "RB": 0x702EB0,
        "SR": 0x00FF00,
        "Y": 0x94FFFF,
        "ZR": 0x94E0E0,
        "NB": 0x73C2C9,
        "MO": 0x54B5B5,
        "TC": 0x3B9E9E,
        "RU": 0x248F8F,
        "RH": 0x0A7D8C,
        "PD": 0x006985,
        "AG": 0xC0C0C0,
        "CD": 0xFFD98F,
        "IN": 0xA67573,
        "SN": 0x668080,
        "SB": 0x9E63B5,
        "TE": 0xD47A00,
        "I": 0x940094,
        "XE": 0x429EB0,
        "CS": 0x57178F,
        "BA": 0x00C900,
        "LA": 0x70D4FF,
        "CE": 0xFFFFC7,
        "PR": 0xD9FFC7,
        "ND": 0xC7FFC7,
        "PM": 0xA3FFC7,
        "SM": 0x8FFFC7,
        "EU": 0x61FFC7,
        "GD": 0x45FFC7,
        "TB": 0x30FFC7,
        "DY": 0x1FFFC7,
        "HO": 0x00FF9C,
        "ER": 0x00E675,
        "TM": 0x00D452,
        "YB": 0x00BF38,
        "LU": 0x00AB24,
        "HF": 0x4DC2FF,
        "TA": 0x4DA6FF,
        "W": 0x2194D6,
        "RE": 0x267DAB,
        "OS": 0x266696,
        "IR": 0x175487,
        "PT": 0xD0D0E0,
        "AU": 0xFFD123,
        "HG": 0xB8B8D0,
        "TL": 0xA6544D,
        "PB": 0x575961,
        "BI": 0x9E4FB5,
        "PO": 0xAB5C00,
        "AT": 0x754F45,
        "RN": 0x428296,
        "FR": 0x420066,
        "RA": 0x007D00,
        "AC": 0x70ABFA,
        "TH": 0x00BAFF,
        "PA": 0x00A1FF,
        "U": 0x008FFF,
        "NP": 0x0080FF,
        "PU": 0x006BFF,
        "AM": 0x545CF2,
        "CM": 0x785CE3,
        "BK": 0x8A4FE3,
        "CF": 0xA136D4,
        "ES": 0xB31FD4,
        "FM": 0xB31FBA,
    }

    return atomColors[atom_name.upper()]
