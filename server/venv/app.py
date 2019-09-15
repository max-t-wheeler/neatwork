from flask import Flask, g, jsonify, request
from flask_cors import CORS
import time

from config import USER_AGENT, API_KEY, API_SECRET
from discogs_client import DiscogsClient
from discograph import DiscoGraph

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

app.config['CLIENT'] = DiscogsClient(USER_AGENT, API_KEY, API_SECRET)

# enable CORS
CORS(app, resource={r'/*': {'origins': '*'}})


@app.route('/get_graph_data', methods=['POST'])
def get_graph_data():
    response_object = {
            'status': 'success'
    }

    graph_data = request.get_json()

    connection = graph_data['connection'].lower()
    num_steps = int(graph_data['num_steps'])
    source_id = str(graph_data['source_id'])
    source_type = graph_data['source_type'].lower()
    target_type = graph_data['target_type'].lower()

    # construct graph
    graph = DiscoGraph(app.config['CLIENT'], connection, num_steps, source_id, source_type, target_type, 'node_link')
    graph.generate()

    response_object['graph_data'] = graph.export()
    app.config['GRAPH_DATA'] = response_object['graph_data']

    return jsonify(response_object)


@app.route('/get_node_data', methods=['POST'])
def get_node_data():
    response_object = {
            'status': 'success'
        }

    node_data = request.get_json()

    node_id = node_data['id']
    node_type = node_data['type']

    # request node data
    node = app.config['VERTEX'][node_type](node_id)

    response_object['node_data'] = {
        'uri': node.url,
        'urls': node.urls
    }

    return jsonify(response_object)


@app.route('/get_search_results', methods=['POST'])
def get_search_results():
    response_object = {
        'status': 'success'
    }

    query_data = request.get_json()

    count = query_data['count']
    source_type = query_data['source_type']
    text = query_data['text']

    search_data = app.config['CLIENT'].search(text, type=source_type)
    response_object['query_data'] = search_data['results'][0:count]

    return jsonify(response_object)


if __name__ == '__main__':
    app.run()

