from ._version import version_info, __version__
from .widget import RepresentationViewer
from .viewer import MolecularViewer, TrajectoryControls
from .trajectory import TrajectoryViewer

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-widget-chemview',
        'require': 'jupyter-widget-chemview/extension'
    }]
