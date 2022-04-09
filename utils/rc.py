from csv import field_size_limit
import os
import yaml

MARARC=os.path.join(os.path.expanduser("~"), ".mararc")

def load_token(filename=MARARC) -> str:
    if not os.path.isfile(filename):
        raise FileNotFoundError('{} not exists'.format(filename))

    with open(filename, 'r') as r:
        try:
            rc = yaml.safe_load(r)
        except yaml.error.YAMLError:
            raise SyntaxError('cannot parse {}'.format(filename))

    token = rc.pop("token", None)
    if token is None:
        raise SyntaxError('token is missing in {}'.format(filename))

    return token