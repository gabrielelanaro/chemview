from .widget import RepresentationViewer
import mdtraj as md
import numpy as np
from itertools import chain, groupby

from IPython.html.widgets import DOMWidget, ContainerWidget
from IPython.display import display
from IPython.utils.traitlets import (Unicode, Bool, Bytes, CInt, Any,
                                     Dict, Enum, CFloat, List, link)

class TrajectoryControls(DOMWidget):
    '''Play/stop buttons to have frames'''
    _view_name = Unicode('TrajectoryControls', sync=True)
    frame = CInt(sync=True)
    n_frames = CInt(sync=True) 
    
    def __init__(self, n_frames):
        super(TrajectoryControls, self).__init__()
        self.n_frames = n_frames - 1

class TrajectoryViewer(RepresentationViewer):

    frame = CInt()

    def __init__(self, traj, primary_structure=None,
                             secondary_structure="cylinder and strand"):
        '''Viewer for trajectories

        tv = TrajectoryViewer(traj)

        tv.frame = 0
        '''
        super(TrajectoryViewer, self).__init__()
        self.trajectory = traj
        self.coordinates = traj.xyz
        self.controls = TrajectoryControls(traj.n_frames)
        link((self, 'frame'), (self.controls, 'frame'))
        self.primary_structure = primary_structure
        self.secondary_structure = secondary_structure

        self._init_primary_structure(primary_structure)
        self._init_secondary_structure(secondary_structure)

    def _init_primary_structure(self, name):
        if name == 'wireframe':
            # Atoms as points, bonds as lines
            colorlist = [0xffffff] * self.trajectory.n_atoms
            points = self.add_representation('points', {'coordinates': self.coordinates[self.frame],
                                                        'colors': colorlist})
            color_array = np.array(colorlist)
            bond_start, bond_end = zip(*self.trajectory.topology.bonds)
            bond_start = [a.index for a in bond_start]
            bond_end = [a.index for a in bond_end]
            lines = self.add_representation('lines', {'startCoords': self.coordinates[self.frame][bond_start],
                                                      'endCoords': self.coordinates[self.frame][bond_end],
                                                      'startColors': color_array[bond_start].tolist(),
                                                      'endColors': color_array[bond_end].tolist()})

            self.points_id = points
            self.lines_id = lines

    def _init_secondary_structure(self, name):

        if name == "cylinder and strand":
            top = self.trajectory.topology
            dssp = md.compute_dssp(self.trajectory[0])[0] # classify residues
            top = self.trajectory.topology

            in_helix = False
            self.helices_starts = helices_starts = []
            self.helices_ends = helices_ends = []
            self.coils = coils = []

            coil = [] # It's gonna be discarded
            for i,typ in enumerate(dssp):
                if typ == 'H':
                    if in_helix == False:
                        # We become helices
                        helices_starts.append(top.residue(i).atom(0).index)
                        in_helix = True

                        # We end the previous coil
                        coil.append(top.residue(i).atom(0).index)
                else:
                    if in_helix == True:
                        # We stop being helices
                        helices_ends.append(top.residue(i).atom(0).index)

                        # We start a new coil
                        coil = []
                        coils.append(coil)
                        in_helix = False

                    # We add control points
                    coil.append(top.residue(i).atom(0).index)
                    [coil.append(a.index) for a in top.residue(i).atoms if a.name == 'CA']

            # Let's render them
            coordinates = self.trajectory.xyz[self.frame]
            self.coils_reps = []
            self.helices_rep = []

            for control_points in coils:
                rid = self.add_representation('smoothtube', {'coordinates': coordinates[control_points],
                                                       'radius': 0.05, 
                                                       'resolution': 4,
                                                       'color': 0xffffff})
                self.coils_reps.append(rid)


            start_idx, end_idx = helices_starts, helices_ends
            rid = self.add_representation('cylinders', {'startCoords': coordinates[list(start_idx)],
                                                  'endCoords': coordinates[list(end_idx)],
                                                  'colors': [0xffff00] * len(coordinates),
                                                  'radii': [0.15] * len(coordinates)})
            self.helices_rep.append(rid)
        elif name is None:
            return
        else:
            raise ValueError("Representation {} not available".format(name))

    def _frame_changed(self, name, old, new):
        coordinates = self.trajectory.xyz[self.frame]

        if self.secondary_structure == 'cylinder and strand':
            for i, control_points in enumerate(self.coils):
                rid = self.update_representation(self.coils_reps[i], 
                    {'coordinates': coordinates[control_points]})

            start_idx, end_idx = self.helices_starts, self.helices_ends
            self.add_representation('cylinders', {'startCoords': coordinates[list(start_idx)],
                                                  'endCoords': coordinates[list(end_idx)]})
        
        if self.primary_structure == 'wireframe':
            bond_start, bond_end = zip(*self.trajectory.topology.bonds)
            bond_start = [a.index for a in bond_start]
            bond_end = [a.index for a in bond_end]
            self.update_representation(self.points_id, {'coordinates': self.coordinates[self.frame]})
            self.update_representation(self.lines_id, {'startCoords': self.coordinates[self.frame][bond_start],
                                                       'endCoords': self.coordinates[self.frame][bond_end]})

    def _secondary_structure_iter(self):
        # We need first to isolate strands (coils) and cylinders (helices)
        dssp = md.compute_dssp(self.trajectory[0])[0] # classify residues
        top = self.trajectory.topology

        keyfunc = lambda ir : (top.residue(ir[0]).chain, ir[1])

        for (chain, ss), grouper in groupby(enumerate(dssp), keyfunc):
            # rindxs is a list of residue indices in this contiguous run
            rindxs = [g[0] for g in grouper]

            start_index = top.residue(rindxs[0]).atom(0).index
            end_index = top.residue(rindxs[-1]).atom(0).index
            yield ss, rindxs # For example 'H', [0, 1, 2, 3]

    def _ipython_display_(self):
        display(self.controls)
        super(TrajectoryViewer, self)._ipython_display_()