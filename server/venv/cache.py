class Cache:
    def __init__(self):
        self.items = {
            'artists': {},
            'labels': {},
            'masters': {},
            'releases': {}
        }

    def get_item(self, item_id, item_type):
        try:
            item = self.items[item_type][item_id]
            print('cache hit')
            return item
        except KeyError:
            print('cache miss')

    def set_item(self, item, item_id, item_type):
        self.items[item_type][item_id] = item
