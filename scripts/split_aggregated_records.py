'''
将以下格式的培训记录表转化为多次记录
2017-2018学年新教师教学研习班 20学时
2017-2019学年新教师教学研习班 14学时
2017-2020学年新教师教学研习班 15学时
2017-2021学年新教师教学研习班 xx学时

=>

2017-2018学年新教师教学研习班(第一次)
2017-2018学年新教师教学研习班(第二次)
2017-2018学年新教师教学研习班(第三次)
'''
import sys

import xlrd
import xlwt


assert len(sys.argv) == 3
in_path, out_path = sys.argv[1:]
assert out_path.endswith('.xls')
sheet = xlrd.open_workbook(in_path).sheet_by_index(0)
num_rows = sheet.nrows
headers = sheet.row_values(0)
rounds = []
for row_idx in range(1, num_rows):
  row = sheet.row_values(row_idx)
  num_hours = int(row[9])
  total_events = num_hours // 2
  length = len(rounds)
  if length < total_events:
    rounds.extend([] for _ in range(total_events - length))
  for idx in range(total_events):
    rounds[idx].append(row)

program_category = '教学促进'
program_name = '新教师教学研习班'
event_time = '20180713'
role = '参与'
record_idx = 0
workbook = xlwt.Workbook()
sheet = workbook.add_sheet('原始')
ptr_r = 0

def write_row(sheet, ptr_r, row):
  for ptr_c in range(len(row)):
    sheet.write(ptr_r, ptr_c, row[ptr_c])


write_row(sheet, ptr_r, headers)
for idx, r in enumerate(rounds):
  event_name = f'2017-2018学年新教师教学研习班（第{idx+1}期)'
  for record in r:
    department_name, user_name, username = record[5:8]
    row = (record_idx, event_name, program_category, program_name,
           event_time, department_name, user_name, username, role,
           2, 1, 1)
    ptr_r += 1
    write_row(sheet, ptr_r, row)
    record_idx += 1

workbook.save(out_path)