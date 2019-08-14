from flask import Flask, g, jsonify, request
from flask_cors import CORS
import time

from config import USER_AGENT, API_TOKEN, API_KEY, API_SECRET
from discogs_client import Client
from discogs_client2 import DiscogsClient
from discograph2 import DiscoGraph

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

app.config['CLIENT'] = Client(USER_AGENT, user_token=API_TOKEN)
app.config['CLIENT2'] = DiscogsClient(USER_AGENT, API_KEY, API_SECRET)

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
        resource_url = graph_data['resource_url']
        source_type = graph_data['source_type'].lower()
        target_type = graph_data['target_type'].lower()

        # construct graph
        graph = DiscoGraph(app.config['CLIENT'], resource_url, connection, source_type, target_type, 'node_link')

        graph.generate(num_steps)
        response_object['graph_data'] = graph.export()
        app.config['GRAPH_DATA'] = response_object['graph_data']
    else:
        response_object['graph_data'] = app.config['GRAPH_DATA']
    return jsonify(response_object)


@app.route('/get_graph_data', methods=['GET', 'POST'])
def get_graph_data():
    response_object = {
            'status': 'success'
    }
    if request.method == 'POST':
        graph_data = request.get_json()

        connection = graph_data['connection'].lower()
        num_steps = int(graph_data['num_steps'])
        source_id = str(graph_data['source_id'])
        source_type = graph_data['source_type'].lower()
        target_type = graph_data['target_type'].lower()

        # construct graph
        graph = DiscoGraph(app.config['CLIENT2'], connection, source_id, source_type, target_type, 'node_link')
        graph.generate(num_steps)

        # graph = {
        #     'nodes': [app.config['CLIENT2'].get_resource(source_id, source_type)],
        #     'links': []
        # }

        # response_object['graph_data'] = graph

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


@app.route('/get_search_results', methods=['GET', 'POST'])
def get_search_results():
    response_object = {
        'status': 'success'
    }
    if request.method == 'POST':
        query_data = request.get_json()

        count = query_data['count']
        source_type = query_data['source_type']
        text = query_data['text']

        search_data = app.config['CLIENT2'].search(text, type=source_type)
        response_object['query_data'] = search_data['results'][0:count]
    else:
        response_object['query_data'] = app.config['QUERY_DATA']
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()

