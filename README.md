# Monitoring Agents Setup

Work in progress

Time: 40.32h

## [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) is the open source server agent to help you collect metrics from your stacks, sensors and systems. (c)
pros:
- secure by default

cons:
- require setup (there are few way to automate it, from influxdb templates up to ansible role in this repo)
- require monitoring setup like TICK or prometheus + grafana

## [Netdata](https://www.netdata.cloud/agent/) is the one agent for bare metal, VMs, edge devices, and anything in between. (c)

pros:
- automatic setup out of the box (but still require addition one for most of all cases)
- have clustering, monitoring and dashboards out of the box, + can export metrics into other monitoring solutions

cons:
- require some security configuration because of rich api (this repo contain configs with some of it)
