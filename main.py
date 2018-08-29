#/usr/bin/python3

import csv
import argparse
import re
from datetime import date

def importCsvData(filename, glcode):
    sales = {}
    jrnls = []
    try:
        with open(filename, 'rb') as f:
            for line in f:
                l = sanitizeDescription(line)
                line = l.split(',')
                # print(line[0][:4], glcode)
                if line[0][:4] == glcode:
                    dept_no = line[0][-2:]
                    batch_no = line[12][-3:]
                    idate = line[3]
                    amt = round(float(line[7]), 2)
                    entry_type = line[5]
                    # print(batch_no, idate, amt, entry_type)
                    if entry_type == 'SD':
                        jrnls.append(line)
                    else:
                        if dept_no not in sales:
                            sales[dept_no] = {batch_no: [idate, amt]}
                        elif batch_no not in sales[dept_no]:
                            sales[dept_no][batch_no] = [idate, amt]
                        else:
                            sales[dept_no][batch_no][1] += amt
        return [sales, jrnls]
    except Exception as e:
        print('Exception: {}'.format(str(e)))

def printReport(sales_data, lotto_data, report_name):
    sales = sales_data[0]
    jrnls = sales_data[1]
    lotto_sales = lotto_data[0]
    lotto_jrnl = lotto_data[1]
    # report_date = date.today()
    # date = report_date.strftime("%A %d. %B %Y")
    with open(report_name, 'w') as r:
        r.write('{:^80}\r\n'.format('101 Batch Report'))
        # r.write('{:^80}\r\n'.format(date))
        r.write('{}\r\n\r\n'.format('='*80))
        r.write('{:18}{:16}{:46}\r\n'.format('Jrnl', 'Date', 'Amount'))
        jrnl_total = 0
        sales_total = 0
        for j in jrnls:
            # print(j)
            r.write('{:18}{:16}{:46,.2f}\r\n'.format(j[4], j[3], float(j[7])))
            jrnl_total += float(j[7])
        r.write('{}\r\n'.format('='*80))
        r.write('{:80,.2f}\r\n\r\n'.format(jrnl_total))
        for d in sorted(sales):
            dept_sales_total = 0
            dept_lotto_total = 0
            dept_difference = 0
            r.write('Dept: {}\r\n'.format(d))
            r.write('{}\r\n'.format('='*80))
            r.write('{:10}{:16}{:>30}{:>12}{:>12}\r\n'.format('Batch No.', 'Date', 'Amount', 'Lotto', 'Difference'))
            # print(d)
            for s in sorted(sales[d]):
                batch_no = s
                idate = sales[d][s][0]
                sales_amt = sales[d][s][1]
                if d in lotto_sales and batch_no in lotto_sales[d]:
                    lotto_amt = lotto_sales[d][s][1]
                else:
                    lotto_amt = 0
                difference = sales_amt + lotto_amt
                r.write('{:10}{:16}{:30,.2f}{:12,.2f}{:12,.2f}\r\n'.format(batch_no, idate, sales_amt, lotto_amt, difference))
                dept_sales_total += sales_amt
                dept_lotto_total += lotto_amt
                dept_difference += difference
            sales_total += dept_sales_total
            r.write('{}\r\n'.format('='*80))
            r.write('{:56,.2f}{:12,.2f}{:12,.2f}\r\n\r\n'.format(dept_sales_total, dept_lotto_total, dept_difference))
        r.write('{}\r\n'.format('='*80))
        r.write('{:20}{:60,.2f}\r\n'.format('Sales Total', sales_total))
        r.write('{:20}{:60,.2f}\r\n'.format('Journal Total', jrnl_total))
        r.write('{:20}{:60,.2f}\r\n'.format('Difference', sales_total + jrnl_total))
    r.close()

def sanitizeDescription(line):
    # pattern = r'("[^",]+),([^",]+),([^"]+")' regex pattern to match commas
    pattern = r'("[^",]+),([^",]+),([^"]+")'
    new_line = re.sub(pattern, 'deleted', line)
    return new_line.replace('"', '').strip('\r\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import CSV data.")
    parser.add_argument('filename', help="Which file would you like to open")
    args = parser.parse_args()
    print(args.filename)
    data1010 = importCsvData(args.filename, '1010')
    data4608 = importCsvData('4608.csv', '4608')
    printReport(data1010, data4608, "101_Report.txt")
