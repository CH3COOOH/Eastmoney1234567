import numpy as np

import cal
from em1234567 import EM1234567

class Fund:
	def __init__(self, fund_code):
		self.fund_code = fund_code
		self.em = EM1234567(fund_code)
		self.day_x_value = self.em.getHistoryPlotJson()


	def getDiffValue(self, iDaysBefore):
		_, v = cal.extractDataFromDays(self.day_x_value, iDaysBefore)
		return np.diff(v)


	def getDiffRate(self, iDaysBefore):
		return cal.getDiffRate(self.day_x_value, iDaysBefore)


	def getContinualRateAndDays(self, iDaysBefore):
		rate, days = cal.getContinualRateAndDays(self.day_x_value, iDaysBefore)
		return rate, days

	def getRateAfterDaysFromOneDay(self, iDaysBefore, iDaysAfter):
		_, v = cal.extractDataFromDays(self.day_x_value, iDaysBefore)
		aRates = []
		for i in range(len(v) - iDaysAfter):
			aRates.append((v[i+iDaysAfter] - v[i]) / v[i])
		return np.array(aRates)


	def write_csv(self, data_sheet, path):
		np.savetxt(path, data_sheet, delimiter=',')


def test(code):
	f = Fund(code)
	r, d = f.getContinualRateAndDays(720)
	f.write_csv(r, 'rate.csv')
	f.write_csv(d, 'days.csv')

if __name__ == '__main__':
	import sys
	test(sys.argv[1])