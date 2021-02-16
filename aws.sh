#!/bin/sh

rm -rf result/*

sm_run_all input \
   --result_dir result \
   --num_cones 10 \
   --writer aws_writer
