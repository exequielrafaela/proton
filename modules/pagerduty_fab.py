
from fabric.api import settings
from fabric.decorators import task
from termcolor import colored
import pygerduty
import sys
# import os.path

@task
def inc_report():
    """
 Usage: edit subdomain and specify an API key (must have full access) below.
 (What's the subdomain? Example: http://demo.pagerduty.com --> "demo")
 Then run: python incidents.py [start date: YYYY-MM-DD] [end date: YYYY-MM-DD]
 Example: python incidents.py 2015-01-01 2015-03-31
    """
    # global user_exists
    with settings(warn_only=False):

        try:
            pager = pygerduty.PagerDuty("btr-consulting", "tAA4wF6yrX1Xrd1nx1Js")
            startdate, enddate = sys.argv[1:]

            # This function escapes quotes in notes in a way that's Excel compatible.
            # All other characters, including comma and new-line, are handled correctly
            # by way of being included within the surrounding quotes.

            def escape(str):
                str = str.replace("\"", "\"\"")
                return str

            def change_text(text):
                return text.encode('utf-8')

            my_filename = sys.path[0] + "/incident_notes_%s_-_%s.csv" % (startdate, enddate)

            with open(my_filename, 'w', 1) as the_file:
                the_file.write("Incident ID,Description,Notes\n")
                for incident in pager.incidents.list(since=startdate, until=enddate):
                    if hasattr(incident.trigger_summary_data, 'subject'):
                        my_description = incident.trigger_summary_data.subject
                    elif hasattr(incident.trigger_summary_data, 'description'):
                        my_description = incident.trigger_summary_data.description
                    my_line = '%s,"%s","' % (incident.incident_number, escape(my_description))
                    my_count = 0
                    for note in incident.notes.list(incident_id=incident.incident_number):
                        my_count += 1
                        if my_count > 1:
                            my_line += "\n"
                        print note.content
                        my_line += "%s, %s: %s" % (
                        escape(note.user.name), escape(note.created_at), escape(note.content))
                    my_line += "\"\n"
                    the_file.write(my_line)

        except KeyError:
            print colored('################################', 'red')
            print colored('Pagerduty report fail', 'red')
            print colored('################################', 'red')