Scene Description Language
==========================

Chemview uses a scene description language in python dictionary and exportable
to json.

**scene**:
  - **camera**: ``camera_spec``
  - **representations** : ``list`` of ``representation_spec``.

**camera_spec**: 
  - **aspect**: ``float`` Aspect ratio 
  - **vfov**: ``int`` field of view in degrees between 0 and 180 
  - **quaternion**: ``list(float, length=4)`` quaternion representing camera rotation
  - **location**: ``list(float, length=3)`` camera location
  - **target**: ``list(float, length=3)`` camera target
    
**representation_spec**: ``dict`` with the following specification:
    - **rep_id**:``string`` unique identifier for the representation
    - **rep_type**: ``string`` spheres | points | cylinders | lines | surface
    - **options**: ``option_spec``

**option_spec**: a dict that contains the option. Different options must be 
passed for different types.

**spheres**:
  - **coordinates**: ``array(float32, shape=(n, 3))`` of 3D coordinates
  - **radii**: ``list(float32)`` of numbers representing sphere radius
  - **alpha**: ``list(float32)`` alpha transparency
  - **colors**: ``list(uint8)`` of colors (hexadecimal)

Optional: radii, alpha, colors

**points**:
  - **coordinates**: ``array(float32, shape=(n, 3))`` 3D coordinates
  - **sizes**: ``list(float32)`` point sizes
  - **colors**: ``list(uint8)`` point colors (hexadecimal)
  - **visible**: ``list(bool)`` point visibility
 
Optional: sizes, colors, visible
 
**cylinders**:
  - **startCoords**: ``array(float32, shape=(n, 3))`` 3D coordinates
  - **endCoords**; ``array(float32, shape=(n, 3))`` 3D coordinates
  - **radii**: cylinder radii
  - **colors**: cylinder colors
  - **alpha**: ``list(float32)`` transparency level

Optional: radii, colors 

**lines**:
  - **startCoords**: ``array(float32, shape=(n, 3))`` 3D coordinates
  - **endCoords**; ``array(float32, shape=(n, 3))`` 3D coordinates
  - **startColors**: ``list(uint8)``
  - **endColors**: ``list(uint8)``

Optional: startColors, endColors, radii

**surface**:
  - **verts**  ``array(float32, shape=(n, 3))`` vertices of the surface
  - **faces**: ``array(uint8, shape=(n, 3))`` indices of the faces 
  - **colors**: ``list(uint8)``
  - **alpha**: ``list(float32)`` transparency level
 
Optional: colors, alpha
