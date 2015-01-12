# Adapted from mdtraj: github.com/mdtraj/mdtraj

import os
import warnings
from IPython.display import display, Javascript
from IPython.html.nbextensions import install_nbextension
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pkg_resources import resource_filename

__all__ = ['enable_notebook']

_REQUIRE_CONFIG = Javascript('''
require.config({
    paths: {
        'three': '/nbextensions/three.min',
        'exporter' : '/nbextensions/objexporter',
        'filesaver' : '/nbextensions/filesaver',
        'base64-arraybuffer': '/nbextensions/base64-arraybuffer',
        'jqueryui': '/nbextensions/jquery-ui.min',
        'contextmenu': '/nbextensions/context',
        'ArcballControls' : '/nbextensions/ArcballControls',
        'chemview': '/nbextensions/chemview',
    },
    shim: {
        three: {
            exports: 'THREE'
        },

        chemview: {
            deps: ['three', 'ArcballControls'],
            exports: 'MolecularViewer'
        },

        exporter: {
            deps: ['three'],
            exports: 'THREE.OBJExporter'
        },

        ArcballControls: {
            deps: ['three'],
            exports: 'THREE.ArcballControls',
        },

        jqueryui: {
            exports: "$"
        },

    },
});
''',
css  = ['/nbextensions/context.standalone.css']
)

def enable_notebook(verbose=0):
    """Enable IPython notebook widgets to be displayed.

    This function should be called before using the chemview widgets.
    """
    libs = ['objexporter.js', 
            'ArcballControls.js', 'filesaver.js',
            'base64-arraybuffer.js', 'context.js', 
            'chemview.js', 'three.min.js', 'jquery-ui.min.js',
            'context.standalone.css']
    fns = [resource_filename('chemview', os.path.join('static', f)) for f in libs]
    install_nbextension(fns, verbose=verbose, overwrite=True)
    display(_REQUIRE_CONFIG)

    widgets = ['chemview_widget.js', 'trajectory_controls_widget.js']
    for fn in widgets:
        fn = resource_filename('chemview', os.path.join('static', fn))
        display(Javascript(filename=fn))

