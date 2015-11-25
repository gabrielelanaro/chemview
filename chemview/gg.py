"""GGplot like interface"""
import uuid

from .utils import get_atom_color
from .widget import RepresentationViewer, TrajectoryControls

from IPython.display import display, Image
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np

class ggview(object):
    def __init__(self, aes):
        self.aes = aes
        self.geometries = []
        self.scales = []

    def display(self):
        # Generate primitives
        aes = self.aes
        
        # Apply scale that map data to aes
        for scale in self.scales:
            scale.render()
            aes = scale.apply(aes)
        
        primitives = []
        for geometry in self.geometries:
            primitives.extend(geometry.produce(aes))

        # We generate a json description
        rv = RepresentationViewer.from_scene({"representations" : primitives})
        return rv

    def __add__(self, other):
        
        if isinstance(other, Geom):
            self.geometries.append(other)
            
        elif isinstance(other, Scale):
            self.scales.append(other)
        else:
            raise ValueError("Data type not understood {}".format(type(other)))

        return self


class ggtraj(ggview):
    
    def __init__(self, frames, aes):
        frame_aes = ggtraj._make_frame_aes(aes, 0)
        super(ggtraj, self).__init__(frame_aes)
        self.frames = frames
        self.traj_aes = aes
        self.update_funcs = []

    def display(self):
        # Generate primitives
        aes = self.aes
        # Apply scale that map data to aes
        for scale in self.scales:
            scale.render()
            aes = scale.apply(aes)
        
        primitives = []
        for geometry in self.geometries:
            prims = geometry.produce(aes)
            primitives.extend(prims)
            
            self.update_funcs.append((prims[0]["rep_id"], geometry.update))
        
        rv = RepresentationViewer.from_scene({"representations" : primitives})        
        tc = TrajectoryControls(self.frames)
        tc.on_frame_change(lambda frame, self=self, widget=rv: self.update(widget, frame))
        # Add trajectory viewer too
        display(rv)
        display(tc)
        
        
        return tc, rv

    @staticmethod
    def _make_frame_aes(aes, frame):
        frame_aes = Aes()
        
        # Make a copy
        for k in aes.keys():
            frame_aes[k] = aes[k]
        
        # Override the traj ones
        for k in aes.keys():
            if k.endswith("_traj"):
                frame_aes[k[:-5]] = aes[k][frame]

        return frame_aes
        
    def update(self, widget, frame):
        
        for rep_id, func in self.update_funcs:
            aes = ggtraj._make_frame_aes(self.traj_aes, frame)
            for scale in self.scales:
                aes = scale.apply(aes)
            
            options = func(aes)
            widget.update_representation(rep_id, options)
    


class Geom(object):
    pass

class GeomPoints(Geom):

    def produce(self, aes):
        # Return a dict of primitives produced from aes data
        return [{
                "rep_id" : uuid.uuid1().hex,
                'type': "points",
                "options": { "coordinates": aes.xyz,
                             "colors": process_colors(len(aes.xyz), aes.get("colors", None)),
                             "sizes": process_sizes(len(aes.xyz), aes.get("sizes", 1)),
                             "visible": aes.get("visible", None) }
                }]

    def update(self, aes):
        # we return options
        return { "coordinates": aes.xyz,
                 "colors": process_colors(len(aes.xyz), aes.get("colors", None)),
                 "sizes": process_sizes(len(aes.xyz), aes.get("sizes", None)),
                 "visible": aes.get("visible", None) }

class GeomLines(Geom):
    def produce(self, aes):
        # Return a dict of primitives produced from aes data
        xyz = np.array(aes.xyz)
        return [
            { "rep_id" : uuid.uuid1().hex,
              'type': "lines",
                "options" : {
                "startCoords": aes.xyz,
                "colors": aes.colors,
                "sizes": aes.sizes}
            }
        ]

class Scale(object):
    pass

class ScaleColorsGradient(Scale):
    property = "colors"
    
    def __init__(self, limits=None,  palette="YlGnBu"):
        self.limits = limits
        self.palette = palette
    
    def apply(self, aes):
        aes = aes.copy()
        colors = process_colors(len(aes.xyz), aes.get("colors", None), self.limits, self.palette)
        aes.colors = colors
        return aes
    
    def render(self):
        from matplotlib import pyplot
        import matplotlib as mpl
        
        # Make a figure and axes with dimensions as desired.
        fig = pyplot.figure(figsize=(8, 3))
        ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])

        # Set the colormap and norm to correspond to the data for which
        # the colorbar will be used.
        cmap = mpl.cm.get_cmap(self.palette)
        norm = mpl.colors.Normalize(vmin=self.limits[0], vmax=self.limits[1])

        # ColorbarBase derives from ScalarMappable and puts a colorbar
        # in a specified axes, so it has everything needed for a
        # standalone colorbar.  There are many more kwargs, but the
        # following gives a basic continuous colorbar with ticks
        # and labels.
        cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                        norm=norm,
                                        orientation='horizontal')
        #cb1.set_label('Some Units')
        from IPython.display import display
        from cStringIO import StringIO
        data = StringIO()
        fig.savefig(data, format="png")
        display(Image(data=data.getvalue()))


def rgbint_to_hex(rgb):
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]

def process_colors(size, colors, limits=None, palette="YlGnBu"):
    if colors is None:
        return [0xffffff] * size
    
    elif isinstance(colors, list) and len(colors) == 0:
        return [0xffffff] * size
    
    elif isinstance(colors, list) and isinstance(colors[0], str):
        return [get_atom_color(c) for c in colors]
    
    elif isinstance(colors, list) and isinstance(colors[0], int):
        return colors
    
    elif isinstance(colors, np.ndarray):
        return process_colors(size, colors.tolist(), limits, palette)
    
    elif isinstance(colors, list) and isinstance(colors[0], float):
        if limits is None:
             vmin = min(colors)
             vmax = max(colors)
        else:
            vmin, vmax = limits
        
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap(palette)
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        return [rgbint_to_hex(c) for c in m.to_rgba(colors, bytes=True)[:, :3]]
    else:
        raise ValueError("Wrong color format")

def process_sizes(size, sizes):
    if sizes is None:
        return [1.0] * size
    if isinstance(sizes, int):
        return [sizes] * size
    elif isinstance(sizes, list) and len(sizes) == 0:
        return [1.0] * size
    elif isinstance(sizes, list) and isinstance(sizes[0], (int, float)):
        return sizes
    else:
        raise ValueError("Wrong sizes format")

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def copy(self):
        return AttrDict(self)
class Aes(AttrDict):
    
    def __init__(self, *args, **kwargs):
        super(Aes, self).__init__(*args, **kwargs)

    def __repr__(self):
        return str(self.copy())
