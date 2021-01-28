import numpy as np

def extractDataFromDays(mData_DayxValue, iDaysBefore):
	mData_DayxValue = np.array(mData_DayxValue)
	if iDaysBefore < mData_DayxValue.shape[0]:
		return np.array(list(range(0, iDaysBefore))), mData_DayxValue[-iDaysBefore:, 1]
	else:
		return np.array(list(range(0, mData_DayxValue.shape[0]))), mData_DayxValue[:, 1]

