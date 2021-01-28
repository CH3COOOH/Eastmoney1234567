import numpy as np

from cal import *
from em1234567 import EM1234567

class Fund:
	def __init__(self, fund_code):
		self.fund_code = fund_code
		self.em = EM1234567(fund_code)
		self.day_x_value = self.em.getHistoryPlotJson()

	def getDiffValue(self, iDaysBefore):
		_, v = extractDataFromDays(self.day_x_value, iDaysBefore)
		return np.diff(v)

	def getDiffRate(self, iDaysBefore):
		_, v = extractDataFromDays(self.day_x_value, iDaysBefore)
		return np.diff(v) / v[:-1]

	def getContinualRate(self, iDaysBefore):
		def _symbol(value):
			if value >= 0:
				return 1
			else:
				return -1
		dfr = self.getDiffRate(iDaysBefore)
		container = []
		base = dfr[0] + _symbol(dfr[0]) * 1.

		for i in range(0, len(dfr) - 1):
			if (dfr[i]*100) * (dfr[i+1]*100) < 0.: # An and An+1 have different symbols
				# print(dfr[i] * dfr[i+1])
				container.append(base - _symbol(base) * 1.)
				base = dfr[i+1] + _symbol(dfr[i+1]) * 1.
			else:
				_ = base
				base = base * (_symbol(dfr[i+1]) * 1. + dfr[i+1])
		return np.array(container)

	def write_csv(self, data_sheet, path):
		np.savetxt(path, data_sheet, delimiter=',')


def test():
	f = Fund('001595')
	f.write_csv(f.getContinualRate(720), 'greatwall.csv')

if __name__ == '__main__':
	test()