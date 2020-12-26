# Eastmoney1234567

Make money, quickly quickly. Utilization of 1234567 fund APIs.

![Monitor](./monitor.JPG)

## Usage

 - Input fund code into a XLSX file and make a list with name and benefit rate in recent years (optional):
 `make_sheet <fund_list.xlsx> <ifGetRate, 0 or 1>`

 - Launch the monitor:
 `monitor <fund_list.xlsx> <delay> [threadNum]`


## For those who want to build a executable

 - If the exeutable made by pyInstaller shows the error "prettytable distribution was not found", copy hook-prettytable.py to the hook directory.

 - For Windows, the path maybe
 `...\Python36\Lib\site-packages\PyInstaller\hooks`