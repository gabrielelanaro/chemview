# Adapted from mdtraj: github.com/mdtraj/mdtraj

import os
import warnings
from IPython.display import display, Javascript
from notebook.nbextensions import install_nbextension

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pkg_resources import resource_filename

__all__ = ['enable_notebook']

def enable_notebook(verbose=0):
    """Enable IPython notebook widgets to be displayed.

    This function should be called before using the chemview widgets.
    """
    libs = ['objexporter.js',
            'ArcballControls.js', 'filesaver.js',
            'base64-arraybuffer.js', 'context.js',
            'chemview.js', 'three.min.js', 'jquery-ui.min.js',
            'context.standalone.css', 'chemview_widget.js',
            'trajectory_controls_widget.js', "layout_widget.js",
            "components/jquery-fullscreen/jquery.fullscreen.js",
            'scales.js']
    fns = [resource_filename('chemview', os.path.join('static', f)) for f in libs]

    [install_nbextension(fn, verbose=verbose, overwrite=True, user=True) for fn in fns]
