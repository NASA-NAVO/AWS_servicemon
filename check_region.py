#!/bin/env python

import sys
import pprint
import boto3
from botocore.exceptions import ClientError


class check_region():

    def __init__(self, region):


        # This code delete / deregisters everything in a region associated
        # with NAVO: instance, AMI, keypair and security group.  It also 
        # checks to make sure there are no residual snapshots lying around.
        # If you are not careful, the storage associated with old state
        # snapshots can add up.

        pp = pprint.PrettyPrinter(indent=4)

        print('')
        print('Region: ' + region)
        print('')


        #--------------------------------------------------------------

        # Connect to Region

        region_client = boto3.client('ec2', region_name=region)


        #--------------------------------------------------------------

        # INSTANCE, AMI AND SNAPSHOTS:

        # Instances

        try:
            response = region_client.describe_instances(
                Filters = [
                    {
                        'Name': 'tag:Name',
                        'Values': ['NAVO']
                    }
                ])

            instances = response['Reservations'][0]['Instances']

            for instance in instances:
                instance_id = instance['InstanceId']

                print('Instance: ' + instance_id)

        except:
            print('No "NAVO" instances.')


        # AMI

        try:
            images = region_client.describe_images(Owners=['self'], 
                       Filters=[{'Name': 'name', 'Values':['NAVO']}])

            ami_id = images['Images'][0]['ImageId']

            print('"NAVO" AMI ID: ' + ami_id)

        except:
            print('No "NAVO" AMI.')


        # Snapshots

        snapshots = region_client.describe_snapshots(OwnerIds=['self'])['Snapshots']

        for snapshot in snapshots:
            
            if snapshot['Description'].find(ami_id) > 0:

                snapshot_id = snapshot['SnapshotId']

                print('Snapshot: ' + snapshot_id)


        #--------------------------------------------------------------

        # KEYPAIR:

        try:
            keypairs = region_client.describe_key_pairs(
                          Filters=[{'Name': 'key-name', 'Values': ['NAVO']}])

            keypair_id = keypairs['KeyPairs'][0]['KeyPairId']

            print('"NAVO" key pair: ' + keypair_id)

        except:
            print('No "NAVO" keypair found.')


        #--------------------------------------------------------------

        # SECURITY GROUP:

        try:
            response = region_client.describe_security_groups(GroupNames=['NAVO'])

            security_group_id = response['SecurityGroups'][0]['GroupId']

            print('"NAVO" security group: ' + security_group_id)

        except:
            print('No "NAVO" security group found.')

        print('')



def main():

    if len(sys.argv) < 2:
        print('Usage: check_region.py <region_name>\n')
        sys.exit(0)
    else:
        check_region(sys.argv[1])

if __name__ == "__main__":
    main()

