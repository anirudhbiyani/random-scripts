#!/bin/python

from __future__ import print_function
import argparse
import csv
import json


parser = argparse.ArgumentParser()
parser.add_argument("--report", help="path to CV report", required=True)
args = parser.parse_args()

# parse tab-delimited CV report
report = list(csv.reader(open(args.report, 'rb'), delimiter='\t'))

output = [{}]
x = 0
i = 3
while i < len(report):
    line = report[i]

    # skip blank lines
    if len(line[0]) == 0:
        pass

    # found new check header
    elif ' | ' in line[0]:
        # start new dict if check previously defined
        if 'id' in output[x]:
            x += 1
            output.append({})
        header = line[0].split(' ',2)
        output[x]['id'] = header[0]
        output[x]['description'] = header[2]

        keys = report[i+1]
        vals = report[i+2]
        for h in range(len(keys)):
            key = keys[h].lower().replace(' ','_')
            output[x][key] = vals[h]
        i += 2

    # parse assets
    else:
        status = '_'.join(line[0].split(' ')[0:1]).lower()
        output[x][status] = []
        keys = report[i+1]
        i += 2
        while i < len(report) and len(report[i][0]) != 0:
            asset = {}
            vals = report[i]
            for h in range(len(keys)):
                if len(keys[h]) == 0:
                    continue
                asset[keys[h]] = vals[h]
            i += 1
            output[x][status].append(asset)

    i += 1

print(json.dumps(output, indent=4))
