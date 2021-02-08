#!/bin/env python

import sys
import pprint
import boto3
from botocore.exceptions import ClientError


class clear_region():

    def __init__(self, region):


        # This code delete / deregisters everything in a region associated
        # with NAVO: instance, AMI, keypair and security group.  It also 
        # checks to make sure there are no residual snapshots lying around.

        # We explicitly check and disallow clean-up of our default us-west-2
        # region.
        
        pp = pprint.PrettyPrinter(indent=4)

        if(region == 'us-west-2'):
            print('Error: deleting base region disallowed.')
            sys.exit(0)



        #--------------------------------------------------------------

        # Connect to Region

        region_client   = boto3.client  ('ec2', region_name=region)
        region_resource = boto3.resource('ec2', region_name=region)


        #--------------------------------------------------------------

        # INSTANCES, AMIS AND SNAPSHOTS:

        response = region_client.describe_instances(
            Filters = [
                {
                    'Name': 'tag:Name',
                    'Values': ['NAVO']
                }
            ])

        reservations = response['Reservations']

        if len(reservations) == 0:
            print('No "NAVO" instances.')

        else:

            # Instances

            print('')

            for reservation in reservations:

                instances = reservation['Instances']

                for instance in instances:

                    instance_id = instance['InstanceId']

                    instance_object = region_resource.Instance(instance_id)

                    region_client.terminate_instances(InstanceIds=[instance_id])

                    instance_object.wait_until_terminated()

                    print('Instance ' + instance_id + ' terminated.')


            # AMIs

            response = region_client.describe_images(Owners=['self'], 
                           Filters=[{'Name': 'name', 'Values':['NAVO']}])

            images = response['Images']

            for image in images:

                ami_id = image['ImageId']

                response = region_client.deregister_image(ImageId=ami_id)

                print('"NAVO" AMI ID ' + ami_id + ' for region ' + region + ' deregistered.')


            # Snapshots

            snapshots = region_client.describe_snapshots(OwnerIds=['self'])['Snapshots']

            for snapshot in snapshots:
                
                if snapshot['Description'].find(ami_id) > 0:

                    snapshot_id = snapshot['SnapshotId']

                    response = region_client.delete_snapshot(SnapshotId=snapshot_id)

                    print('Snapshot ' + snapshot_id + ' deleted.')


        #--------------------------------------------------------------

        # KEYPAIRS:

        response = region_client.describe_key_pairs(
                       Filters=[{'Name': 'key-name', 'Values': ['NAVO']}])

        keypairs = response['KeyPairs']

        for keypair in keypairs:

            keypair_id = keypair['KeyPairId']

            region_client.delete_key_pair(KeyPairId=keypair_id)

            print('"NAVO" key pair ' + keypair_id + ' deleted.')


        #--------------------------------------------------------------

        # SECURITY GROUPS:

        try:
            response = region_client.describe_security_groups(GroupNames=['NAVO'])

            security_groups = response['SecurityGroups']

            for security_group in security_groups:

                security_group_id = security_group['GroupId']

                region_client.delete_security_group(GroupId=security_group_id)

                print('"NAVO" security group ' + security_group_id + ' deleted.')

        except:
            pass

        print('')



def main():

    if len(sys.argv) < 2:
        print('Usage: clear_region.py <region_name>\n')
        sys.exit(0)
    else:
        clear_region(sys.argv[1])

if __name__ == "__main__":
    main()

