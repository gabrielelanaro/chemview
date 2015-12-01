from __future__ import print_function
from chemview.gg import ggview, Aes, GeomPoints, GeomLines, ggtraj
import numpy as np

np.random.seed(10)
def test_gg():
    gg = ggview(Aes(xyz=[[0, 0, 0], [0, 0, 0.15]], 
                    colors=["H", "Cl"],
                    sizes=[1, 1],
                    connect=[[0, 1]],
                    visible=[True, True]))
    
    gg = (gg + GeomPoints() + GeomLines())
    gg.primitives

def test_gg_colors():
    aes = Aes(xyz=[[0, 0, 0], [0, 0, 0.15]], 
              colors=[-1.0, 2.0])
    print(GeomPoints().produce(aes))
    
def test_gg_traj():
    # Random coordinates
    
    xyz = np.random.rand(10, 10, 3)
    gg = ggtraj(Aes(xyz_traj=xyz)) + GeomPoints()
    print(gg.primitives) 
