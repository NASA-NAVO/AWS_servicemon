#!/bin/env python

import sys
import boto3
from botocore.exceptions import ClientError


# To get a list of the AWS regions we have access to:

ec2 = boto3.client('ec2')

aws_regions = ec2.describe_regions()

print ('\nRegions we have access to:\n')
for region in aws_regions['Regions']:
    region_name = region['RegionName']
    print ('   ', region_name)

print ('')
