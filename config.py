import yaml


def read_yaml(path):
    with open(path, 'r') as doc:
        return yaml.load(doc)


def load_yaml(path):
    cfg = read_yaml(path)
    if 'include' in cfg and cfg['include']:
        for inc in cfg['include']:
            inc_yaml = read_yaml(inc)
            cfg = {**cfg, **inc_yaml}
    return cfg