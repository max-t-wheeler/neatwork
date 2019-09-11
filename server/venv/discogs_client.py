import requests
import time

from cache import Cache

BASE_URL = 'https://api.discogs.com'


class DiscogsClient:
    def __init__(self, user_agent, key, secret):

        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': f'{user_agent}',
                'Authorization': f'Discogs key={key}, secret={secret}'
             }
        )
        self.data = Cache()

    def get_resource(self, resource_id, resource_type):

        resource = self.data.get_item(resource_id, resource_type + 's')

        if resource is not None:
            return resource

        resp = requests.get(
            self._url(f'{resource_type}s/{str(resource_id)}'),
            headers=self.session.headers
        )

        if resp.status_code == 200:

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

        if resp.status_code == 404:
            print('Resource not found')
            return

        if resp.status_code == 429:
            print('Waiting...')
            time.sleep(60)
            return self.get_resource(resource_id, resource_type)

    def get_releases(self, resource):

        resp = requests.get(resource, headers=self.session.headers)

        if resp.status_code == 200:
            return resp.json()

        if resp.status_code == 404:
            print('Resource not found')
            return

        if resp.status_code == 429:
            print('Waiting...')
            time.sleep(60)
            return self.get_releases(resource)

    def search(self, query, **kwargs):
        query_type = kwargs['type']
        resp = requests.get(
            self._url(f'database/search?q={query}&type={query_type}&per_page=100'),
            headers=self.session.headers
        )

        if resp.status_code == 200:
            search_results = resp.json()
            return search_results

        if resp.status_code == 404:
            print('Resource not found')
            return

        if resp.status_code == 429:
            print('Waiting...')
            time.sleep(60)
            return self.search(query, **kwargs)

    def _url(self, path):
        return f'{BASE_URL}/{path}'
