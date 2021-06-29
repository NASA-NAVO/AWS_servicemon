# AWS_servicemon

*The purpose of this repo is to illustrate an efficient way to manage a large
number of AWS EC2 instances around the world without resorting to fancy packages
to do so.*

The NAVO ServiceMon application is Python code that monitors a configurable set
of TAP (Table Access Protocol) and Cone Search services around the world.  These
protocols were developed by the International Virtual Observatory Alliance (IVOA)
as a standard way to access remote astronomical catalogs.

The other side of monitoring is to see how the location of the site doing the
monitoring affects the results, so it was decided to run ServiceMon from a collection
of AWS (Amazon Web Services) centers around the world.  

This can be done using the AWS console but after doing this for half a dozen centers 
and updating it several times as the code evolves, the manual approach can become
quite taxing.  

The real difference between using the cloud for jobs like this and using your own machines
is not in the programming but in the cost model.  When you buy your own machines the cost
is up-front; after that you are already committed and might as well use those machines as
fully as you can.  On the cloud, resources are incremental, so the primary concern is to
structure jobs so as to use machines in as brief a set of increments as possible and 
turn them "off" in between.

There are two levels of automation that we can use to achieve this control.  AWS provides a 
set of command-line tools (called the AWS CLI) that can be incorporated into general shell 
scripts.  These are quite complete.  They are written in Python and are based on a lower-level 
Python library which can itself be used directly.  For full control, this is the approach to
take.

This library is called "boto3" (more accurately, both boto3 and AWS CLI are built on
"botocore").  It allows us to fully programs the interaction, with exception 
handling and polling were necessary built in.  Of the various programming interfaces
to AWS, boto3 (along with nodejs) is the most complete and efficient.  There is 
essentially nothing you can do to AWS that you can't do through it.


## Configuring AWS

We chose to use the AWS "us-west-2" region (in Oregon) as our base.  There we 
configured an EC2 instance (using a small "t2.micro" platform) with Anaconda Python
some support libraries, and the ServiceMon code and configuration files, then created 
a machine image (AMI) from the instance (ours was named "NAVO" for ease in referencing it).
This is all tuned to our use case but none of what follows is particulary 
application-specific.

There are several things you have to do to replicate such a system in another 
region and doing it by copying an existing configuration is by far the simplest
approach.  We have captured all this in a Python script called "config_region.py",
which does the following:

* Search our 'home' region (us-west-2) for our AMI by name ('NAVO').

* Copy the AMI to the new region.  Regions are self-contained; you
can't refer to AMIs, etc. across them.

* Set up an security keypair. AWS can generate keypairs for you or
you can use ssh-keygen, etc. AWS never needs or wants the private
key, that is your responsibility.  We want the say keypair on all
regions so we upload the public key ourselves.

* Set up a "security group" (i.e. the rules for handling network
protocols).  We only need ssh access and we had set up our 'home'
instance that way, so we download the specifics of that security
group and us them to create our security group on the new region.

* Now we have enough set up to create an EC2 instance on the new
region (with checks to see that it doesn't already exist). We
add a 'tag' with key "Name" and value "NAVO", again to help 
find things later.

* We want to use the AWS "Systems Management" package, which will
let us run programs on the instance without having to log in
via ssh first.  The way AWS has this set up, it requires giving
the instance permission to do certain things on it own.  AWS
refers to this as a 'role'.  It is possible to set this up from
first principles using JSON structures but there are a lot of 
details and since we have such a role already set up on our
'home' instance, we an just go get that and associate it with
the new region.

* Finally, the new instance we create will by default be running.
Since running an instance costs real money we only want to do
that when we have actual work to do, so we 'stop' the instance.
It still exists but in a stopped state we won't be charged
(except for any permanent storage associate with the instance).

There are also ancillary scripts to clear out everything associated with an
region (clear_region.py) including instance, AMI, keypairs, etc. and to 
check a region (check_region.py) by listing out the details of all the above.

We are using a set of six regions spaced around the world (us-west-2 in Oregon,
us-east-1 in Virginia, sa-east-1 in Sao Paolo Brazil, eu-west-3 in Paris,
ap-northeast-1 in Tokyo and ap-southeast-2 in Sydney Australia).


## Running ServiceMon Jobs

Since we want to limit the times that the EC2 instances are running, we will
use a set of scripts to:

* Start an instance (start_region.py).

* Run the ServiceMon code on the instance (run_servicemon.py).

* Stop the instance (stop_region.py).

These are further wrapped with a simple "run_region.py" script.

On a local (non-cloud) machine, we are running cron job which cycles through 
the regions and around the clock, so there is one Servicemon run every hour:

<pre>
30  0,6,12,18 * * * /home/ServiceMon/AWS/run_region.sh us-west-2      >> /tmp/ServiceMon.debug 2>&1
30  1,7,13,19 * * * /home/ServiceMon/AWS/run_region.sh us-east-1      >> /tmp/ServiceMon.debug 2>&1
30  2,8,14,20 * * * /home/ServiceMon/AWS/run_region.sh sa-east-1      >> /tmp/ServiceMon.debug 2>&1
30  3,9,15,21 * * * /home/ServiceMon/AWS/run_region.sh eu-west-3      >> /tmp/ServiceMon.debug 2>&1
30 4,10,16,22 * * * /home/ServiceMon/AWS/run_region.sh ap-northeast-1 >> /tmp/ServiceMon.debug 2>&1
30 5,11,17,23 * * * /home/ServiceMon/AWS/run_region.sh ap-southeast-2 >> /tmp/ServiceMon.debug 2>&1
</pre>

The ServiceMon code sends all the results to a central database (not on the
cloud) so no resource build up on cloud storage, also keeping costs down.

