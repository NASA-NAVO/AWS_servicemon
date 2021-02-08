#!/bin/env python

import sys
import time
import pprint
import boto3

from datetime import datetime
from botocore.exceptions import ClientError

class start_region():

    # This code starts instances named "NAVO" on the named region.

    def __init__(self, region):

        pp = pprint.PrettyPrinter(indent=4)


        # Connect to Region

        region_client   = boto3.client  ('ec2', region_name=region)
        region_resource = boto3.resource('ec2', region_name=region)


        # Start "NAVO"-named instances

        response = region_client.describe_instances(
            Filters = [
                {
                    'Name': 'tag:Name',
                    'Values': ['NAVO']
                }
            ])

        reservations = response['Reservations']

        if len(reservations) == 0:
            print(region + ': No "NAVO" instances [start_region].')

        else:

            # Start all the stopped (and non-terminated) instances
            # that have the Name tag "NAVO"

            starttime = datetime.now()
            print('\n' + region + ': Start time: ' + str(starttime) + ' [start_region]')

            for reservation in reservations:

                instances = reservation['Instances']
                
                for instance in instances:

                    instance_id = instance['InstanceId']

                    instance_object = region_resource.Instance(instance_id)

                    state = instance['State']['Name']

                    if state == 'stopped':
                        response = region_client.start_instances(
                            InstanceIds=[instance_id], DryRun=False)

                        instance_object.wait_until_running()

                        print(region + ': Adding sleep(30) to avoid race condition.')

                        time.sleep(30)
                        
                        check = region_client.describe_instances(InstanceIds=[instance_id])

                        state = check['Reservations'][0]['Instances'][0]['State']['Name']

                        print(region + ': Check state: ' + state)

                        print(region + ': Instance ' + instance_id + ' started.')

                    elif state == 'running':
                        print(region + ': Instance ' + instance_id + ' is already running.')
                    
                    else:
                        continue

                    dns = instance_object.public_dns_name

                    # print('[ec2-user@' + instance['PublicDnsName'] + ']\n')
                    print(region + ': [ec2-user@' + dns + ']')

            endtime = datetime.now()
            print(region + ': End time: ' + str(endtime) + ' [start_region]')

def main():

    if len(sys.argv) < 2:
        print('Usage: start_region.py <region_name>\n')
        sys.exit(0)
    else:
        start_region(sys.argv[1])

if __name__ == "__main__":
    main()
