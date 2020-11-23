# https://www.cnblogs.com/easypython/p/9084426.html

from em1234567 import EM1234567
import openpyxl
import prettytable as pt
import os
from time import sleep

class RealtimeEvaluate:
	def __init__(self, fname):
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		
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

	def update(self):
		rates = []
		for c in self.codes:
			em = EM1234567(c)
			try:
				realtime = em.getRealtimeInfo()
				rates.append(self.__colorByRate(realtime['gszzl']))
			except:
				rates.append('--')
		tb = pt.PrettyTable()
		tb.add_column('CODE', self.codes)
		tb.add_column('NAME', self.names)
		tb.add_column('RATE', rates)
		self.__clear()
		print(tb)

	def cycleUpdate(self, delay):
		while True:
			self.update()
			self.__timenow()
			sleep(delay)
			print('Updating...')

if __name__ == '__main__':
	import sys
	rev = RealtimeEvaluate(sys.argv[1])
	rev.cycleUpdate(30)
	
