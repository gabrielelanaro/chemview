============================
Installation and Quick Start
============================

Installing chemview is extremely easy.

Installation with pip
---------------------

Open a terminal or command line and install using pip.

.. code-block:: bash

    # Dependencies
    pip install ipython[notebook] # Any 2.x version is fine
    pip install numpy
    # Latest chemview
    pip install git+git://github.com/gabrielelanaro/chemview

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