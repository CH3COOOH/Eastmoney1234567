import libLch as lch
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class Plotter:
	def __init__(self, fund_code):
		self.fund = lch.Fund(fund_code)

	def continualRateAndDays(self, iDays):
		# Code: crad
		r, d = self.fund.getContinualRateAndDays(iDays)
		print('%d %d' % (abs(int(r.max()-r.min())), abs(int(d.max()-d.min()))))
		plt.subplot(1, 2, 1)
		plt.hist(r * 100, bins=abs(int(100 * (r.max()-r.min()))), facecolor="blue", edgecolor="black", alpha=0.7)
		plt.xlabel("涨跌百分比 [%]")
		plt.ylabel("样本数")
		plt.title("基金[%s] 连续增长百分比" % self.fund.fund_code)
		plt.subplot(1, 2 ,2)
		plt.hist(d, bins=abs(int(d.max()-d.min())), facecolor="blue", edgecolor="black", alpha=0.7)
		plt.xlabel("连续增长天数")
		plt.ylabel("样本数")
		plt.title("基金[%s] 连续增长天数" % self.fund.fund_code)
		plt.show()

	def rateAfterDaysFromOneDay(self, iDaysBefore, iDaysAfter):
		# Code: radf
		r = self.fund.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		plt.hist(r * 100, bins=abs(int(100 * (r.max()-r.min()))), facecolor="blue", edgecolor="black", alpha=0.7)
		plt.xlabel("涨跌百分比 [%]")
		plt.ylabel("样本数")
		plt.title("基金[%s] 自买入起放置%d天" % (self.fund.fund_code, iDaysAfter))
		plt.show()


	def parameters(self, param):
		if param[0] == 'crad':
			self.continualRateAndDays(int(param[1]))
		elif param[0] == 'radf':
			self.rateAfterDaysFromOneDay(int(param[1]), int(param[2]))

if __name__ == '__main__':
	import sys
	ptr = Plotter(sys.argv[1])
	ptr.parameters(sys.argv[2:])