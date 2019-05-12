import re

import xlrd
import xlwt


pat = re.compile(r'(.*?)(校级|市级|省级|国家级)(.*?奖)')
fpath = '~/Desktop/TMSFTT/2018年教学竞赛获奖情况.xls'

workbook = xlrd.open_workbook(fpath)
sheet = workbook.sheet_by_index(0)
num_rows = sheet.nrows
awards = {}
for row in (sheet.row_values(i) for i in range(1, num_rows)):
    department_name, teacher_name, program = row[1:4]
    res = pat.search(program)
    if res is None:
        raise Exception()
    else:
        program, category, level = res.groups()
    key = (department_name, teacher_name)
    awards.setdefault(key, [])
    print(program, category, level)
    awards[key].append((program, category, level))

fpath = '~/Desktop/TMSFTT/2018年教师发展工作量-全-0316-工号.xls'

workbook = xlrd.open_workbook(fpath)
sheet = workbook.sheet_by_index(0)
num_rows = sheet.nrows
records = []
cnt = 0
headers = sheet.row_values(0)
for record in (sheet.row_values(i) for i in range(1, num_rows)):
    program, department_name, teacher_name = record[1:4]
    if program == '校青年教师讲课竞赛':
        program = '大连理工大学青年教师讲课竞赛'
    key = (department_name, teacher_name)
    if key in awards:
        for item in awards[key]:
            if item[0].startswith(program):
                cnt += 1
                program = '|'.join(item)
                record[1] = program
                awards[key].remove(item)
                break
    records.append(record)


fpath = '/Users/youchen/Desktop/TMSFTT/2018年教师发展工作量-全-0316-工号-获奖情况.xls'
workbook = xlwt.Workbook()
worksheet = workbook.add_sheet('原始')
for col, header in enumerate(headers):
    worksheet.write(0, col, header)
for row, record in enumerate(records, 1):
    for col, val in enumerate(record):
        worksheet.write(row, col, val)
workbook.save(fpath)
