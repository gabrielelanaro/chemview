# chemview

[![Documentation Status](https://readthedocs.org/projects/chemview/badge/?version=latest)](https://readthedocs.org/projects/chemview/?badge=latest)

The new generation molecular viewer for the IPython notebook.

# Installation

chemlab requires a few basic dependencies to be installed:

- numpy
- ipython 2.x (development version 0.3 breaks the widget API)
- numba (optional)

    pip install ipython[notebook]
    pip install numpy

    # Download chemview
    git clone https://github.com/gabrielelanaro/chemview
    cd chemview
    pip install .


## Installation using conda

To install chemview using conda you can first create an environment (optionally):

    $ conda create -p /path/to/new/environment python
    $ source activate /path/to/new/environment

next, you can install the required dependencies and chemview itself.

    $ conda install ipython-notebook
    $ conda install numpy
    $ conda install numba
    $ pip install .

## Ready to go!

At this point you are ready to go!

    $ ipython notebook

You can try chemview on the test notebooks provided 
