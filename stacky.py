import os
import re
import requests
import sys
import time

import prettytable as pt


STACKTACH = os.environ['STACKTACH_URL']


def _check(response):
    if response.status_code == 200:
        return response

    print "Error fetching results (%d)" % response.status_code
    x = response.text
    search = re.search('<title>(.*)</title>', x, re.IGNORECASE)
    if search:
        print "Server reported:", search.group(1)
    sys.exit(response.status_code)


def get_event_names():
    r = _check(requests.get(STACKTACH + "/stacky/events"))
    return r.json


def get_host_names():
    r = _check(requests.get(STACKTACH + "/stacky/hosts"))
    return r.json


def get_deployments():
    r = _check(requests.get(STACKTACH + "/stacky/deployments"))
    return r.json


def show_timings_for_uuid(uuid):
    pass


def related_to_uuid(uuid):
    params = {'uuid' : uuid}
    r = _check(requests.get(STACKTACH + "/stacky/uuid", params=params))
    return r.json


if len(sys.argv) == 1:
    print """Usage: stacky <command>
deployments - list stacktach deployments
events      - list of unique event names
watch       - 'watch <deployment id> <event-name> <polling sec>'
               deployment id 0 = all
               event-name empty = all
               polling = 2s
show    - inspect event ####
uuid    - inspect events with uuid xxxxx
summary - show summarized timings for all events
timings - show timings for <event-name> (no .start/.end)
request - show events with <request id>
kpi     - crunch KPI's
hosts   - list all host names"""
    sys.exit(0)

def dump_results(results):
    title = results.pop(0)
    if not results:
        print "No results"
        return

    t = pt.PrettyTable(title)
    for x in results:
        t.add_row(x)
    print str(t)


cmd = sys.argv[1]
if cmd == 'deployments':
    dump_results(get_deployments())

if cmd == 'events':
    dump_results(get_event_names())

if cmd == 'hosts':
    dump_results(get_host_names())

if cmd == 'uuid':
    uuid = sys.argv[2]
    print "Events related to", uuid
    dump_results(related_to_uuid(uuid))
    dump_results(show_timings_for_uuid(uuid))

if cmd == 'timings':
    name = sys.argv[2]
    r = _check(requests.get(STACKTACH + "/stacky/timings/%s" % name))
    dump_results(r.json)

if cmd == 'summary':
    r = _check(requests.get(STACKTACH + "/stacky/summary/"))
    dump_results(r.json)

if cmd == 'request':
    request_id = sys.argv[2]
    params = {'request_id': request_id}
    r = _check(requests.get(STACKTACH + "/stacky/request", params=params))
    dump_results(r.json)

if cmd == 'show':
    event_id = sys.argv[2]
    results = _check(requests.get(STACKTACH + "/stacky/show/%s" % event_id))
    results = results.json
    if len(results) == 0:
        print "Event %d not found" % event_id
        sys.exit(0)

    key_values = results.pop(0)
    data, uuid = results
    dump_results(key_values)
    if uuid:
        dump_results(related_to_uuid(uuid))

if cmd == 'watch':
    event_name = ""
    deployment = None
    poll = 2  # seconds

    if len(sys.argv) > 2:
        deployment_id = int(sys.argv[2])
        print "Deployment id:", deployment_id
    else:
        print "All Deployments"

    if len(sys.argv) > 3:
        event_name = sys.argv[3]
        print "Event name:", event_name
    if len(sys.argv) > 4:
        poll = int(sys.argv[4])
    print "Polling every %d seconds" % poll

    last_poll = None
    row = 0
    while 1:
        time.sleep(poll)


if cmd == 'kpi':
    r = _check(requests.get(STACKTACH + "/stacky/kpi"))
    dump_results(r.json)