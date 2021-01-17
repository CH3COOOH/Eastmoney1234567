# Reference
# https://blog.csdn.net/chaoren499/article/details/90232332
import requests
import re
import json

class EM1234567:
	def __init__(self, fund_code):
		self.fund_code = fund_code

	def __jsonLoad(self, sJson):
		return json.loads(re.match(".*?({.*}).*", sJson, re.S).group(1))

	def __getHistoryText(self):
		r = requests.get('https://fund.eastmoney.com/pingzhongdata/%s.js?v=20160518155842' % self.fund_code)
		return r.text

	def getRealtimeInfo(self):
		r = requests.get('https://fundgz.1234567.com.cn/js/%s.js?rt=1463558676006' % self.fund_code)
		return self.__jsonLoad(r.text)
		# *** keys ***
		# fundcode
		# name
		# jzrq (what date)
		# dwjz (dan wei jing zhi)
		# gsz (gu suan zhi)
		# gszzl (gu suan zeng zhang lv)
		# gztime (gu zhi time)

	def getHistoryRate(self):
		def _rateGen(pattern, fromText):
			_ = re.search(pattern, fromText)
			if _ == None:
				return -100
			return float(_.group().split('"')[1])
		r_text = self.__getHistoryText()
		rate_1y = _rateGen('syl_1n="(\S+)"', r_text)
		rate_6m = _rateGen('syl_6y="(\S+)"', r_text)
		rate_3m = _rateGen('syl_3y="(\S+)"', r_text)
		rate_1m = _rateGen('syl_1y="(\S+)"', r_text)
		return {'1m': rate_1m, '3m': rate_3m, '6m': rate_6m, '1y': rate_1y}

	def getHistoryPlotJson(self):
		t_points = re.search('Data_ACWorthTrend = \[\[.+?\]\];', self.__getHistoryText()).group()
		t_points = t_points.split(' = ')[1][:-1]
		return json.loads(t_points)


def test(fund_code):
	m = EM1234567(fund_code)
	realtime = m.getRealtimeInfo()
	hisory = m.getHistoryRate()
	print('NAME: %s' % realtime['name'])
	print('UPDATE: %s' % realtime['jzrq'])
	print('RATE (NOW): %s' % realtime['gszzl'])
	print('RATE (1M): %.2f' % hisory['1m'])
	print('RATE (3M): %.2f' % hisory['3m'])
	print('RATE (6M): %.2f' % hisory['6m'])
	print('RATE (1Y): %.2f' % hisory['1y'])

if __name__ == '__main__':
	import sys
	test(sys.argv[1])