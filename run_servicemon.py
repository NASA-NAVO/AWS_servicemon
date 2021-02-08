#!/bin/env python

import sys
import time
import pprint
import boto3

from datetime import datetime
from botocore.exceptions import ClientError


class run_servicemon():

    def __init__(self, region):


        # This code starts a run of "servicemon on a "NAVO" EC2 instance. 

        pp = pprint.PrettyPrinter(indent=4)


        # Connect to Region

        region_client = boto3.client('ec2', region_name=region)

        ssm = boto3.client('ssm', region_name=region)


        # Find an instance that can run "servicemon"

        starttime = datetime.now()
        print('\n' + region + ': Start time: ' + str(starttime) + ' [run_servicemon]')

        try:
            response = region_client.describe_instances(
                Filters = [
                    {
                        'Name': 'tag:Name',
                        'Values': ['NAVO']
                    }
                ])
        except:
            print(region + ': EC2 describe_instances() failed.')
            sys.exit(0)

        instance_id = -1

        reservations = response['Reservations']

        for reservation in reservations:

            instances = reservation['Instances']

            for instance in instances:

                instance_id = instance['InstanceId']

                state = instance['State']['Name']

                if state == 'terminated':
         
                    continue

        if instance_id == -1:
            print(region + ': No "NAVO" instances. [run_servicemon]')
            sys.exit(0)
        else:
            print(region + ': Instance ID: ' + instance_id)


        # Send a command to (in this case) one EC2 instance

        command  = 'cd /home/ec2-user/ServiceMon; ./aws.sh'

        timeout = 1800

        start_time = time.time()

        try:
            response = ssm.send_command(
                        InstanceIds=[instance_id],
                        DocumentName="AWS-RunShellScript",
                        Parameters={
                            'commands': [command],
                            'executionTimeout': [str(timeout)]
                        } )

            print(region + ': Command "' + command + '" sent to instance ' + instance_id)

            command_id = response['Command']['CommandId']

        except ClientError as e:
            print(region + ': SSM send_command() failed:')
            pp.pprint(region + ": " + str(e))
            sys.exit(0)


        # Poll until command finishes.  Servicemon fires up
        # a bunch of scripts and these will continue running
        # for several minutes.

        total = 0

        while True:
            time.sleep(30)

            total = total + 30

            try:
                list = ssm.list_commands(CommandId=command_id)
            except:
                print(region + ': SSM list_commands() failed.')
                sys.exit(0)

            status = list['Commands'][0]['Status']

            print(region + ': ' + status + ' [' + str(total) + ']')

            if status == 'Pending' or status == 'InProgress':
                continue

            elif status == 'Failed':
                print(region + ': Failed (or timeout)\n')
                break

            elif status == 'Success':
                elapsed_time = time.time() - start_time
                print(region + ': Success.  Elapsed time: ' + str(elapsed_time))
                break

            else:
                print(region + ': Final status:  ' + status)

                elapsed_time = time.time() - start_time
                print(region + ': Elapsed time: ' + str(elapsed_time))
                break

        endtime = datetime.now()
        print(region + ': End time: ' + str(endtime) + ' [start_region]\n')


def main():

    if len(sys.argv) < 2:
        print('Usage: run_servicemon.py <region_name>\n')
        sys.exit(0)
    else:
        run_servicemon(sys.argv[1])
        sys.exit(0)

if __name__ == "__main__":
    main()
