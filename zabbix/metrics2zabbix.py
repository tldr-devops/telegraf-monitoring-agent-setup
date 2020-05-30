#!/usr/bin/env python

# Script for parsing prometheus metrics format and send it into zabbix server
# MIT License
# https://github.com/Friz-zy/telegraf-monitoring-agent-setup

import re
import os
import sys
import time
import json
import socket
import optparse
try:
    from urllib.request import urlopen
except:
    from urllib import urlopen


def parse(source='http://127.0.0.1:9273/metrics'):
    # https://prometheus.io/docs/practices/naming/
    # https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels
    regex = re.compile(r'^(?P<metric>[a-zA-Z_:][a-zA-Z0-9_:]*)(?P<labels>{.*})?\s+(?P<value>.+)(\s+(?P<timestamp>\w+))?$')
    help_line = ''
    type_line = ''
    metrics = []

    text = urlopen(source).read()

    for line in text.splitlines():
        line = line.decode("utf-8")

        if line[0:6] == '# HELP':
            help_line = line
            continue
        elif line[0:6] == '# TYPE':
            type_line = line
            continue
        elif line[0] == '#':
            continue

        metric = regex.match(line).groupdict()
        metric['line_raw'] = line
        metric['help'] = help_line
        metric['type'] = type_line
        metric['source'] = source
        metrics.append(metric)

    return metrics

def main():
    parser = optparse.OptionParser()
    source = 'http://127.0.0.1:9273/metrics'
    destination = '/tmp/prom2zabbix'
    parser.set_defaults(source=source,
                        destination=destination,
                        hostname='')
    parser.add_option("-s", "--source", dest="source",
                    help="Prometheus source, default is " + source)
    parser.add_option("-d", "--destination", dest="destination",
                    help="Output .keys and .metrics files pattern, default is " + destination)
    (options, args) = parser.parse_args()

    seconds = int(time.time())
    metrics = parse(options.source)

    data = {"data": []}
    with open(options.destination + '.metrics', 'w') as f:
        for metric in metrics:
            if not metric['timestamp']:
                metric['timestamp'] = seconds
            if not metric['labels']:
                metric['labels'] = '{}'
            else:
                metric['labels'] = metric['labels'].replace(',', ';')

            # hacks
            if metric['metric'] == 'procstat_created_at':
                metric['value'] = metric['value'].replace('e+18', 'e+09')

            m = {}
            for k, v in metric.items():
                m["{#%s}" % k.upper()] = v
            data["data"].append(m)
            # https://www.zabbix.com/documentation/3.0/manpages/zabbix_sender
            escaped_labels = metric['labels'].replace('\\', '\\\\').replace('"', '\\"')
            f.write('- "telegraf[%s,%s]" %s %s\n' % (
                metric['metric'],
                escaped_labels,
                metric['timestamp'],
                metric['value']))

    data = json.dumps(data)
    escaped_data = data.replace('\\', '\\\\').replace('"', '\\"')
    with open(options.destination + '.keys', 'w') as f:
        f.write('- telegraf[keys] %s "%s"\n' % (
            seconds,
            escaped_data))

    # print(data)

if __name__ == "__main__":
    main()
