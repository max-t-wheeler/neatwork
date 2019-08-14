import requests
import time

from cache import Cache

BASE_URL = 'https://api.discogs.com'


class DiscogsClient:
    def __init__(self, user_agent, key, secret):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': f'{user_agent}', 'Authorization': f'Discogs key={key}, secret={secret}'})
        self.data = Cache()

    def get_resource(self, resource_id, resource_type):
        resource = self.data.get_item(resource_id, resource_type + 's')

        if resource is not None:
            return resource

        time.sleep(1)
        resp = requests.get(
            self._url(f'{resource_type + "s/" + str(resource_id)}'),
            headers=self.session.headers
        )
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

        self.data.set_item(resource, resource_id, resource_type + 's')

        return resource

    def get_releases(self, resource):
        time.sleep(1.1)
        resp = requests.get(resource, headers=self.session.headers)
        releases = resp.json()

        return releases

    def search(self, query, **kwargs):
        query_type = kwargs['type']
        resp = requests.get(
            self._url('database/search?q=' + query + '&type=' + query_type + '&per_page=100'),
            headers=self.session.headers
        )
        search_results = resp.json()

        return search_results

    def _url(self, path):
        return f'{BASE_URL}/{path}'
