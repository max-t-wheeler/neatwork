import axios from 'axios';

export function getSearchResults(payload, context) {
    const path = 'http://localhost:5000/get_search_results';

    console.log('Retrieving search results...');

    axios.post(path, payload)
    .then((res) => {
        context.queryData = res.data.query_data;
        console.log('Search results retrieved');
    })
    .catch((error) => {
        context.display.loading = false;
        context.failureMessage = 'Failed to retrieve search results';
        context.display.failureMessage = true;
        console.log(error);
    });
}

export function getGraphData(payload, context) {
    const path = 'http://localhost:5000/get_graph_data';

    console.log('Requesting graph data...');

    axios.post(path, payload)
    .then((res) => {
        context.graphData = res.data.graph_data;
        context.display.loading = false;
        context.display.graph = true;
        console.log('Graph generated');
    })
    .catch((error) => {
        context.display.loading = false;
        context.failureMessage = 'Failed to generate graph data';
        context.display.failureMessage = true;
        console.log(error);
    });
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

export function getReleaseData(resourceId) {
    const path = 'http://localhost:5000/get_release_data';

    console.log('Requesting node data...');

    return axios.post(path, {
        resource_id: resourceId,
    })
    .then(res => res.data.release_data)
    .catch(error => console.log(error));
}
