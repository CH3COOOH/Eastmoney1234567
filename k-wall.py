import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from math import ceil
import time

from em1234567 import EM1234567
import cal

plt.rcParams['font.sans-serif']=['Microsoft YaHei']

class HistoryCurve:
	def __init__(self, fname, daysAgo=365, rate='peak'):
		# rate表示生成的折线图中标记的点类型
		# 'peak'表示寻找区间中的最大值，计算到当前的变化率
		# 'nearest'表示寻找最近的峰值/谷值，计算到当前的变化率
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		self.daysAgo = daysAgo
		self.rateType = rate

	def __getDataFromEM1234567(self, code):
		em = EM1234567(code)
		return em.getHistoryPlotJson()


	def update(self):
		

		n_fund = len(self.codes)
		n_nxn = ceil(n_fund ** .5)

		for i in range(n_fund):
			print('[%s] %s' % (self.codes[i], self.names[i]))

			xy_points = self.__getDataFromEM1234567(self.codes[i])

			## Extract curve data from array
			x_time, y_value = cal.extractDataFromDays(xy_points, self.daysAgo)

			plt.subplot(n_nxn, n_nxn, i+1)
			plt.grid()
			plt.title('[%s] %s' % (self.codes[i], self.names[i]))
			# 画出涨跌折线图
			plt.plot(x_time, y_value, zorder=1)

			t_color = 'red'
			if self.rateType == 'peak':
				## Get peak and value now
				# y_now = y_value[-1]
				# y_max = np.max(y_value)
				# idx_peak = np.where(y_value==y_max)
				# rate = (y_now - y_max) / y_max * 100
				y_now, y_max, idx, rate = cal.getPeakAndDropRate(y_value)

				if rate < 0:
					t_color = 'green'
					plt.scatter(x_time[idx], y_value[idx], s=7.5, c='red', zorder=2)
				else:
					rate = (y_now - y_value[0]) / y_max * 100
					plt.scatter(x_time[0], y_value[0], s=7.5, c='green', zorder=2)

			elif self.rateType == 'nearest':
				idx, rate = cal.getHowMuchChangedFromPreviousPeakOrValley(y_value)
				if rate < 0:
					t_color = 'green'
					plt.scatter(x_time[idx], y_value[idx], s=7.5, c='red', zorder=2)
				else:
					plt.scatter(x_time[idx], y_value[idx], s=7.5, c='red', zorder=2)

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
		if len(sys.argv) == 4:
			hc = HistoryCurve(f_xlsx, daysAgo, sys.argv[3])
		else:
			hc = HistoryCurve(f_xlsx, daysAgo)

	else:
		hc = HistoryCurve(f_xlsx)

	hc.update()
