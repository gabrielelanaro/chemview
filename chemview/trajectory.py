from __future__ import absolute_import

from .viewer import MolecularViewer

import numpy as np

from IPython.display import display
from IPython.utils.traitlets import (CInt, link)

class TrajectoryViewer(RepresentationViewer):

    frame = CInt()

    def __init__(self, coordinate_frames, topology, width=500, height=500):
        '''Display a set of coordinate frames
        '''
        self.coordinate_frames = coordinate_frames
        super(TrajectoryViewer, self).__init__(coordinate_frames[0], topology)

        self.controls = TrajectoryControls(traj.n_frames)
        link((self, 'frame'), (self.controls, 'frame'))

    def _on_frame_change(self, name, old, new):
        self.coordinates = self.coordinate_frames[new]

    def _ipython_display_(self):
        display(self.controls)
        super(TrajectoryViewer, self)._ipython_display_()