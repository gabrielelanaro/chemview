'''Static export for viewing in  nbviewer (or the web)'''
import json
from IPython.display import display, Javascript, HTML

def display_static(viewer):
    '''Display a static version of the selected widget'''

    # First generate the serialized json
    def callback(content):
        display_json(content['json'])

    viewer._connect_event('serialize', callback)
    viewer._remote_call('_handle_serialize')


def display_json(json_data):
    # Load the modules with javascript
    requires = '''
    var prefix = "https://rawgit.com/gabrielelanaro/chemview/master/chemview/static/";

    require.config({
        paths: {
            'jquery': prefix + 'jquery.min',
            'jqueryui': prefix + 'jquery-ui.min',
            'exporter': prefix + 'objexporter.js',
            'three': prefix + 'three.min',
            'base64-arraybuffer': prefix + 'base64-arraybuffer',
            'ArcballControls' : prefix + 'ArcballControls',
            'chemview': prefix + 'chemview',
        },
        shim: {
            three: {
                exports: 'THREE'
            },

            chemview: {
                deps: ['three', 'ArcballControls', 'base64-arraybuffer'],
                exports: 'MolecularViewer'
            },

            ArcballControls: {
                deps: ['three'],
                exports: 'THREE.ArcballControls',
            },
        },
    });
    '''

    # Create canvas and attach a molecularviewer to it
    # Embed the json object
    displaycode = ('''
            <canvas id="molecular_viewer"></canvas>
            <script>
    
            require(['chemview'], function () {
                console.log('done loading');
                var canvas = $("#molecular_viewer").css({width: 400, height: 400});
                var mv = new MolecularViewer(canvas);
                var data = ''' + json.dumps(json_data) + ''';
    
                mv.deserialize(data);
                mv.animate();
    
                // Give it a nice zoom
                mv.controls.dollyIn(1.9);
    
                mv.resize(canvas.width(), canvas.height());
            });
    
            </script>
        ''')

    display(Javascript(requires))
    display(HTML(displaycode))
    #print displaycode