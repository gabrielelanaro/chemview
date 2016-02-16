============================
Installation and Quick Start
============================

Installing chemview with conda is fairly easy. First download anaconda (or miniconda):

http://continuum.io/downloads

To install chemview using conda you can first create an environment (optional):

.. code-block:: bash

    $ conda create -p /path/to/new/environment python
    $ source activate /path/to/new/environment

then, you can install chemview directly from the binstar channel.

.. code-block:: bash

    $ conda install -c http://conda.binstar.org/gabrielelanaro

or, for the development version you can manually install the dependencies:

.. code-block:: bash

    $ conda install notebook numpy numba
    $ git clone https://github.com/gabrielelanaro/chemview
    $ cd chemview
    $ pip install .

It is also possible to install chemview using pip:

.. code-block:: bash

    pip install notebook numpy numba # Jupyter 4.x

    # Download and install chemview
    git clone https://github.com/gabrielelanaro/chemview
    cd chemview
    pip install .
    
Chemview has an optional <povray http://www.povray.org/>_ backend for
rendering high quality images. For this you'll need to install the povray software
and the vapory bindings:

 
.. code-block:: bash

    pip install vapory


Quick Start
-----------

In this section we'll see how to visualize a benzene molecule with chemview. To start, let's launch IPython notebook and start a new notebook.

.. code-bock:: bash

    ipython notebook

.. include:: notebooks/QuickStart.rst

Congratulation for finishing the first tutorial! You can now move on more advanced topics:

.. toctree::
    :maxdepth: 2

    representations
    interactivity
    lowlevel
