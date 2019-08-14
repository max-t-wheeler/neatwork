import requests
import time

from cache import Cache

BASE_URL = 'https://api.discogs.com'


class DiscogsClient:
    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Discogs token={token}'})

        self.data = Cache()

        self.artists = Cache()
        self.labels = Cache()
        self.masters = Cache()
        self.releases = Cache()

        self.node = {
            'artist': Cache(),
            'label': Cache(),
            'master': Cache(),
            'release': Cache(),
        }

    def get_resource(self, resource_id, resource_type):
        # resource = self.node[resource_type].get_item(resource_id, resource_type)
        resource = self.data.get_item(resource_id, resource_type + 's')
        # cached_resource = resource
        # print(resource)

        if resource is not None:
            return resource

        # print(self._url(f'{resource_type + "s/" + str(resource_id)}'))

        time.sleep(1)
        resp = requests.get(self._url(f'{resource_type + "s/" + str(resource_id)}'))
        resource = resp.json()

        if resource_type == 'artist':
            if 'members' in resource.keys():
                resource['type'] = 'group'
            else:
                resource['type'] = 'member'
        elif resource_type == 'label':
            resource['type'] = 'label'
        else:
            resource['type'] = 'release'

        # if cached_resource is None:
        self.data.set_item(resource, resource_id, resource_type + 's')

        return resource

    def get_releases(self, resource):
        time.sleep(1)
        resp = requests.get(resource)
        releases = resp.json()

        return releases

    def get_associations(self, pk):
        u = self.get_resource(pk)
        if 'members' in u.keys():
            pass
        if 'groups' in u.keys():
            pass
        if 'sublabels' in u.keys():
            pass
        if 'parent_label' in u.keys():
            pass

    def get_collaborations(self, pk):
        pass

    def get_discography(self, pk):
        resource_type = pk.split('/')[0]
        releases = self.node[resource_type].get_item(pk)

        if releases is not None:
            return releases

        resp = requests.get(self._url(f'{pk}'))
        resource = resp.json()

        return releases

    def search(self, query, **kwargs):
        time.sleep(1)

        query_type = kwargs['type']
        resp = requests.get(
            self._url('database/search?q=' + query + '&type=' + query_type + '&per_page=100'),
            headers=self.session.headers
        )
        search_results = resp.json()

        return search_results

    def _url(self, path):
        return f'{BASE_URL}/{path}'
