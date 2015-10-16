from __future__ import absolute_import

from .viewer import MolecularViewer
from .widget import TrajectoryControls

import numpy as np

from IPython.display import display
from traitlets import (CInt, link)

class TrajectoryViewer(MolecularViewer):

    frame = CInt()

    def __init__(self, coordinate_frames, topology, width=500, height=500):
        '''Display a trajectory in the IPython notebook.

        :param list coordinate_frames: A list containing the positions of the atoms (as np.ndarray) for each frame.
        :param dict topology: A dictionary specifying the topology

        .. seealso:: :class:`MolecularViewer`

        '''
        self.coordinate_frames = coordinate_frames
        super(TrajectoryViewer, self).__init__(coordinate_frames[0], topology, width=width, height=height)

        self.controls = TrajectoryControls(len(coordinate_frames))
        link((self, 'frame'), (self.controls, 'frame'))

    def _frame_changed(self, name, old, new):
        self.coordinates = self.coordinate_frames[new]

    def _ipython_display_(self):
        display(self.controls)
        super(TrajectoryViewer, self)._ipython_display_()
