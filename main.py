import matplotlib.pyplot as plt

from mara.mara import Data, Plot

if __name__ == '__main__':
    d = Data('001', compare=True)
    df = d.get(dict(CataC='CataA + CataB'))

    p = Plot()
    p.draw(df, title='CataC', separate=True, kind='line')

    plt.show()