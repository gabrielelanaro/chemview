from .widget import RepresentationViewer
import mdtraj as md
from itertools import chain, groupby

from IPython.html.widgets import DOMWidget
from IPython.utils.traitlets import (Unicode, Bool, Bytes, CInt, Any,
                                     Dict, Enum, CFloat, List)

class TrajectoryControls(DOMWidget):
    _view_name = Unicode('TrajectoryControls', sync=True)
    frame = CInt(sync=True)   
    
    def __init__(self):
        super(TrajectoryControls, self).__init__()

class TrajectoryViewer(RepresentationViewer):

    frame = CInt()


    def __init__(self, traj, primary_structure=None,
                             secondary_structure="cylinder and strand"):
        '''Viewer for mdtraj trajectories.

        tv = TrajectoryViewer(traj)

        tv.frame = 0
        '''
        super(TrajectoryViewer, self).__init__()
        self.trajectory = traj

        self.primary_structure = primary_structure
        self.secondary_structure = secondary_structure

        self._init_secondary_structure(secondary_structure)

    def _init_secondary_structure(self, name):
        self.cylinders = {'indices': [],
                          'representations': []}
        self.coils = {'indices': [],
                      'representations': []}

        if name == "cylinder and strand":
            top = self.trajectory.topology
            dssp = md.compute_dssp(self.trajectory[0])[0] # classify residues
            top = self.trajectory.topology

            in_helix = False
            helices_starts = []
            helices_ends = []
            coils = []

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
        else:
            raise ValueError("Representation {} not available".format(name))

    def _on_frame_changed(self, name, old, new):

        coordinates = self.trajectory.xyz[self.frame]
        for i, control_points in enumerate(self.coils):
            rid = self.update_representation(self.cooils_reps[i], 
                {'coordinates': coordinates[control_points]})

        start_idx, end_idx = helices_starts, helices_ends
        rid = self.add_representation('cylinders', {'startCoords': coordinates[list(start_idx)],
                                              'endCoords': coordinates[list(end_idx)],
                                              'colors': [0xffff00] * len(coordinates),
                                              'radii': [0.15] * len(coordinates)})
        self.helices_rep.append(rid)

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