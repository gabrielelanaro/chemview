.. chemview documentation master file, created by
   sphinx-quickstart on Wed Nov 12 10:38:29 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to chemview's documentation!
====================================

chemview is an interactive molecular viewer designed for the IPython notebook. With chemview you can:

    - **Display** molecules and systems in an easy and efficient manner.
    - Look at those systems evolve in **time**. chemview is fast by design, updates on the properties are performed only when necessary.
    - Perform interactive data visualization in the IPython notebook.
    - Create new ways to visualize your data by using the flexible low-level API.

chemview is implemented using web technologies such as WebGL_ and `three.js <http://threejs.org>`_, giving chemview an **excellent multi-platform support**.

**Excited?** Try it out (it works on smartphones too):

    - Left Click: Rotate
    - Wheel: Zoom
    - Right Click: Pan

.. raw:: html
    :file: _static/minidemo.html

.. _WebGL: http://en.wikipedia.org/wiki/WebGL

Go ahead with the :doc:`quick`.

Contents:

.. toctree::
   :maxdepth: 2

   quick
   representations
   interactive

chemview is licensed under the LGPL2 and is hosted on github at http://github.com/gabrielelanaro/chemview.

Credits
-------

chemview branched from the mdtraj_ project in an effort to make trajectory viewing possible in the browser. It is developed mainly by `Gabriele Lanaro <http://gabrielelanaro.github.io>`_. While the code is original work, the idea was inspired by iview_.


.. _mdtraj: http://mdtraj.org
.. _iview: https://github.com/HongjianLi/iview

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

