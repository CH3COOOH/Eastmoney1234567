import numpy as np

def extractDataFromDays(mData_DayxValue, iDaysBefore):
	mData_DayxValue = np.array(mData_DayxValue)
	if iDaysBefore < mData_DayxValue.shape[0]:
		return np.array(list(range(0, iDaysBefore))), mData_DayxValue[-iDaysBefore:, 1]
	else:
		return np.array(list(range(0, mData_DayxValue.shape[0]))), mData_DayxValue[:, 1]

def symbol(x):
	# 符号函数
	if x >= 0:
		return 1
	else:
		return -1

def getPeakAndDropRate(aDataSeries):
	y_now = aDataSeries[-1]
	y_max = np.max(aDataSeries)
	idx_peak = np.where(aDataSeries==y_max)
	rate = (y_now - y_max) / y_max * 100
	return y_now, y_max, idx_peak, rate

def getHowMuchChangedFromPreviousPeakOrValley(aDataSeries, iStartPoint=-1):
	# 用于计算自上个峰/谷至当前的连续涨/跌百分比
	# 默认从最新数据（即列表最后一个点）开始向前查找
	
	# 确定是在找Peak还是Valley
	iStart = len(aDataSeries) + iStartPoint
	i = iStart
	isFindingPeak = symbol(aDataSeries[i-1] - aDataSeries[i])

	if isFindingPeak == 1:
		while (aDataSeries[i-1] - aDataSeries[i] >= 0) and (i >= 1):
			i -= 1
	else:
		while (aDataSeries[i-1] - aDataSeries[i] <= 0) and (i >= 1):
			i -= 1
	fValueOfFound = aDataSeries[i]
	fDelta = aDataSeries[iStart] - fValueOfFound
	fRate = fDelta / fValueOfFound
	return i, fRate * 100

def main():
	a = [1,2,3,4,5,4,3,8,9,6,15,10,9]
	i, r = getHowMuchChangedFromPreviousPeakOrValley(a)
	print('%.2f, %.4f' % (i, r))

if __name__ == '__main__':
	main()