# https://www.cnblogs.com/easypython/p/9084426.html

import gevent
from gevent import monkey
from gevent import pool

monkey.patch_all()
from em1234567 import EM1234567
import openpyxl
import prettytable as pt
import os
from time import sleep

class RealtimeEvaluate:
	def __init__(self, fname, threadNum=20, logPath=None):
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		self.threadNum = threadNum
		self.logPath = logPath

	def __colorByRate(self, rate):
#		if os.name == 'nt':
#			return rate
		if float(rate) > 0.:
			return '\033[31m'+rate+'\033[0m'
		else:
			return '\033[32m'+rate+'\033[0m'

	def __clear(self):
		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')

	def __timenow(self):
		if os.name == 'nt':
			os.system('date /t')
		else:
			os.system('date')
			if self.logPath != None:
				os.system('echo $(date) >> ' + self.logPath)

	def update(self):

		def _getRealtimeInfo(c):
			try:
				em = EM1234567(c)
				return em.getRealtimeInfo()
			except:
				return None

		rates = []
		rate_pool = pool.Pool(self.threadNum)
		ob_pool = []
		for c in self.codes:
			ob = rate_pool.spawn(_getRealtimeInfo, c)
			ob_pool.append(ob)
		# rate_pool.join()
		gevent.joinall(ob_pool)
		for i in ob_pool:
			try:
				if i.value is not None:
					if self.logPath == None:
						rates.append(self.__colorByRate(i.value['gszzl']))
					else:
						rates.append(i.value['gszzl'])
				else:
					rates.append('--')
			except:
				rates.append("--")
		tb = pt.PrettyTable()
		tb.add_column('代码', self.codes)
		tb.add_column('名称', self.names)
		tb.add_column('实时', rates)
		self.__clear()
		print(tb)
		if self.logPath != None:
			with open(self.logPath, 'w') as o:
				o.write(tb.get_string())

	def cycleUpdate(self, delay):
		while True:
			self.update()
			self.__timenow()
			if delay <= 0:
				break
			sleep(delay)
			print('Updating...')

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 3:
		rev = RealtimeEvaluate(sys.argv[1])
	elif len(sys.argv) == 4:
		rev = RealtimeEvaluate(sys.argv[1], int(sys.argv[3]))
	elif len(sys.argv) == 5:
		rev = RealtimeEvaluate(sys.argv[1], int(sys.argv[3]), sys.argv[4])
	else:
		print('Usage: ./monitor <fund_list.xlsx> <delay> [threadNum] [logPath]')
		print('if delay == 0 => Update only once')
		exit(0)
	rev.cycleUpdate(int(sys.argv[2]))
