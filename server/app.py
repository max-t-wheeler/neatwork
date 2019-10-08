from flask import Flask, g, jsonify, request
from flask_cors import CORS

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


@app.route('/get_resource_data', methods=['POST'])
def get_resource_data():
    response_object = {
        'status': 'success'
    }

    resource_data = request.get_json()

    resource_id = resource_data['resource_id']
    resource_type = resource_data['resource_type']

    response_object['resource_data'] = app.config['CLIENT'].get_resource(resource_id, resource_type)

    return jsonify(response_object)


@app.route('/get_release_data', methods=['POST'])
def get_release_data():
    response_object = {
        'status': 'success'
    }

    resource_data = request.get_json()

    resource_id = resource_data['resource_id']

    response_object['release_data'] = app.config['CLIENT'].get_resource(resource_id)

    return jsonify(response_object)


if __name__ == '__main__':
    app.run()

