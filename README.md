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

next, you can either install chemview from the binstar channel.

    $ conda install -c http://conda.binstar.org/gabrielelanaro

or by installing dependencies

    $ conda install ipython-notebook
    $ conda install numpy
    $ conda install numba
    $ git clone https://github.com/gabrielelanaro/chemview
    $ cd chemview
    $ pip install .

chemlab requires a few basic dependencies to be installed:

It is also possible to install using pip. 

We need to first install the dependencies:

- numpy
- ipython 2.x (development version 0.3 breaks the widget API)
- numba

And then install using the following commands:

    pip install ipython[notebook]
    pip install numpy
    pip install numba
    # Download chemview
    git clone https://github.com/gabrielelanaro/chemview
    cd chemview
    pip install .


## Ready to go!

At this point you are ready to go!

    $ ipython notebook

You can try chemview on the test notebooks in this distribution. 
