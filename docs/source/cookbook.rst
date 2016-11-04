Cookbook
========

This documents contains `recipes` to accomplish common tasks with ``chemview``.

Syncronizing cameras across multiple widgets
--------------------------------------------

Using the IPython traitlets system it is possible to syncronize the camera
across different widgets. In the following example we download two molecules (ethane and butane) from the
web using the chemlab_ API, then we create two molecular viewers and we link their cameras:

.. code::

    from IPython.display import display
    from IPython.utils.traitlets import link

    from chemview import MolecularViewer

    from chemlab.notebook import download_molecule

    butane = download_molecule('butane')
    ethane = download_molecule('ethane')

    # Create the two molecular viewer widgets
    mv1 = MolecularViewer(butane.r_array, {'atom_types': butane.type_array,
                                           'bonds': butane.bonds})
    mv1.wireframe()

    mv2 = MolecularViewer(ethane.r_array, {'atom_types': ethane.type_array,
                                           'butane': butane.bonds})
    mv2.wireframe()

    # Link their attributes camera_str together
    link((mv1, 'camera_str'), (mv2, 'camera_str'))

    display(mv1)
    display(mv2)

.. _chemlab: http://chemlab.readthedocs.org

.. _plotting_molecular_orbitals: 

Plotting molecular orbitals
---------------------------
