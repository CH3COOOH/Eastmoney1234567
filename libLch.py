import numpy as np

import cal
from em1234567 import EM1234567

class Fund:
	def __init__(self, fund_code, src_dir):
		self.fund_code = fund_code
		self.em = EM1234567(fund_code)
		self.day_x_value = np.array(self.em.loadHistoryPlotFromLocal(src_dir)).astype(float)


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


	def getMoreThanRate(self, iDaysBefore, iDaysAfter, fChangeRate):
		aDataSeries = 100 * self.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		# c = 0
		# if fChangeRate >= 0:
		# 	c = len(np.where(aDataSeries >= fChangeRate)[0])
		# else:
		# 	c = len(np.where(aDataSeries <= fChangeRate)[0])
		c = len(np.where(cal.symbol(fChangeRate) * aDataSeries >= cal.symbol(fChangeRate) * fChangeRate)[0])
		r1 = c / len(aDataSeries)
		aDataHalf = aDataSeries[np.where(cal.symbol(fChangeRate) * aDataSeries >= 0)]
		c = len(np.where(cal.symbol(fChangeRate) * aDataHalf >= cal.symbol(fChangeRate) * fChangeRate)[0])
		r2 = c / len(aDataHalf)
		return r1, r2


	def getPredictByChangeRate(self, iDaysBefore, iDaysAfter, fChangeRate, offset=.3, pdtDays=3):
		aRateArray = 100 * self.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		idx_up = np.where(aRateArray<=fChangeRate+offset)[0]
		idx_down = np.where(aRateArray>=fChangeRate-offset)[0]
		idx_hit = np.array(list(set(idx_up) & set(idx_down))).astype(int)
		print(idx_hit)
		dResult = {}
		for d in range(1, pdtDays+1):
			if (idx_hit+iDaysAfter+d)[-1] > len(aRateArray)-1:
				continue
			v_now = self.day_x_value[idx_hit+iDaysAfter]
			v_after = self.day_x_value[idx_hit+iDaysAfter+d]
			rate = (v_after - v_now) / v_now * 100
			# print(rate)
			dResult[d] = [rate.min(), rate.max(), rate.mean()]
		return dResult

	def write_csv(self, data_sheet, path):
		np.savetxt(path, data_sheet, delimiter=',')


def test(code, src):
	f = Fund(code, src)
	r, d = f.getContinualRateAndDays(720)
	f.write_csv(r, 'rate.csv')
	f.write_csv(d, 'days.csv')

if __name__ == '__main__':
	import sys
	test(sys.argv[1], sys.argv[2])