#!/usr/bin/env python
""" Plot CSV columns as Lines in a chart.
"""

import argparse
import sys
try:
    import pygal
except:
    print('Error:')
    print(' => please install pygal in order to make plots: pip install pygal')
    sys.exit(1)


def print_columns(filename):
    with open(filename, 'r') as csv:
        header_txt = csv.readline()[:-1]
        headers = header_txt.split(';')
        print('{} column names are: \n\t{}'.format(args.file, str(headers)))


def csv_column(filename, column_name, convert=lambda x: x):
    column = []
    with open(filename, 'r') as csv:
        headers = csv.readline()[:-1].split(';')
        idx = headers.index(column_name)
        for line in csv.readlines():
            splitted = line.split(';')
            column.append(convert(splitted[idx]))
    return column


def extract_column_expression(column_expression):
    # column description can contain expressions on what to do with the column
    # for example blah//1000 would do the division of blah before returning it
    # currently: only division by a constant is supported:
    # column_name//constant or column_name
    if '//' in column_expression:
        expr_spl = column_expression.split('//')
        column_name = expr_spl[0]
        divisor = float(expr_spl[1])
        return column_name, lambda x: float(x)/divisor
    else:
        return column_expression, lambda x: float(x)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=globals()['__doc__'], add_help=True)
    parser.add_argument('--columns', required=True, nargs='+', dest='columns',
                        help="Columns to plot, in the form file$column eg: CPU_ALL.csv$User%%")
    parser.add_argument('--only-print-cols', action='store_true', default=False, dest='print_cols')

    args = parser.parse_args()
    column_names = args.columns

    print(">>>> columns: {}".format(column_names))

    if args.print_cols:
        print_columns(args.file)
        print('Exit.')
        sys.exit(0)

    columns = []  # list in the form: [('column_name', [val1, val2, ....], ...)]
    for column in column_names:
        column_file, column_expression = column.split('$')
        column_name, conversion_fun = extract_column_expression(column_expression)
        column = csv_column(column_file, column_name, convert=conversion_fun)
        print('*********************************************Extracted column')
        print(column_name, ' => ', column)
        print('*************************************************************')
        columns.append((column_name, column_expression, column))

    config = pygal.Config()
    config.legend_at_bottom = True
    # config.logarithmic = True
    config.y_labels = [5, 15, 30, 60, 90, 100]
    line_chart = pygal.Line(config)
    line_chart.title = str(column_names)
    # line_chart.x_labels = map(str, range(2002, 2013))
    for column_name, column_expression, values in columns:
        line_chart.add(column_expression, values)
    line_chart.render_to_file('chart.svg')
