import numpy as np

import cal
from em1234567 import EM1234567

class Fund:
	def __init__(self, fund_code, src_dir):
		self.fund_code = fund_code
		self.em = EM1234567(fund_code)
		self.day_x_value = np.array(self.em.loadHistoryPlotFromLocal(src_dir)).astype(float)


	def getSampleNum(self, iDaysBefore):
		_, v = cal.extractDataFromDays(self.day_x_value, iDaysBefore)
		return len(v)


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
		c = len(np.where(cal.symbol(fChangeRate) * aDataSeries >= cal.symbol(fChangeRate) * fChangeRate)[0])
		r1 = c / len(aDataSeries)
		aDataHalf = aDataSeries[np.where(cal.symbol(fChangeRate) * aDataSeries >= 0)]
		c = len(np.where(cal.symbol(fChangeRate) * aDataHalf >= cal.symbol(fChangeRate) * fChangeRate)[0])
		r2 = c / len(aDataHalf)
		return r1, r2


	def getPredictByChangeRate(self, iDaysBefore, iDaysAfter, fChangeRate, pdtDays=3):
		aRateArray = 100 * self.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		_, aDataArray = cal.extractDataFromDays(self.day_x_value, iDaysBefore)
		# 比如我想查找-5.3%，实际查找的是(-5, -6)范围内的记录
		genRange = [int(fChangeRate), int(fChangeRate) + cal.symbol(fChangeRate) * 1]
		genRange.sort()
		idx_hit = np.where((aRateArray >= genRange[0]) & (aRateArray <= genRange[1]))[0]
		# 计算命中样本在样本空间中的占比
		iSampleNum = len(idx_hit)

		dResultList = {}
		for d in range(1, pdtDays+1):
			dResultList[d] = []
		# d1: [r1, r2, ...]
		# d2: [r1, r2, ...]
		for i in idx_hit:
			if i + pdtDays + iDaysAfter > len(aDataArray) - 1:
				continue
			fValue = aDataArray[i+iDaysAfter]
			for d in range(1, pdtDays+1):
				fValueOfNDaysAfter = aDataArray[i+iDaysAfter+d]
				fRate = 100 * (fValueOfNDaysAfter - fValue) / fValue
				dResultList[d].append(fRate)

		for d in dResultList.keys():
			ds = dResultList[d]
			dResultList[d] = [np.min(ds), np.max(ds), np.mean(ds)]

		return dResultList, iSampleNum

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