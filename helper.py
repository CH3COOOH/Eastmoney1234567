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

		ar, ad = cal.getAveRaiseAndDrop(r)
		print('增长平均=%.2f%%，回撤平均=%.2f%%' % (ar, ad))

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
		r_all, r_half = self.fund.getMoreThanRate(iDaysBefore, iDaysAfter, fChangeRate)
		r_all *= 100
		r_half *= 100
		print('\n从%d天前至今，基金[%s]在任意一天投入%d天后%s超过%.2f%%的比率为%.2f%%' % (
			iDaysBefore,
			self.fund.fund_code,
			iDaysAfter,
			{-1: '跌', 1: '涨'}[cal.symbol(fChangeRate)],
			fChangeRate,
			r_all))
		print('如果只考虑%s，则该比例为%.2f%%' % (
			{-1: '跌', 1: '涨'}[cal.symbol(fChangeRate)],
			r_half))

	def predictByChangeRate(self, iDaysBefore, iDaysAfter, fChangeRate, pdtDays):
		print('\n从%d天前至今，基金[%s]在%d天内%s%.2f%%(左右)的' % (
			iDaysBefore,
			self.fund.fund_code,
			iDaysAfter,
			{-1: '下跌', 1: '上涨'}[cal.symbol(fChangeRate)],
			fChangeRate))
		
		dPredict, iSampleNum = self.fund.getPredictByChangeRate(iDaysBefore, iDaysAfter, fChangeRate, pdtDays)
		for d in dPredict.keys():
			print('  %d天后：%.2f%% (最差), %.2f%% (最佳), %.2f%%(均值)' % (
				d,
				dPredict[d][0],
				dPredict[d][1],
				dPredict[d][2]))
		print('* 样本数%d, 占比%.2f%%' % (iSampleNum, 100 * iSampleNum / self.fund.getSampleNum(iDaysBefore)))


	def parameters(self, param):
		if param[0] == 'crad':
			self.continualRateAndDays(int(param[1]))
		elif param[0] == 'radf':
			self.rateAfterDaysFromOneDay(int(param[1]), int(param[2]))
		elif param[0] == 'mtr':
			self.moreThanRate(int(param[1]), int(param[2]), float(param[3]))
		elif param[0] == 'pbcr':
			self.predictByChangeRate(int(param[1]), int(param[2]), float(param[3]), int(param[4]))

if __name__ == '__main__':
	import sys
	ptr = Plotter(sys.argv[1])
	ptr.parameters(sys.argv[2:])