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


	def update(self):

		n_fund = len(self.codes)
		n_nxn = ceil(n_fund ** .5)

		for i in range(n_fund):
			print('[%s] %s' % (self.codes[i], self.names[i]))

			em = EM1234567(self.codes[i])
			xy_points = np.array(em.getHistoryPlot())
			x_time = None
			y_value = None
			
			if self.daysAgo >= xy_points.shape[0]:
				x_time = xy_points[:, 0].astype(np.int64)
				y_value = xy_points[:, 1]
				# x_time_date = map(lambda t: time.strftime('%Y%m%d', time.localtime(t/1000)), x_time)
				# x_time_date = np.array(list(x_time)).astype(np.int)
			else:
				x_time = xy_points[-self.daysAgo:, 0].astype(np.int64)
				y_value = xy_points[-self.daysAgo:, 1]

			plt.subplot(n_nxn, n_nxn, i+1)
			plt.title('[%s] %s' % (self.codes[i], self.names[i]))
			plt.plot(x_time, y_value)
			# plt.xticks(x_time, x_time_date)

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
