=============================
Grammar of graphics interface
=============================

Inspired by the huge success of the ggplot package for R, chemview implements
a similar grammar of graphics.

The grammar of graphics interface encourage separation of data and graphics 
giving composable and rich visualizations. An example best explains the concept:

.. code:: python
    
    from chemview.gg import *
    coordinates = [[0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.3],
                   [0.0, 0.0, 0.4],
                   [0.0, 0.0, 0.5],
                   [0.0, 0.0, 0.6],
                   [0.0, 0.0, 0.7]]
    values = [0.0, 0.1, 0.2, 0.3, 0.5, 0.6]
    mask = np.array([False, True, True, False, True, True])
    gg = ggview(Aes(xyz=coordinates, colors=values,
                    visible=mask))

The class ``ggview`` takes an argument of type ``Aes`` that maps graphic 
(aesthetic) properties to the data. In this case we bind
the ``xyz`` attribute is set to represent the coordinates, the property
 ``colors`` is bound to a set of floating point numbers, and ``visible`` is 
 bound to a mask.
 
This mappings are not useful by themselves, but they take life when combined 
with geometric objects, if we add ``GeomPoints()``, a set of points is displayed
color-coded and masked by the values we passed earlier.

.. code:: python

    gg + GeomPoints()
    gg.display() # for interactive viz in Jupyter notebook
    # gg.render() # for static viz

To display a molecule color-coded by atom type it is sufficient to write:

.. code:: python

    gg = ggview(Aes(xyz=coordinates, 
                    colors=['H', 'O', 'H', 'H', 'O', 'H'])) + GeomPoints()
    gg.display()


This way of doing graphics is extremely powerful because graphic elements
can be easily composed to create custom visualizations.
 
Trajectories
------------
 
This style is also apt to trajectory visualizations. In general, you can make a
certain aesthetics to have a value that varies over time by suffixing it with
 ``_traj``
 
.. code:: python
    coordinates = np.random.rand(10, 100, 3) # 10 frames, 100 points, 3 coordinates
    gg = ggtraj(10, Aes(xyz_traj=coordinates, 
                        colors=np.random.rand(100))) + GeomPoints()
    gg.display()
    
You can similarly change ``colors_traj`` to an array of shape ``(10, 100)`` to
obtain a color that changes frame by frame.
 
Overriding aesthetics
---------------------


Theming
-------


Other Examples
--------------
 
GeomLines()
 
GeomCylinders()

GeomSpheres()

GeomBackbone()

GeomCartoon()

 
 
