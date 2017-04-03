#!/usr/bin/env python

import requests
import sys
import json
from datetime import date, timedelta

# Your PagerDuty API key.  A read-only key will work for this.
AUTH_TOKEN = 'key'
# The API base url, make sure to include the subdomain
BASE_URL = 'https://subdomain.pagerduty.com/api/v1'
# The service ID that you would like to query.  You can leave this blank to query all services.
service_id = ""
# The start date that you would like to search.  It's currently setup to start yesterday.
# yesterday = date.today() - timedelta(1)
since = '2017-03-20'
# The end date that you would like to search.
until = '2017-03-26'

HEADERS = {
    'Authorization': 'Token token={0}'.format(AUTH_TOKEN),
    'Content-type': 'application/json',
}


def get_incident_count(since, until, service_id=None):
    global incident_count

    params = {
        'service': service_id,
        'since': since,
        'until': until
    }
    print '{0}/incidents/count'.format(BASE_URL)
    count = requests.get(
        '{0}/incidents/count'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )
    incident_count = count.json()['total']


def get_incidents(since, until, offset, service_id=None):
    print "offset:" + str(offset)
    file_name = 'pagerduty_export'
    output = ""

    params = {
        'service': service_id,
        'since': since,
        'until': until,
        'offset': offset
    }

    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )

    for incident in all_incidents.json()['incidents']:
        get_incident_details(incident["id"], str(incident["incident_number"]), incident["service"]["name"],
                             file_name + since + ".csv")


def get_incident_details(incident_id, incident_number, service, file_name):
    start_time = ""
    end_time = ""
    summary = ""
    has_details = False
    has_summary = False
    has_body = False
    output = incident_number + "," + service + ","

    f = open(file_name, 'a')

    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries?include[]=channel'.format(BASE_URL, incident_id),
        headers=HEADERS
    )

    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger":
            if log_entry["created_at"] > start_time:
                start_time = log_entry["created_at"]
                if ("summary" in log_entry["channel"]):
                    has_summary = True
                    summary = log_entry["channel"]["summary"]
                if ("details" in log_entry["channel"]):
                    has_details = True
                    details = log_entry["channel"]["details"]
                if ("body" in log_entry["channel"]):
                    has_body = True
                    body = log_entry["channel"]["body"]
        elif log_entry["type"] == "resolve":
            end_time = log_entry["created_at"]

    output += start_time + ","
    output += end_time
    if (has_summary):
        output += ",\"" + summary + "\""
    if (has_details):
        output += ",\"" + str(details) + "\""
    if (has_body):
        output += ",\"" + str(body) + "\""
    output += "\n"
    f.write(output)


def get_incident_stats(since, until, service_id=None):
    get_incident_count(since, until, service_id)
    print "Number of incidents: ", incident_count
    for offset in xrange(0, incident_count):
        if offset % 100 == 0:
            get_incidents(since, until, offset, service_id)
    print "Exporting has completed successfully."


def main(argv=None):
    if argv is None:
        argv = sys.argv
    get_incident_stats(since, until, "")


if __name__ == '__main__':
    sys.exit(main())