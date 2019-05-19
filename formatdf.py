class DFFormatter:
    def __init__(self, map):
        self.map = map

    def map_search(self, name):
        for k in self.map:
            if k in name:
                return self.map[k]
        return None

    def format(self, df):
        columns = []
        for name in df.columns.tolist():
            x = {
                'id': name,
                'name': name,
            }
            found = self.map_search(name)
            merge = found if found is not None else {
                'type': 'text'
            }
            columns.append(dict(x, **merge))
        return columns