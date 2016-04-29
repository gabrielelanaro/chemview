import numpy as np
from .widget import RepresentationViewer, TrajectoryControls
from .utils import get_atom_color
from .marchingcubes import marching_cubes
from . import gg

from traitlets import Any

__all__ = ['MolecularViewer']
# Library-agnostic molecular viewer
class MolecularViewer(RepresentationViewer):

    coordinates = Any()

    def __init__(self, coordinates, topology, width=500, height=500):
        '''Create a Molecular Viewer widget to be displayed in IPython notebook.

        :param np.ndarray coordinates: A numpy array containing the 3D coordinates of the atoms to be displayed
        :param dict topology: A dict specifying the topology as described in the User Guide.

        '''
        super(MolecularViewer, self).__init__(width, height)
        self.update_callbacks = []
        self.coordinates = coordinates.astype('float32')
        self.topology = topology

        self._axes_reps = []

    def points(self, size=1.0, highlight=None, colorlist=None, opacity=1.0):
        """Display the system as points.

        :param float size: the size of the points.


        """
        if colorlist is None:
            colorlist = [get_atom_color(t) for t in self.topology['atom_types']]
        if highlight is not None:
            if isinstance(highlight, int):
                colorlist[highlight] = 0xff0000
            if isinstance(highlight, (list, np.ndarray)):
                for i in highlight:
                    colorlist[i] = 0xff0000

        sizes = [size] * len(self.topology['atom_types'])

        points = self.add_representation('points', {'coordinates': self.coordinates.astype('float32'),
                                                    'colors': colorlist,
                                                    'sizes': sizes,
                                                    'opacity': opacity})
        # Update closure
        def update(self=self, points=points):
            self.update_representation(points, {'coordinates': self.coordinates.astype('float32')})
            
        self.update_callbacks.append(update)
        self.autozoom(self.coordinates)
        
    def labels(self, text=None, coordinates=None, colorlist=None, sizes=None, fonts=None, opacity=1.0):
        '''Display atomic labels for the system'''
        if coordinates is None:
            coordinates=self.coordinates
        l=len(coordinates)
        if text is None:
            if len(self.topology.get('atom_types'))==l:
                text=[self.topology['atom_types'][i]+str(i+1) for i in range(l)]
            else:
                text=[str(i+1) for i in range(l)]
            
        text_representation = self.add_representation('text', {'coordinates':   coordinates,
                                                               'text':        text,
                                                               'colors':      colorlist,
                                                               'sizes':       sizes,
                                                               'fonts':       fonts,
                                                               'opacity':     opacity})
        def update(self=self, text_representation=text_representation):
            self.update_representation(text_representation, {'coordinates': coordinates})
        
        self.update_callbacks.append(update)
        
    def remove_labels(self):
        '''Remove all atomic labels from the system'''
        for rep_id in self.representations.keys():
            if self.representations[rep_id]['rep_type']=='text' and rep_id not in self._axes_reps:
                self.remove_representation(rep_id)
    
    def toggle_axes(self, parameters = None):
        '''Toggle axes [x,y,z] on and off for the current representation
        Parameters: dictionary of parameters to control axes:
            position/p:     origin of axes
            length/l:       length of axis
            offset/o:       offset to place axis labels
            axis_colors/ac: axis colors
            text_colors/tc: label colors
            radii/r:        axis radii
            text/t:         label text
            sizes/s:        label sizes
            fonts/f:        label fonts'''
        
        if len(self._axes_reps)>0:
            for rep_id in self._axes_reps:
                self.remove_representation(rep_id)
            self._axes_reps = []
        else:
            if not isinstance(parameters,dict):
                parameters={}
                
            def defaults(pdict,keys,default,length=3,instance=(int,float)):
                '''Helper function to generate default values and handle errors'''
                for k in keys:
                    val=pdict.get(k)
                    if val!=None:
                        break
                if val==None:
                    val=default
                elif isinstance(val,instance) and length>1:
                    val = [val]*length
                elif isinstance(val,(list,np.generic,np.ndarray)) and length>1:
                    if not all([isinstance(v,instance) for v in val]):
                        raise RuntimeError("Invalid type {t} for parameter {p}. Use {i}.".format(t=type(val),p=val,i=instance))
                elif not isinstance(val,instance):
                    raise RuntimeError("Invalid type {t} for parameter {p}. Use {i}.".format(t=type(val),p=val,i=instance))
                return val
                
            p =  defaults(parameters,['positions','position','p'],np.average(self.coordinates,0))
            l =  defaults(parameters,['lengths','length','l'],max([np.linalg.norm(x-p) for x in self.coordinates]),1)
            o =  defaults(parameters,['offsets','offset','o'],l*1.05,1)
            ac = defaults(parameters,[a+c for a in ['axis_','a',''] for c in ['colors','colours','color','colour','c']],[0xff0000,0x00ff00,0x0000ff],3,(int,hex))
            tc = defaults(parameters,[a+c for a in ['text_','t',''] for c in ['colors','colours','color','colour','c']],[0xff0000,0x00ff00,0x0000ff],3,(int,hex))
            r =  defaults(parameters,['radii','radius','r'],[0.005]*3,3)
            t =  defaults(parameters,['text','labels','t'],['X','Y','Z'],3,str)
            s =  defaults(parameters,['sizes','size','s'],[32]*3,3)
            f =  defaults(parameters,['fonts','font','f'],['Arial']*3,3,str)
            
            starts=np.array([p,p,p],float)
            ends=np.array([p+[l,0,0],p+[0,l,0],p+[0,0,l]],float)
            axis_labels_coords=np.array([p+[o,0,0],p+[0,o,0],p+[0,0,o]],float)
            
            a_rep=self.add_representation('cylinders',{"startCoords":starts,
                                                     "endCoords":ends,
                                                     "colors":ac,
                                                     "radii":r})
            
            t_rep=self.add_representation('text',{"coordinates":axis_labels_coords,
                                                  "text":t,
                                                  "colors":tc,
                                                  "sizes":s,
                                                  "fonts":f})
            self._axes_reps = [a_rep, t_rep]
            
    
    def lines(self):
        '''Display the system bonds as lines.

        '''
        if "bonds" not in self.topology:
            return

        bond_start, bond_end = zip(*self.topology['bonds'])
        bond_start = np.array(bond_start)
        bond_end = np.array(bond_end)

        color_array = np.array([get_atom_color(t) for t in self.topology['atom_types']])
        lines = self.add_representation('lines', {'startCoords': self.coordinates[bond_start],
                                                  'endCoords': self.coordinates[bond_end],
                                                  'startColors': color_array[bond_start].tolist(),
                                                  'endColors': color_array[bond_end].tolist()})

        def update(self=self, lines=lines):
            bond_start, bond_end = zip(*self.topology['bonds'])
            bond_start = np.array(bond_start)
            bond_end = np.array(bond_end)

            self.update_representation(lines, {'startCoords': self.coordinates[bond_start],
                                                 'endCoords': self.coordinates[bond_end]})
        self.update_callbacks.append(update)
        self.autozoom(self.coordinates)

    def wireframe(self, pointsize=0.2, opacity=1.0):
        '''Display atoms as points of size *pointsize* and bonds as lines.'''
        self.points(pointsize, opacity=opacity)
        self.lines()

    def ball_and_sticks(self, ball_radius=0.05, stick_radius=0.02, colorlist=None, opacity=1.0):
        """Display the system using a ball and stick representation.
        """

        # Add the spheres

        if colorlist is None:
            colorlist = [get_atom_color(t) for t in self.topology['atom_types']]
        sizes = [ball_radius] * len(self.topology['atom_types'])

        spheres = self.add_representation('spheres', {'coordinates': self.coordinates.astype('float32'),
                                                      'colors': colorlist,
                                                      'radii': sizes,
                                                      'opacity': opacity})

        def update(self=self, spheres=spheres):
            self.update_representation(spheres, {'coordinates': self.coordinates.astype('float32')})

        self.update_callbacks.append(update)

        # Add the cylinders

        if 'bonds' in self.topology and self.topology['bonds'] is not None:
            start_idx, end_idx = zip(*self.topology['bonds'])
            # Added this so bonds don't go through atoms when opacity<1.0
            new_start_coords = []
            new_end_coords = []
            for bond_ind, bond in enumerate(self.topology['bonds']):
                trim_amt = (ball_radius**2 - stick_radius**2)**0.5 if ball_radius>stick_radius else 0
                start_coord = self.coordinates[bond[0]]
                end_coord = self.coordinates[bond[1]]
                vec = (end_coord-start_coord)/np.linalg.norm(end_coord-start_coord)
                new_start_coords.append(start_coord+vec*trim_amt)
                new_end_coords.append(end_coord-vec*trim_amt)

            cylinders = self.add_representation('cylinders', {'startCoords': np.array(new_start_coords,dtype='float32'),
                                                  'endCoords': np.array(new_end_coords,dtype='float32'),
                                                  'colors': [0xcccccc] * len(new_start_coords),
                                                  'radii': [stick_radius] * len(new_start_coords),
                                                  'opacity': opacity})
            # Update closure
            def update(self=self, rep=cylinders, start_idx=start_idx, end_idx=end_idx):
                self.update_representation(rep, {'startCoords': self.coordinates[list(start_idx)],
                                                 'endCoords': self.coordinates[list(end_idx)]})

            self.update_callbacks.append(update)
        self.autozoom(self.coordinates)

    def line_ribbon(self):
        '''Display the protein secondary structure as a white lines that passes through the
           backbone chain.

        '''
        # Control points are the CA (C alphas)
        backbone = np.array(self.topology['atom_names']) == 'CA'
        smoothline = self.add_representation('smoothline', {'coordinates': self.coordinates[backbone],
                                                            'color': 0xffffff})

        def update(self=self, smoothline=smoothline):
            self.update_representation(smoothline, {'coordinates': self.coordinates[backbone]})
        self.update_callbacks.append(update)
        
        self.autozoom(self.coordinates)

    def cylinder_and_strand(self):
        '''Display the protein secondary structure as a white,
           solid tube and the alpha-helices as yellow cylinders.

        '''
        top = self.topology
        # We build a  mini-state machine to find the
        # start end of helices and such
        in_helix = False
        helices_starts = []
        helices_ends = []
        coils = []

        coil = []
        for i, typ in enumerate(top['secondary_structure']):
            if typ == 'H':
                if in_helix == False:
                    # We become helices
                    helices_starts.append(top['residue_indices'][i][0])
                    in_helix = True

                    # We end the previous coil
                    coil.append(top['residue_indices'][i][0])
            else:
                if in_helix == True:
                    # We stop being helices
                    helices_ends.append(top['residue_indices'][i][0])

                    # We start a new coil
                    coil = []
                    coils.append(coil)
                    in_helix = False

                # We add control points
                coil.append(top['residue_indices'][i][0])
                [coil.append(j) for j in top['residue_indices'][i] if top['atom_names'][j] == 'CA']

        # We add the coils
        coil_representations = []
        for control_points in coils:
            rid = self.add_representation('smoothtube', {'coordinates': self.coordinates[control_points],
                                                   'radius': 0.05,
                                                   'resolution': 4,
                                                   'color': 0xffffff})
            coil_representations.append(rid)


        start_idx, end_idx = helices_starts, helices_ends
        cylinders = self.add_representation('cylinders', {'startCoords': self.coordinates[list(start_idx)],
                                              'endCoords': self.coordinates[list(end_idx)],
                                              'colors': [0xffff00] * len(self.coordinates),
                                              'radii': [0.15] * len(self.coordinates)})
        def update(self=self, cylinders=cylinders, coils=coils,
                   coil_representations=coil_representations,
                   start_idx=start_idx, end_idx=end_idx, control_points=control_points):
            for i, control_points in enumerate(coils):
                rid = self.update_representation(coil_representations[i],
                                                 {'coordinates': self.coordinates[control_points]})

            self.update_representation(cylinders, {'startCoords': self.coordinates[list(start_idx)],
                                                  'endCoords': self.coordinates[list(end_idx)]})

        self.update_callbacks.append(update)
        self.autozoom(self.coordinates)
        
    def cartoon(self, cmap=None):
        '''Display a protein secondary structure as a pymol-like cartoon representation.
        
        :param cmap: is a dictionary that maps the secondary type 
                    (H=helix, E=sheet, C=coil) to a hexadecimal color (0xffffff for white) 
        '''
        # Parse secondary structure
        top = self.topology
        
        geom = gg.GeomProteinCartoon(gg.Aes(xyz=self.coordinates, 
                                            types=top['atom_names'],
                                            secondary_type=top['secondary_structure']),
                                            cmap=cmap)
        
        primitives = geom.produce(gg.Aes())
        ids = [self.add_representation(r['rep_type'], r['options']) for r in primitives]
        
        def update(self=self, geom=geom, ids=ids):
            primitives = geom.produce(gg.Aes(xyz=self.coordinates))
            [self.update_representation(id_, rep['options']) 
                for id_, rep_options in zip(ids, primitives)]
        
        self.update_callbacks.append(update)
        self.autozoom(self.coordinates)
    
    def _coordinates_changed(self, name, old, new):
        [c() for c in self.update_callbacks]

    def add_isosurface(self, function, isolevel=0.3, resolution=32, style="wireframe", color=0xffffff):
        '''Add an isosurface to the current scene.

        :param callable function: A function that takes x, y, z coordinates as input and is broadcastable using numpy. Typically simple
                                  functions that involve standard arithmetic operations and functions
                                  such as ``x**2 + y**2 + z**2`` or ``np.exp(x**2 + y**2 + z**2)`` will work. If not sure, you can first
                                  pass the function through ``numpy.vectorize``.\

                                  Example: ``mv.add_isosurface(np.vectorize(f))``
        :param float isolevel: The value for which the function should be constant.
        :param int resolution: The number of grid point to use for the surface. An high value will give better quality but lower performance.
        :param str style: The surface style, choose between ``solid``, ``wireframe`` and ``transparent``.
        :param int color: The color given as an hexadecimal integer. Example: ``0xffffff`` is white.

        '''

        avail_styles = ['wireframe', 'solid', 'transparent']
        if style not in avail_styles:
            raise ValueError('style must be in ' + str(avail_styles))

        # We want to make a container that contains the whole molecule
        # and surface
        area_min = self.coordinates.min(axis=0) - 0.2
        area_max = self.coordinates.max(axis=0) + 0.2

        x = np.linspace(area_min[0], area_max[0], resolution)
        y = np.linspace(area_min[1], area_max[1], resolution)
        z = np.linspace(area_min[2], area_max[2], resolution)

        xv, yv, zv = np.meshgrid(x, y, z)
        spacing = np.array((area_max - area_min)/resolution)

        if isolevel >= 0:
            triangles = marching_cubes(function(xv, yv, zv), isolevel)
        else: # Wrong traingle unwinding roder -- god only knows why
            triangles = marching_cubes(-function(xv, yv, zv), -isolevel)

        if len(triangles) == 0:
            ## NO surface
            return

        faces = []
        verts = []
        for i, t in enumerate(triangles):
           faces.append([i * 3, i * 3 +1, i * 3 + 2])
           verts.extend(t)

        faces = np.array(faces)
        verts = area_min + spacing/2 + np.array(verts)*spacing
        rep_id = self.add_representation('surface', {'verts': verts.astype('float32'),
                                                     'faces': faces.astype('int32'),
                                                     'style': style,
                                                     'color': color})
        self.autozoom(verts)

    def add_isosurface_grid_data(self, data, origin, extent, resolution,
                                 isolevel=0.3, scale=10,
                                 style="wireframe", color=0xffffff):
        """
        Add an isosurface to current scence using pre-computed data on a grid
        """
        spacing = np.array(extent/resolution)/scale
        if isolevel >= 0:
            triangles = marching_cubes(data, isolevel)
        else:
            triangles = marching_cubes(-data, -isolevel)
        faces = []
        verts = []
        for i, t in enumerate(triangles):
            faces.append([i * 3, i * 3 +1, i * 3 + 2])
            verts.extend(t)
        faces = np.array(faces)
        verts = origin + spacing/2 + np.array(verts)*spacing
        rep_id = self.add_representation('surface', {'verts': verts.astype('float32'),
                                                     'faces': faces.astype('int32'),
                                                     'style': style,
                                                     'color': color})
             
        self.autozoom(verts)
