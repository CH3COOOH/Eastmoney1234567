#  -*- coding: utf-8 -*-
# https://www.cnblogs.com/easypython/p/9084426.html
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)


# import gevent
# from gevent import monkey
# from gevent import pool

# monkey.patch_all()

import threading

from em1234567 import EM1234567
import openpyxl
import prettytable as pt
import os
from math import ceil
from time import sleep


class ListContainer:
	def __init__(self):
		self.container = []

	def insert(self, x):
		self.container.append(x)

	def get(self):
		return self.container


class RealtimeEvaluate:
	def __init__(self, fname, threadNum=20, logPath=None):
		wb = openpyxl.load_workbook(fname)
		sh = wb['INFO']
		self.codes = list(map(lambda x: x.value, sh['A']))
		self.names = list(map(lambda x: x.value, sh['B']))
		self.threadNum = threadNum
		self.logPath = logPath

	def __colorByRate(self, rate):
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

		def _getRealtimeInfoFromCodeList(cl, container):
			for c in cl:
				container.insert(_getRealtimeInfo(c))
			return 0

		def _chunks(arr, m):
			n = int(ceil(len(arr) / float(m)))
			return [arr[i:i + n] for i in range(0, len(arr), n)]

		rates_raw = ListContainer()
		code_groups = _chunks(self.codes, self.threadNum)
		task_list = []

		for cg in code_groups:
			task = threading.Thread(target=_getRealtimeInfoFromCodeList, args=(cg, rates_raw, ))
			task_list.append(task)
			task.start()

		for t in task_list:
			t.join()

		json_list = rates_raw.get()

		display_codes = []
		display_names = []
		display_rates = []

		for j in json_list:
			try:
				if j is not None:
					display_codes.append(j['fundcode'])
					display_names.append(j['name'])
					if self.logPath == None:
						display_rates.append(self.__colorByRate(j['gszzl']))
					else:
						display_rates.append(i['gszzl'])
				else:
					display_codes.append('--')
					display_names.append('--')
					display_rates.append('--')
			except:
				display_codes.append('ERR')
				display_names.append('ERR')
				display_rates.append('ERR')

		tb = pt.PrettyTable()
		tb.add_column('代码', display_codes)
		tb.add_column('名称', display_names)
		tb.add_column('实时', display_rates)

		if self.logPath == None:
			self.__clear()
			print(tb)
		else:
			print('Running as daemon...')
			html = '''
<html>
<head>
	<title>henChat</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<pre style="word-wrap: break-word; white-space: pre-wrap;">
%s
</pre>
</body>
</html>

			''' % tb.get_string()
			with open(self.logPath, 'w') as o:
				o.write(html)

	def cycleUpdate(self, delay):
		while True:
			self.update()
			self.__timenow()
			if delay <= 0 or self.logPath == None:
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
		print('Log mode supports one-time update only. Please write it into crontab.')
		exit(0)
	rev.cycleUpdate(int(sys.argv[2]))


