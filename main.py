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
            if not 'plots' in template:
                fatal("template file doesn't contain plots")

        except yaml.YAMLError:
            fatal('parse template file error')

    data = Data(arg.symbols, compare=arg.compare)
    p = Plot()
    for t in template['plots']:
        if not 'name' in t:
            warnings.warn('bad plot, no name')
            continue

        catlog = t['name'] if not 'formula' in t else {t['name']:t['formula']}

        df = data.get(catalog=catlog)

        separate = True if 'separate' in t and t['separate'] else False
        kind = t['kind'] if 'kind' in t else 'line'

        p.draw(df, title=t['name'], separate=separate, kind=kind)

    plt.show()

    return

if __name__ == '__main__':
    main()