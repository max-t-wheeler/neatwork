import discogs_client
import json
import networkx as nx
import numpy as np
import time


class DiscoGraph:

    def __init__(self, client, root, connection, source_type, target_type, graph_type=None):

        self.client = client
        self.connection = connection

        if graph_type == 'tree':
            self.graph = nx.DiGraph()
        elif connection == 'association' and source_type != target_type:
            self.graph = nx.MultiGraph()
        else:
            self.graph = nx.Graph()

        self.graph_type = graph_type
        self.query = client.search(root, type=source_type)[0]
        self.root_data = self.query.data
        self.source_type = source_type
        self.target_type = target_type

    def append_node(self, source, target, node_type, neighbors=None, offset=0):
        if neighbors is not None:
            neighbors.append(target['resource_url'])

        name = 'name'

        if node_type in ['master', 'release']:
            name = 'title'

        self.graph.add_edge(source['id'], target['id'], offset=offset)
        self.graph.add_node(target['id'], name=target[name], type=node_type)

    def crawl_releases(self, root, releases):
        if self.target_type == 'artist':
            for release in releases:
                time.sleep(1)
                artists = self.client._get(release['resource_url'])['artists']
                for artist in artists:
                    self.append_node(root, artist, self.target_type, offset=100*np.random.random(1)[0])
        elif self.target_type == 'label':
            for release in releases:
                time.sleep(1)
                labels = self.client._get(release['resource_url'])['labels']
                for label in labels:
                    self.append_node(root, label, self.target_type, offset=100 * np.random.random(1)[0])
        else:
            for release in releases:
                self.append_node(root, release, self.target_type)

    def filter_releases(self, releases, limited_releases):
        if self.source_type == 'artist':
            if self.target_type == 'master':
                for release in releases['releases']:
                    try:
                        if release['role'] == 'Main' and release['type'] == 'master':
                            limited_releases.append(release)
                    except:
                        print('Encountered error while filtering releases')
            else:
                for release in releases['releases']:
                    if release['role'] == 'Main' and release['type'] == 'master':
                        time.sleep(1)
                        main_release = self.client._get('https://api.discogs.com/releases/' + str(release['main_release']))
                        limited_releases.append(main_release)
                    if release['role'] == 'Main' and release['type'] == 'release' and (release['format'].find('Album') != -1 or release['format'].find('Single') != -1):
                        limited_releases.append(release)
        else:
            for release in releases['releases']:
                try:
                    if release['format'].find('Album') != -1 or release['format'].find('Single') != -1:
                        limited_releases.append(release)
                except:
                    print('Encountered error while filtering releases')

    def crawl_dislike_associations(self, root):
        releases = self.client._get(root['releases_url'] + '?per_page=500')
        num_pages = releases['pagination']['pages']

        releases_ = []

        self.filter_releases(releases, releases_)

        count = 1

        while count < num_pages:
            time.sleep(1)
            releases = self.client._get(releases['pagination']['urls']['next'])
            self.filter_releases(releases, releases_)
            count += 1

        print(len(releases_))
        self.crawl_releases(root, releases_)

    def crawl_like_associations(self, root, depth):

        count = 0
        root_url = root['resource_url']
        links = [root_url]
        visited = [root_url]

        while count < depth:

            neighbors = self.explore_neighbors(links)
            links = []

            for neighbor in neighbors:
                if neighbor not in visited:
                    links.append(neighbor)
                    visited.append(neighbor)

            count += 1

    # for each node
    #   discover all children
    #   add each to the graph
    #   and link each child to its parent
    # return the list of children for further exploration
    def explore_neighbors(self, nodes):

        neighbors = []

        if self.source_type == 'artist':
            for node in nodes:
                time.sleep(1)
                try:
                    v = self.client._get(node)
                    if 'members' in v.keys():
                        for member in v['members']:
                            self.append_node(v, member, 'member', neighbors)
                    elif 'groups' in v.keys():
                        for group in v['groups']:
                            self.append_node(v, group, 'group', neighbors)
                except discogs_client.exceptions.HTTPError:
                    print('HTTP Error')
        else:
            for node in nodes:
                time.sleep(1)
                try:
                    v = self.client._get(node)
                    if 'sublabels' in v.keys():
                        for label in v['sublabels']:
                            self.append_node(v, label, 'label', neighbors)
                    if 'parent_label' in v.keys() and v['parent_label']['id'] not in self.graph:
                        self.append_node(v, v['parent_label'], 'label', neighbors)
                except discogs_client.exceptions.HTTPError:
                    print('HTTP Error')

        return neighbors

    # construct a graph by starting with a root node
    # and discovering neighbors up to a given depth
    # note that cycles are allowed in the output
    # but prevented while crawling
    def constructor(self, depth):

        root = self.root_data['resource_url']
        u = self.client._get(root)

        if self.source_type == 'artist':
            if 'members' in u.keys():
                self.graph.add_node(u['id'], name=u['name'], type='group')
            else:
                self.graph.add_node(u['id'], name=u['name'], type='member')
        elif self.source_type == 'label':
            self.graph.add_node(u['id'], name=u['name'], type='label')
        else:
            print('Invalid query type provided in discograph.constructor')
            return 0

        if self.connection == 'association':
            if self.source_type == self.target_type:
                self.crawl_like_associations(u, depth)
            else:
                self.crawl_dislike_associations(u)
        elif self.connection == 'collaboration':
            pass
        else:
            self.crawl_dislike_associations(u)

        nx.set_node_attributes(self.graph, dict(self.graph.degree), 'degree')

    def export(self, root=None):

        if self.graph_type is 'node_link':
            graph_json = nx.node_link_data(self.graph)
        elif self.graph_type is 'cytoscape':
            graph_json = nx.cytoscape_data(self.graph)
        elif self.graph_type is 'tree':
            if nx.is_directed(self.graph):
                graph_json = nx.tree_data(self.graph, root)
            else:
                print('Graph passed into export data is not directed')
                return 0

        return graph_json
