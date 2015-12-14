#!/usr/bin/env python
""" parse an NMON file. Ouput one .csv file per measurement type (CPU_ALL, MEM...)
"""

import argparse
from datetime import datetime
from os import path
import re
import sys
import os
import errno

SEPARATOR = ','
NEWLINE = '\n'
EPOCH = datetime(1970, 1, 1)

ticks = {}  # dict in the form {'TIMENAME': timestamp}
measurements_definitions = {}  # dict in the form {'measurement': [column1, column2, ....]}
out_files = {}  # dict in the form: {'measurement', open('measurement.csv', 'w')}
is_measurement_pattern = re.compile("^.*,(T[0-9]+),")  # ex: CPU_ALL,T0001,0.1,0.3,0.1,99.5,,24
global nmon_file
nmon_file = None


def to_epoch_secs(datetime_ts):
    return (datetime_ts - EPOCH).total_seconds()


def is_tick_definition(line):
    return line.startswith('ZZZZ,')


def is_defined_measurement(name):
    return name in measurements_definitions


def parse_measurement_definition(line):
    # measurement definition are in the form "name: columns" for example:
    # CPU_ALL,CPU Total dev-res-node-05,User%,Sys%,Wait%,Idle%,Busy,CPUs
    # which is:
    # measurement name, description, column1, column2...
    splitted = line.split(SEPARATOR)
    return splitted[0], splitted[2:]


def parse_tick_definition(line):
    # ticks are in the form: ZZZZ,T0252,16:59:52,04-DEC-2015
    splitted = line.split(SEPARATOR)
    name = splitted[1]
    timestamp = datetime.strptime(splitted[3] + " " + splitted[2], "%d-%b-%Y %H:%M:%S")
    return name, timestamp


def handle_measurement(line):
    # measurements are in the form: CPU_ALL,T0001,0.1,0.3,0.1,99.5,,24
    splitted = line.split(SEPARATOR)
    measurement_type = splitted[0]
    measurement_definition = measurements_definitions[measurement_type]
    timestamp = ticks[splitted[1]]
    values = splitted[2:]
    return measurement_type, timestamp, values


def is_measurement(line):
    return is_measurement_pattern.match(line) is not None


def get_file(measurement_type):
    measurement_file = out_files.get(measurement_type, None)
    if not measurement_file:
        global nmon_file
        measurement_file = open(nmon_file+'.'+measurement_type+'.csv', 'w')
        measurement_columns = measurements_definitions[measurement_type]
        measurement_file.write('timestamp;'+';'.join(measurement_columns)+NEWLINE)
        out_files[measurement_type] = measurement_file
    return measurement_file


def write_measurement(measurement_type, timestamp, values):
    measurement_file = get_file(measurement_type)
    ts_secs = str(int(to_epoch_secs(timestamp)))
    values_csv = ';'.join(values)
    measurement_file.write(ts_secs+';'+values_csv+NEWLINE)


def handle_line(line):
    if is_tick_definition(line):
        name, timestamp = parse_tick_definition(line)
        ticks[name] = timestamp
        return

    if line.startswith(measurements_COMMA):
        # measurements are either definitions or ocurrences:
        # definition of CPU_ALL: CPU_ALL,CPU Total dev-res-node-05,User%,Sys%,Wait%,Idle%,Busy,CPUs
        # ocurrence of CPU_ALL:  CPU_ALL,T0001,0.1,0.3,0.1,99.5,,24
        if is_measurement(line):
            measurement_type, timestamp, values = handle_measurement(line)
            write_measurement(measurement_type, timestamp, values)
            return
        name, columns = parse_measurement_definition(line)
        measurements_definitions[name] = columns


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=globals()['__doc__'], add_help=True)
    parser.add_argument('file', help='NMON file to be parsed')
    parser.add_argument('--out-dir', default='./', dest='out_dir',
                        help='Directory to store .csv files in.')

    args = parser.parse_args()

    line_count = 0
    measurements = ('CPU_ALL', 'MEM', 'NET', 'PROC', 'NETPACKET', 'DISKBUSY',
                    'DISKREAD', 'DISKWRITE', 'DISKXFER', 'DISKBSIZE')
    measurements_COMMA = tuple((m+SEPARATOR for m in measurements))

    measurements = tuple(measurements)

    nmon_file = args.file
    with open(nmon_file, 'r') as f:
        mkdir_p(args.out_dir)
        os.chdir(args.out_dir)
        for line in f.readlines():
            line_count += 1
            handle_line(line[:-1])  # rm \n from line
