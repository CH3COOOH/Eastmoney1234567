import libLch as lch
import cal
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class Plotter:
	def __init__(self, fund_code, src_dir='local-data'):
		self.fund = lch.Fund(fund_code, src_dir)

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

	def rateAfterDaysFromOneDay(self, iDaysBefore, iDaysAfter, isGraph=False):
		# Code: radf
		r = self.fund.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		r *= 100
		r_mean = r.mean()

		print('\n从%d天前至今，基金[%s]在任意一天投入%d天后收益期望为%.2f%%\n最高收益为%.2f%%，最低为%.2f%%，风险收益比为%.2f' % (
			iDaysBefore,
			self.fund.fund_code,
			iDaysAfter,
			r_mean,
			r.max(),
			r.min(),
			r_mean / r.min()))

		if isGraph:
			color = lambda x: {-1: 'green', 1: 'red'}[x]
			plt.hist(r, bins=abs(int(r.max()-r.min())), facecolor="blue", edgecolor="black", alpha=0.7)
			plt.text(r_mean, 0, '%.2f%%' % r_mean,
					ha='right',
					c=color(cal.symbol(r_mean)),
					# zorder=3,
					bbox=dict(boxstyle="square",
						ec='grey',
						fc='white',
						alpha=.5
					))
			plt.xlabel("涨跌百分比 [%]")
			plt.ylabel("样本数")
			plt.title("基金[%s] 自买入起放置%d天" % (self.fund.fund_code, iDaysAfter))
			plt.show()

	def moreThanRate(self, iDaysBefore, iDaysAfter, fChangeRate):
		r = self.fund.getRateAfterDaysFromOneDay(iDaysBefore, iDaysAfter)
		r *= 100
		print('\n从%d天前至今，基金[%s]在任意一天投入%d天后涨/跌超过%.2f%%的比率为%.2f%%' % (
			iDaysBefore,
			self.fund.fund_code,
			iDaysAfter,
			fChangeRate,
			cal.getMoreThanRate(r, fChangeRate)))

	def parameters(self, param):
		if param[0] == 'crad':
			self.continualRateAndDays(int(param[1]))
		elif param[0] == 'radf':
			self.rateAfterDaysFromOneDay(int(param[1]), int(param[2]))
		elif param[0] == 'mtr':
			self.moreThanRate(int(param[1]), int(param[2]), float(param[3]))


if __name__ == '__main__':
	import sys
	ptr = Plotter(sys.argv[1])
	ptr.parameters(sys.argv[2:])