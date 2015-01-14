import numpy as np
from .widget import RepresentationViewer, TrajectoryControls
from .utils import get_atom_color
from .marchingcubes import marching_cubes


from IPython.utils.traitlets import Any

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



    def points(self, size=1.0):
        """Display the system as points.

        :param float size: the size of the points.
        """
        colorlist = [get_atom_color(t) for t in self.topology['atom_types']]
        sizes = [size] * len(self.topology['atom_types'])

        points = self.add_representation('points', {'coordinates': self.coordinates.astype('float32'),
                                                    'colors': colorlist,
                                                    'sizes': sizes })
        # Update closure
        def update(self=self, points=points):
            self.update_representation(points, {'coordinates': self.coordinates.astype('float32')})
        self.update_callbacks.append(update)

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

    def wireframe(self, pointsize=0.2):
        '''Display atoms as points of size *pointsize* and bonds as lines.'''
        self.points(pointsize)
        self.lines()

    def ball_and_sticks(self, ball_radius=0.05, stick_radius=0.02):
        """Display the system using a ball and stick representation.
        """
        
        # Add the spheres
        
        colorlist = [get_atom_color(t) for t in self.topology['atom_types']]
        sizes = [ball_radius] * len(self.topology['atom_types'])

        spheres = self.add_representation('spheres', {'coordinates': self.coordinates.astype('float32'),
                                                      'colors': colorlist,
                                                      'radii': sizes})

        def update(self=self, spheres=spheres):
            self.update_representation(spheres, {'coordinates': self.coordinates.astype('float32')})

        self.update_callbacks.append(update) 

        # Add the cylinders
        
        if 'bonds' in self.topology:
            start_idx, end_idx = zip(*self.topology['bonds'])
            cylinders = self.add_representation('cylinders', {'startCoords': self.coordinates[list(start_idx)],
                                                  'endCoords': self.coordinates[list(end_idx)],
                                                  'colors': [0xcccccc] * len(self.coordinates),
                                                  'radii': [stick_radius] * len(self.coordinates)})
            # Update closure
            def update(self=self, rep=cylinders, start_idx=start_idx, end_idx=end_idx):
                self.update_representation(rep, {'startCoords': self.coordinates[list(start_idx)],
                                                 'endCoords': self.coordinates[list(end_idx)]})

            self.update_callbacks.append(update)        

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
        area_min = self.coordinates.min(axis=0) - 2.0
        area_max = self.coordinates.max(axis=0) + 2.0

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
           faces.append([i * 3, i * 3 +1, i * 3 +2])
           verts.extend(t)
  
        faces = np.array(faces)
        verts = area_min + spacing/2 + np.array(verts)*spacing
        rep_id = self.add_representation('surface', {'verts': verts.astype('float32'),
                                                     'faces': faces.astype('int32'),
                                                     'style': style,
                                                     'color': color})

