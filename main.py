import pandas as pd
import matplotlib.pyplot as plt

from pandas import *
from numpy.random import randn

class Plot:
	"""
	Plot the Figure.
	"""

	def __init__(self) -> None:
		pass

	def draw(self, x1, x2, title, separate=True, kind='line'):

		df = pd.concat([x1, x2], axis=1)

		if len(df.columns) == 1:
			separate = False

		if separate == False:
			df.plot(title=title, kind=kind)

		else:
			_, axes = plt.subplots(nrows=1, ncols=len(df.columns))

			for i, col in enumerate(df.columns):
				df[col].plot(title=title, kind=kind, ax=axes[i])

		return

	def show(self):
		plt.show()

		return

if __name__ == '__main__':

	ts = Series(randn(5), index=date_range('12/29/1999', periods=5))
	ts = ts.cumsum()

	df = DataFrame(randn(5), index=ts.index, columns=['A'])
	df = df.cumsum()

	ts = Series(randn(4), index=date_range('1/1/2000', periods=4))
	ts = ts.cumsum()

	df2 = DataFrame(randn(4), index=ts.index, columns=['B'])
	df2 = df2.cumsum()

	p = Plot()
	p.draw(df, df2, title='test1', kind='line', separate=True)

	p.draw(df, df2, title='test1', kind='bar', separate=False)

	p.show()