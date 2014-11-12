The Javascript Viewer
=====================

The javascript viewer is developed on the library THREE.js.

We have a collection of classes, Renderers and each renderer has its own functionality.

.. js:class:: PointRenderer(coords, colors, sizes)

    :param Float32View coords: Coordinates as a flat typed array.
    :param List colors: Colors as hexadecimal values passed as a string.
    :param List sizes: The size of the points passed as a list. Note that the sizes may not be 
                       representative and they have a max cap of 16.

    Renders the coordinates as round points in space.
