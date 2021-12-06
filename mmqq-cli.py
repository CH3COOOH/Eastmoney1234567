import os
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
PY_CMD = 'py'

if __name__ == '__main__':
	while True:
		print('''
====================================
     Make Money Quickly Quickly
            2021-02-25
------------------------------------
请选择功能
1. 用名称和近期涨跌更新基金代码xlsx
2. 用基金代码或xlsx更新本地数据集
3. 启动Monitor
4. 生成行情曲线墙
5. 启动LCH分析工具
====================================''')

		ch = input('> ')

		if ch == '1':
			ch = input('XLSX文件位置 是否抓取历史涨跌记录(0/1)\n> ')
			src, his = ch.split(' ')
			os.system(PY_CMD + ' make_sheet.py %s %s' % (src, his))


		elif ch == '2':
			todo = input('''
-f xlsx文件名 存储目录: 从xlsx文件定义的列表批量更新
-c 基金代码 存储目录: 用基金代码更新特定基金
> ''')
			p1, p2, p3 = todo.split(' ')
			os.system(PY_CMD + ' local-update.py %s %s %s' % (p1, p2, p3))

		elif ch == '3':
			todo = input('''
xlsx基金列表 更新周期(0=仅更新一次) 线程数
> ''')
			p1, p2, p3 = todo.split(' ')
			os.system(PY_CMD + ' monitor.py %s %s %s' % (p1, p2, p3))

		elif ch == '4':
			todo = input('''
xlsx文件名 回溯天数 区间峰值or最近极值(peak | nearest)
> ''')
			p1, p2, p3 = todo.split(' ')
			os.system(PY_CMD + ' k-wall.py %s %s %s' % (p1, p2, p3))

		elif ch == '5':
			todo = input('''
【LCH】 需要分析什么信息？
crad. 统计最大连续涨/跌百分比和天数
radf. 统计N天损益
 mtr. 统计基金任意一天投入N天后涨/跌超过R%的比率
> ''')
			if todo == 'crad':
				cd, p1 = input('基金代码 回溯天数 = ').split(' ')
				os.system(PY_CMD + ' helper.py %s %s %s' % (cd, todo, p1))
			elif todo == 'radf':
				cd, p1, p2 = input('基金代码 回溯天数 N = ').split(' ')
				os.system(PY_CMD + ' helper.py %s %s %s %s' % (cd, todo, p1, p2))
			elif todo == 'mtr':
				cd, p1, p2, p3 = input('基金代码 回溯天数 N R = ').split(' ')
				os.system(PY_CMD + ' helper.py %s %s %s %s %s' % (cd, todo, p1, p2, p3))
