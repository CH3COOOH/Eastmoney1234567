"""命令行工具：从基金 xlsx 文件生成历史价格折线图。

用法示例：
    python k-wall.py -f funds.xlsx
    python k-wall.py -f funds.xlsx -d 180 -r nearest
    python k-wall.py -f funds.xlsx --headless -o result.png
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
from math import ceil
import time

from em1234567 import EM1234567
import cal

plt.rcParams['font.sans-serif']=['Microsoft YaHei']

class HistoryCurve:
	"""根据基金列表生成历史价格折线图并计算变化率。"""

	def __init__(self, fname, daysAgo=365, rate='peak', headless=False, img_save_path=None):
		"""初始化历史曲线生成器。

		Parameters:
		    fname (str): xlsx 文件路径，第一列为基金代码，第二列为基金名称。
		    daysAgo (int): 向前计算历史数据的天数，默认 365。
		    rate (str): 变化率计算方式，'peak' 或 'nearest'。
		    headless (bool): 是否启用无头模式，直接保存图像而不弹出窗口。
		    img_save_path (str|None): 无头模式时图像保存路径。
		"""
		# rate 表示生成的折线图中标记的点类型
		# 'peak' 表示寻找区间中的最大值，计算到当前的变化率
		# 'nearest' 表示寻找最近的峰值/谷值，计算到当前的变化率
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		self.daysAgo = daysAgo
		self.rateType = rate
		self.headless = headless
		self.img_save_path = img_save_path

		if headless:
			if not img_save_path:
				raise ValueError("无头模式下必须提供图像保存路径。")
				sys.exit(1)
			plt.switch_backend('Agg')

	def __getDataFromEM1234567(self, code):
		em = EM1234567(code)
		return em.getHistoryPlotJson()


	def update(self):
		

		n_fund = len(self.codes)
		n_nxn = ceil(n_fund ** .5)
		plt.figure(figsize=(n_nxn * 4, n_nxn * 3))

		for i in range(n_fund):
			print('[%s] %s' % (self.codes[i], self.names[i]))

			xy_points = self.__getDataFromEM1234567(self.codes[i])

			## Extract curve data from array
			x_time, y_value = cal.extractDataFromDays(xy_points, self.daysAgo)

			ax = plt.subplot(n_nxn, n_nxn, i+1)
			ax.grid(True)
			ax.set_title('[%s] %s' % (self.codes[i], self.names[i]), pad=8)
			# 画出涨跌折线图
			ax.plot(x_time, y_value, zorder=1)

			t_color = 'red'
			if self.rateType == 'peak':
				## Get peak and value now
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

		plt.tight_layout(pad=2.0)
		plt.subplots_adjust(hspace=0.4, wspace=0.35, top=0.92)

		if self.headless:
			plt.savefig(self.img_save_path, bbox_inches='tight', dpi=150, format='jpg')
			plt.close()
		else:
			plt.show()


def parse_args():
	parser = argparse.ArgumentParser(
		description='生成基金历史价格折线图，并计算当前点的变化率。'
	)
	parser.add_argument('-f', '--file', required=True,
							dest='fname', metavar='XLSX',
							help='输入 xlsx 文件路径，第一列为基金代码，第二列为基金名称。')
	parser.add_argument('-d', '--days', type=int, default=365,
							help='向前计算历史数据的天数，默认 365。')
	parser.add_argument('-r', '--rate', choices=['peak', 'nearest'], default='peak',
							help="变化率计算方式：'peak' 查找区间峰值，'nearest' 查找最近峰/谷。")
	parser.add_argument('--headless', action='store_true',
							help='启用无头模式，直接保存图像而不弹出窗口。')
	parser.add_argument('-o', '--output', metavar='PATH',
							help='无头模式下保存图像的输出路径。')
	return parser.parse_args()


if __name__ == '__main__':
	args = parse_args()
	hc = HistoryCurve(
		args.fname,
		args.days,
		args.rate,
		args.headless,
		args.output,
	)
	hc.update()
