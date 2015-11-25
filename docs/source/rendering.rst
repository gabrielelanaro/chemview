=================
Offline Rendering
=================

Chemview interactive visualization are "nice", but are not something you would
put in a publication. In this case we can use `Povray <http://www.povray.org/>`_
throught the vapory bindings.

On Ubuntu, you can install povray with::

    sudo apt-get install povray

And installing vapory is as easy as::

    pip install vapory

Scene dictionary format:

{ 'representations': [],
  'camera': {'aspect' : 10,
             'location': [0, 0, 0],
             'target': [0, 0, 0],
             'quaternion': [0, 0, 0, 1],
             'vfov': 10},
  'lights': [{'direction'}],
  'shadows' : False,
}
