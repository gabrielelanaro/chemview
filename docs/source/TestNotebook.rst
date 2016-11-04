
.. code:: python

    import chemview
    from chemview import RepresentationViewer
    from IPython.display import display
    import numpy as np


.. parsed-literal::

    <IPython.core.display.Javascript at 0x7f4b60147550>



.. parsed-literal::

    <IPython.core.display.Javascript at 0x7f4b50a30d90>


.. code:: python

    
    
    coordinates = np.array([[0.0, 1.1, 0.1], [1, 0, 0]], 'float32')
    radii = np.array([1.0, 0.7]).astype('float32')
    colors = [0xFFFFFF, 0xFF999F]
    sizes = [1.0, 2.0]
    
    rv = RepresentationViewer()
    surf_id = rv.add_representation('spheres', {'coordinates': coordinates, 'radii': radii, 'resolution': 8})
    point_id = rv.add_representation('point', {'coordinates': coordinates, 'colors': colors, 'sizes': sizes})
    rv
.. code:: python

    #rv.update_representation(point_id, {'sizes': [2.0, 1.0]})
    rv.remove_representation(surf_id)
.. code:: python

    import mdtraj as md
    traj = md.load_pdb('http://www.rcsb.org/pdb/files/2M6K.pdb')
    print traj

.. parsed-literal::

    <mdtraj.Trajectory with 30 frames, 4462 atoms, 292 residues, and unitcells>


.. code:: python

    atoms = list(traj.topology.atoms)
    chain = list(traj.topology.chains)[0]
    atom = atoms[1]
    atom.element, atom.is_backbone(), atom.residue
    list(chain.atoms)[0]



.. parsed-literal::

    ALA24-N



.. code:: python

    # We can render backbones as chains
    #rv = RepresentationViewer()
    import numpy as np
    for chain in traj.topology.chains:
        backbone_coords = []
        backbone_idx = []
        for atom in chain.atoms:
            if atom.name == 'CA':
                backbone_idx.append(atom.index)
                #print atom.index, atom.name
    backbone_coords = traj.xyz[0][backbone_idx].astype('float32')
    #print backbone_coords
    smooth_id = rv.add_representation('smoothtube', {'coordinates': backbone_coords, 'radius': 0.05, 'resolution': 8})
.. code:: python

    import itertools
    import time
    
    for coords in itertools.cycle(traj.xyz):
        rv.update_representation(smooth_id, {'coordinates': coords[backbone_idx].astype('float32')})
        time.sleep(1)

::


    ---------------------------------------------------------------------------
    KeyboardInterrupt                         Traceback (most recent call last)

    <ipython-input-8-45aab733935e> in <module>()
          4 for coords in itertools.cycle(traj.xyz):
          5     rv.update_representation(smooth_id, {'coordinates': coords[backbone_idx].astype('float32')})
    ----> 6     time.sleep(1)
    

    KeyboardInterrupt: 


.. code:: python

    # how do we find the helices?
    
    
    
    rv = RepresentationViewer()
    
    for chain in traj.topology.chains:
        backbone_coords = []
        backbone_idx = []
        for atom in chain.atoms:
            if atom.name == 'CA':
                backbone_idx.append(atom.index)
                #print atom.index, atom.name
    backbone_coords = traj.xyz[0][backbone_idx].astype('float32')
    #print backbone_coords
    smooth_id = rv.add_representation('smoothtube', {'coordinates': backbone_coords, 'radius': 0.05, 'resolution': 8})
    
    # Secondary structure
    from itertools import groupby
    dssp = md.compute_dssp(traj[0])[0]
    top = traj.topology
    result = []
    keyfunc = lambda ir : (top.residue(ir[0]).chain, ir[1])
    for (chain, ss), grouper in groupby(enumerate(dssp), keyfunc):
        # rindxs is a list of residue indices in this contiguous run
        rindxs = [g[0] for g in grouper]
        start_index = top.residue(rindxs[0]).atom(0).index
        end_index = top.residue(rindxs[-1]).atom(0).index
        if ss == 'H':
            rv.add_representation('cylinder', {'start': traj.xyz[0][start_index].tolist(), 
                                               'end': traj.xyz[0][end_index].tolist(),
                                               'radius': 0.4})
    rv
.. code:: python

    from chemview.widget import encode_numpy
    from chemlab.db import CirDB
    from chemview.widget import MolecularViewer
    cirdb = CirDB()
    alanine = cirdb.get('molecule', 'benzene')
    
    print alanine.type_array
    mv = MolecularViewer(coordinates = alanine.r_array,
                         atom_types = alanine.type_array)
    #mv.add_vdw_surface(64)
    mv

.. parsed-literal::

    [u'C' u'C' u'C' u'C' u'C' u'C' u'H' u'H' u'H' u'H' u'H' u'H']


.. parsed-literal::

    /home/gabriele/workspace/chemlab/chemlab/core/molecule.py:338: FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.
      if val == None:


.. code:: python

    for i in range(10000):
        mv.update_representation(mv.representations_id[0], {'coordinates': (alanine.r_array + (np.random.random(3)-0.5)).astype('float32')})

::


    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)

    <ipython-input-2-1cec986f714c> in <module>()
          1 for i in range(10000):
    ----> 2     mv.update_representation(mv.representations_id[0], {'coordinates': (alanine.r_array + (np.random.random(3)-0.5)).astype('float32')})
    

    NameError: name 'np' is not defined


.. code:: python

    from chemview.widget import AnimationViewer
    import numpy as np
    class MyViewer(AnimationViewer):
        def update(self, frame):
            self.remove_vdw_surface()
            self.coordinates = self.coordinates + (np.random.random(3)-0.5)
            self.add_vdw_surface(32)
    
    MyViewer(coordinates = alanine.r_array, atom_types=alanine.type_array, frames=100)
