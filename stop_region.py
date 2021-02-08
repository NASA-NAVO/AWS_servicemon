#!/bin/env python

import sys
import pprint
import boto3

from datetime import datetime
from botocore.exceptions import ClientError


class stop_region():

    # This code stops an instance build from the "NAVO" 
    # AMI on the named region.

    def __init__(self, region):

        pp = pprint.PrettyPrinter(indent=4)


        # Connect to Region

        region_client   = boto3.client  ('ec2', region_name=region)
        region_resource = boto3.resource('ec2', region_name=region)


        # Stop "NAVO"-named instances

        starttime = datetime.now()
        print(region + ': Start time: ' + str(starttime) + ' [stop_region]')

        response = region_client.describe_instances(
            Filters = [
                {
                    'Name': 'tag:Name',
                    'Values': ['NAVO']
                }
            ])

        reservations = response['Reservations']

        if len(reservations) == 0:
            print(region + ': No "NAVO" instances. [stop_region]')

        else:

            # Stop all the running instances that have the Name tag "NAVO"

            for reservation in reservations:

                instances = reservation['Instances']
                
                for instance in instances:

                    state = instance['State']['Name']

                    if state == 'stopped':
                        print(region + ': Instance ' + instance_id + ' is already running.')

                    elif state == 'running':

                        instance_id = instance['InstanceId']

                        instance_object = region_resource.Instance(instance_id)

                        response = region_client.stop_instances(
                            InstanceIds=[instance_id], DryRun=False)

                        instance_object.wait_until_stopped()

                        print(region + ': Instance ' + instance_id + ' stopped.')

                    else:
                        continue

            endtime = datetime.now()
            print(region + ': End time: ' + str(endtime) + ' [stop_region]')


def main():

    if len(sys.argv) < 2:
        print('Usage: stop_region.py <region_name>\n')
        sys.exit(0)
    else:
        stop_region(sys.argv[1])

if __name__ == "__main__":
    main()
