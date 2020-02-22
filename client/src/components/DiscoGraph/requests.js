import axios from 'axios';

export function getSearchResults(payload) {
    const path = 'http://localhost:5000/get_search_results';

    console.log('Retrieving search results...');

    return axios.post(path, payload)
    .then(res => res.data.query_data);
}

export function getGraphData(payload) {
    const path = 'http://localhost:5000/get_graph_data';

    console.log('Requesting graph data...');

    return axios.post(path, payload)
    .then(res => res.data.graph_data);
}

export function getResourceData(resourceId, resourceType) {
    const path = 'http://localhost:5000/get_resource_data';

    console.log('Requesting resource data...');

    return axios.post(path, {
        resource_id: resourceId,
        resource_type: resourceType,
    })
    .then(res => res.data.resource_data)
    .catch(error => console.log(error));
}

export function getReleaseData(resourceId, resourceType) {
    const path = 'http://localhost:5000/get_release_data';

    console.log('Requesting release data...');

    return axios.post(path, {
        resource_id: resourceId,
        resource_type: resourceType,
    })
    .then(res => res.data.release_data)
    .catch(error => console.log(error));
}
