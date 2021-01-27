import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from math import ceil
import time
from em1234567 import EM1234567

plt.rcParams['font.sans-serif']=['Microsoft YaHei']

class HistoryCurve:
	def __init__(self, fname, daysAgo=365):
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		self.daysAgo = daysAgo


	def __getDataFromEM1234567(self, code):
		em = EM1234567(code)
		return np.array(em.getHistoryPlotJson())


	def update(self):

		n_fund = len(self.codes)
		n_nxn = ceil(n_fund ** .5)

		for i in range(n_fund):
			print('[%s] %s' % (self.codes[i], self.names[i]))

			xy_points = self.__getDataFromEM1234567(self.codes[i])
			x_time = None
			y_value = None

			## Extract curve data from array
			if self.daysAgo < xy_points.shape[0]:
				x_time = np.array(list(range(0, self.daysAgo)))
				y_value = xy_points[-self.daysAgo:, 1]
			else:
				## The set backtracking days is too big
				x_time = np.array(list(range(0, xy_points.shape[0])))
				y_value = xy_points[:, 1]

			## Get peak and value now
			y_now = y_value[-1]
			y_max = np.max(y_value)
			idx_peak = np.where(y_value==y_max)
			rate = (y_now - y_max) / y_max * 100

			plt.subplot(n_nxn, n_nxn, i+1)
			plt.grid()
			plt.title('[%s] %s' % (self.codes[i], self.names[i]))
			plt.plot(x_time, y_value, zorder=1)

			t_color = 'red'
			if rate < 0:
				t_color = 'green'
				plt.scatter(x_time[idx_peak], y_value[idx_peak], s=7.5, c='red', zorder=2)
			else:
				rate = (y_now - y_value[0]) / y_max * 100
				plt.scatter(x_time[0], y_value[0], s=7.5, c='green', zorder=2)

			plt.text(x_time[-1], y_value[-1], '%.2f%%' % rate,
				ha='right',
				c=t_color,
				zorder=3,
				bbox=dict(boxstyle="square",
					ec='grey',
					fc='white',
					alpha=.5
				))

		plt.show()


if __name__ == '__main__':
	import sys
	f_xlsx = sys.argv[1]
	if len(sys.argv) >= 3:
		daysAgo = int(sys.argv[2])
		hc = HistoryCurve(f_xlsx, daysAgo)
	else:
		hc = HistoryCurve(f_xlsx)
	
	hc.update()
