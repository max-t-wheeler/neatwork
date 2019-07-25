from flask import Flask, g, jsonify, request
from flask_cors import CORS
import time

import config
import discogs_client
import discograph

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['CLIENT'] = discogs_client.Client('Neatwork - Discogs', user_token=config.API_TOKEN)
app.config['VERTEX'] = {
    'artist': app.config['CLIENT'].artist,
    'group': app.config['CLIENT'].artist,
    'label': app.config['CLIENT'].label,
    'master': app.config['CLIENT'].release,
    'member': app.config['CLIENT'].artist,
    'release': app.config['CLIENT'].release
}

# enable CORS
CORS(app, resource={r'/*': {'origins': '*'}})

@app.route('/generate_graph', methods=['GET', 'POST'])
def generate_graph():
    response_object = {
            'status': 'success'
    }
    if request.method == 'POST':
        graph_data = request.get_json()

        connection = graph_data['connection'].lower()
        num_steps = int(graph_data['num_steps'])
        root = graph_data['name'].lower()
        source_type = graph_data['source_type'].lower()
        target_type = graph_data['target_type'].lower()

        # construct graph
        graph = discograph.DiscoGraph(app.config['CLIENT'], root, connection, source_type, target_type, 'node_link')

        graph.constructor(num_steps)
        response_object['graph_data'] = graph.export()
        app.config['GRAPH_DATA'] = response_object['graph_data']
    else:
        response_object['graph_data'] = app.config['GRAPH_DATA']
    return jsonify(response_object)


@app.route('/get_node_data', methods=['GET', 'POST'])
def get_node_data():
    response_object = {
            'status': 'success'
        }
    if request.method == 'POST':
        node_data = request.get_json()

        node_id = node_data['id']
        node_type = node_data['type']

        # request node data
        node = app.config['VERTEX'][node_type](node_id)

        response_object['node_data'] = {
            'uri': node.url,
            'urls': node.urls
        }

    else:
        response_object['graph_data'] = app.config['GRAPH_DATA']
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
