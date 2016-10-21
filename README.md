# chemview

[![Join the chat at https://gitter.im/gabrielelanaro/chemview](https://badges.gitter.im/gabrielelanaro/chemview.svg)](https://gitter.im/gabrielelanaro/chemview?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Documentation Status](https://readthedocs.org/projects/chemview/badge/?version=latest)](https://readthedocs.org/projects/chemview/?badge=latest)
[![Build Status](https://travis-ci.org/gabrielelanaro/chemview.svg?branch=master)](https://travis-ci.org/gabrielelanaro/chemview)

Version: 0.7

The new generation molecular viewer for the IPython notebook.


# Installation

Installing chemview with conda is fairly easy. First download anaconda (or miniconda):

http://continuum.io/downloads

To install chemview using conda you can first create an environment (optional):

    $ conda create -p /path/to/new/environment python
    $ source activate /path/to/new/environment

then, you can install chemview directly from the binstar channel.

    $ conda install -c gabrielelanaro chemview

or, for the development version you can manually install the dependencies:

    pip install jupyter notebook numba numpy matplotlib

    # Download and install chemview
    git clone https://github.com/gabrielelanaro/chemview
    cd chemview
    pip install .

The new jupyter also requires you to install the widget manually:

    jupyter nbextension enable widgetsnbextension --user --py
    jupyter nbextension install --user --py --symlink chemview
    jupyter nbextension enable --user --py  chemview

## Ready to go!

At this point you are ready to go!

    $ jupyter notebook

You can try chemview on the test notebooks present in this distribution or head to the documentation
http://chemview.readthedocs.org


# Credits

Many thanks to the project contributors:

- Tristan Mackenzie
- James Kermode
