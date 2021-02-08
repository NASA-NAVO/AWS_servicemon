#!/bin/sh

export PATH=.:/home/jcg/bin:/home/jcg/anaconda3/bin:/exo/cm/ws/jcg/montage/bin:/usr/bin:/bin:$PATH

export LD_LIBRARY_PATH=/usr/lib:/exo/cm/ws/jcg/exoenv/misc/lib:/exo/cm/ws/jcg/exoenv/core/lib64:/exo/cm/ws/jcg/exoenv/python/lib:/exo/cm/ws/jcg/exoenv/gnu/lib:/usr/lib64:/usr/lib:$LD_LIBRARY_PATH

export PYTHONPATH=/home/jcg/python/lib:/exo/cm/ws/jcg/exoenv/python/lib:/exo/cm/ws/jcg/rtb/lib:/exo/cm/ws/jcg/base/lib/python:/exo/cm/ws/jcg/exo/lib/python:/exo/cm/ws/jcg/base/lib64/python:$PYTHONPATH

cd /home/jcg/ServiceMon/AWS

python run_region.py $1
