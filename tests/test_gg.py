from __future__ import print_function
from chemview.gg import ggview, Aes, GeomPoints, GeomLines, GeomSpheres, GeomCylinders, ggtraj, GeomRibbon, GeomProteinCartoon
import numpy as np
from nose.tools import eq_
from chemview.utils import beta_sheet_normals, normalized


def npeq_(a, b):
    assert np.allclose(a, b)

np.random.seed(10)


def test_geom_points():
    xyz = [[0, 0, 0], [0, 0, 0.15]]
    points = GeomPoints(Aes(xyz=xyz))
    reps = points.produce(Aes())

    # It produces a single points representation
    eq_(reps[0]["rep_type"], "points")
    npeq_(reps[0]["options"]["coordinates"], xyz)


def test_geom_spheres():
    xyz = [[0, 0, 0], [0, 0, 0.15]]
    points = GeomSpheres(Aes(xyz=xyz))
    reps = points.produce(Aes())

    # It produces a single points representation
    eq_(reps[0]["rep_type"], "spheres")
    npeq_(reps[0]["options"]["coordinates"], xyz)


def test_geom_lines():
    xyz = [[0, 0, 0], [0, 0, 0.15], [0.15, 0.15, 0.15]]

    lines = GeomLines(Aes(xyz=xyz, edges=[[0, 1], [1, 2]]))
    reps = lines.produce(Aes())

    # It produces a single points representation
    eq_(reps[0]["rep_type"], "lines")
    npeq_(reps[0]["options"]["startCoords"], xyz[:2])
    npeq_(reps[0]["options"]["endCoords"], xyz[1:])


def test_geom_cylinders():
    xyz = [[0, 0, 0], [0, 0, 0.15], [0.15, 0.15, 0.15]]

    lines = GeomCylinders(Aes(xyz=xyz, edges=[[0, 1], [1, 2]]))
    reps = lines.produce(Aes())

    # It produces a single points representation
    eq_(reps[0]["rep_type"], "cylinders")
    npeq_(reps[0]["options"]["startCoords"], xyz[:2])
    npeq_(reps[0]["options"]["endCoords"], xyz[1:])

# def test_geom_surface():
#     surf = GeomSurface(Aes(function=lambda x, y, z: x**2 + y**2 + z**2),
#                        bounds=[[-1, 1], [-1, 1], [-1, 1]],
#                        resolution=[32, 32, 32])
#
#     surf2 = GeomSurface(Aes(voxels=data),
#                         bounds=[[-1, 1], [-1, 1], [-1, 1]],
#                         resolution=[32, 32, 32])


def test_geom_ribbon():
    # For this test we need chemlab
    from chemlab.io import datafile
    system = datafile('tests/data/pdb1g8p.ent', format='pdb').read('system')

    sheet = system.sub(secondary_structure='E', secondary_id=1)
    coordinates = sheet.sub(atom_name='CA').r_array
    normals = beta_sheet_normals(coordinates, sheet.sub(atom_name='C').r_array, sheet.sub(atom_name='O').r_array)

    ribbon = GeomRibbon(Aes(xyz=coordinates, normals=normals))
    reps = ribbon.produce(Aes())
    eq_(reps[0]['rep_type'], 'ribbon')
    npeq_(reps[0]['options']['coordinates'], coordinates)
    npeq_(reps[0]['options']['normals'], normals)


def test_geom_cartoon():
    # For this test we need chemlab
    from chemlab.io import datafile
    system = datafile('tests/data/pdb1g8p.ent', format='pdb').read('system')

    cartoon = GeomProteinCartoon(Aes(xyz=system.r_array,
                                     types=system.atom_name,
                                     secondary_id=system.secondary_id,
                                     secondary_type=system.secondary_structure))

    reps = cartoon.produce(Aes())

    eq_(reps[0]['rep_type'], 'ribbon')
    # npeq_(reps[0]['options']['coordinates'], coordinates)
    # npeq_(reps[0]['options']['normals'], normals)
