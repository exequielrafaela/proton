# aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=matias.desanti
# > /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-events.json

# aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=AuthorizeSecurityGroupIngress
# > /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-event-by-event

# $ aws cloudtrail lookup-events --start-time 2017-03-08T20:40:00.000Z --end-time 2017-03-08T21:20:00.000Z
# --lookup-attributes AttributeKey=EventName,AttributeValue=AuthorizeSecurityGroupIngress
# > /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-event-by-event-with-time.json

# aws ec2 describe-instances > /home/delivery/Programming/proton/conf/AWS/ec2-instance-details.json


import os
import pwd
from fabric.api import settings, env, sudo, local
# from fabric.contrib.files import exists, append
from fabric.decorators import task
# from fabric.tasks import Task
from termcolor import colored
import json

@task
def sec_grup_per_ec2(sgid='sg-'):
    """
Method to obaint all de EC2s associated to a certain AWS Security Group
Remember that this task it's intended to be run with role "local"
    :param sgid: AWS security group ID
    """
    # global user_exists
    with settings(warn_only=False):

        try:
            with open('./conf/AWS/ec2-instance-details.json') as json_data:
                json_raw = json.load(json_data)
                # print(json_raw)

                #for key, value in json_raw.items():
                    #print key, value

                print json_raw["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]
                print json_raw["Reservations"][0]["Instances"][0]["SecurityGroups"][1]["GroupId"]

                print json_raw["Reservations"][1]["Instances"][0]["SecurityGroups"][0]["GroupId"]
                # print json_raw["Reservations"][1]["Instances"][0]["SecurityGroups"][1]["GroupId"] => Since this
                # has only 1 Sec group then this line will result in "IndexError: list index out of range"

                # sg_item = [item for item in json_raw["Reservations"]
                            # if item["Instances"][0]["SecurityGroups"][0]["GroupId"] == sgid]

                # print sg_item

        except KeyError:
            print colored('################################', 'red')
            print colored('User ' + sgid + 'does not exists', 'red')
            print colored('################################', 'red')
