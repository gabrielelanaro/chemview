# chemview

[![Documentation Status](https://readthedocs.org/projects/chemview/badge/?version=latest)](https://readthedocs.org/projects/chemview/?badge=latest)

Version: 0.1

The new generation molecular viewer for the IPython notebook.

# Installation

Installing chemview with conda is fairly easy. First download anaconda (or miniconda):

http://continuum.io/downloads

To install chemview using conda you can first create an environment (optional):

    $ conda create -p /path/to/new/environment python
    $ source activate /path/to/new/environment

then, you can install chemview directly from the binstar channel.

    $ conda install -c http://conda.binstar.org/gabrielelanaro

or, for the development version you can manually install the dependencies:

    $ conda install ipython-notebook numpy numba
    $ pip install vapory
    $ git clone https://github.com/gabrielelanaro/chemview
    $ cd chemview
    $ pip install .

It is also possible to install chemview using pip:

    pip install ipython[notebook] # ipython 2.x (development version 0.3 breaks the widget API)
    pip install numpy
    pip install numba

    # Download and install chemview
    git clone https://github.com/gabrielelanaro/chemview
    cd chemview
    pip install .

## Ready to go!

At this point you are ready to go!

    $ ipython notebook

You can try chemview on the test notebooks present in this distribution or head to the documentation
http://chemview.readthedocs.org
