
.. py:class:: MolecularViewer(self, coordinates, topology, width=500, height=500)

    Create a Molecular Viewer widget to be displayed in IPython notebook.
    
    :param np.ndarray coordinates: A numpy array containing the 3D coordinates of the atoms to be displayed
    :param dict topology: A dict specifying the topology as described in the User Guide.
    
    .. py:method:: points(self, size=1.0)
    
        Display the system as points.
        
        :param float size: the size of the points.
    
    .. py:method:: lines(self)
    
        Display the system bonds as lines.
        
                
    
    .. py:method:: wireframe(self, pointsize=1.0)
    
        Display atoms as points of size *pointsize* and bonds as lines.
    
    .. py:method:: ball_and_sticks(self, ball_radius=0.05, stick_radius=0.02)
    
        Display the system using a ball and stick representation.
                
    
    .. py:method:: line_ribbon(self)
    
        Display the protein secondary structure as a white lines that passes through the 
        backbone chain.
    
    .. py:method:: cylinder_and_strand(self)
    
        Display the protein secondary structure as a white, 
        solid tube and the alpha-helices as yellow cylinders.
    
    .. py:method:: add_surface(self, function, isolevel=0.3, resolution=32, style='wireframe', color=16777215)
    
    
