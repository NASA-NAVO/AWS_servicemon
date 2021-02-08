#!/bin/env python

import sys
import time
import pprint
import boto3

from datetime import datetime
from botocore.exceptions import ClientError


class run_command():

    def __init__(self, region):


        # This code starts a run of a command on a "NAVO" EC2 instance. 

        pp = pprint.PrettyPrinter(indent=4)


        # Connect to Region

        region_client = boto3.client('ec2', region_name=region)

        ssm = boto3.client('ssm', region_name=region)


        # Find an instance that can run "command"

        try:
            response = region_client.describe_instances(
                Filters = [
                    {
                        'Name': 'tag:Name',
                        'Values': ['NAVO']
                    }
                ])
        except:
            print('EC2 describe_instances() failed.')
            sys.exit(0)

        starttime = datetime.now()
        print('Start time: ' + str(starttime) + ' [run_command]')

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
            print('\n' + region + ': No "NAVO" instances. [run_command]')
            sys.exit(0)
        else:
            print('\nInstance ID: ' + instance_id)


        # Send a command to (in this case) one EC2 instance

        command  = 'ls -l'

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

            print('\n' + region + ': Command "' + command + '" sent to instance ' + instance_id)

            command_id = response['Command']['CommandId']

        except ClientError as e:
            print('\nSSM send_command() failed:')

            print('\n-------------------------------------------------------')
            pp.pprint(e)
            print('-------------------------------------------------------\n')

            sys.exit(0)


        # Poll until command finishes.  command fires up
        # a bunch of scripts and these will continue running
        # for several minutes.

        while True:
            time.sleep(30)

            try:
                list = ssm.list_commands(CommandId=command_id)
            except:
                print('SSM list_commands() failed.')
                sys.exit(0)

            status = list['Commands'][0]['Status']

            if status == 'Pending' or status == 'InProgress':
                continue

            elif status == 'Failed':
                print('\n' + region + ': Failed (or timeout)\n')
                break

            elif status == 'Success':
                elapsed_time = time.time() - start_time
                print('\n' + region + ': Success.  Elapsed time: ' + str(elapsed_time))

                print('---------------------------------------')
                pp.pprint(list)
                print('---------------------------------------')
                break

            else:
                print('\n' + region + ': Final status:  ' + status)

                print('---------------------------------------')
                pp.pprint(list)
                print('---------------------------------------')

                elapsed_time = time.time() - start_time
                print('\n' + region + ': Elapsed time: ' + str(elapsed_time))
                break

        endtime = datetime.now()
        print('End time: ' + str(endtime) + ' [run_command]\n')


def main():

    if len(sys.argv) < 2:
        print('Usage: run_command.py <region_name>\n')
        sys.exit(0)
    else:
        run_command(sys.argv[1])
        sys.exit(0)

if __name__ == "__main__":
    main()
