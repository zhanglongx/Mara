import argparse
import yaml
import warnings
import matplotlib.pyplot as plt

from mara.mara import Data, Plot

def fatal(*args):
    warnings.warn(*args)
    exit(1)

def main():
    opt = argparse.ArgumentParser(description='Mara main program')

    opt.add_argument('-c', '--compare', action='store_true', default=False, 
                        help='to compare with industry average')
    opt.add_argument('-t', '--template', type=str, default="mara.yaml",
                        help='template file in .yaml [mara.yaml]')
    opt.add_argument('symbols', type=str, nargs='+', help='symbols input')

    arg = opt.parse_args()

    with open(arg.template, "r") as stream:
        try:
            template = yaml.safe_load(stream)
            if not 'plots' in template or not 'global' in template:
                fatal("template file doesn't contain plots/global")

        except yaml.YAMLError:
            fatal('parse template file error')

    globalSettings = template.pop('global', None)
    token = globalSettings.pop('token', None)
    if token is None:
        fatal('global: missing token')

    # FIXME: also for formulas
    fields = [t['name'] for t in template['plots'] if 'name' in t]
    
    data = Data(arg.symbols, token, fields=fields, compare=arg.compare)

    p = Plot()
    for t in template['plots']:
        name = t.pop('name', None)
        if name is None:
            warnings.warn('bad plot, no name')
            continue

        _ = t.pop('formula', None)
        catalog = name if _ is None else {name: _}

        df = data.get(catalog=catalog)

        separate = t.pop('separate', True)
        p.draw(df, title=name, separate=separate, **t)

    plt.show()

    return

if __name__ == '__main__':
    main()