#!/bin/bash
echo "job finished, backing up files."
PBS_JOBID=$1
cp -f -R /tmp/$PBS_JOBID/* jobs/2015-10-27_17-38-26__25acd080-7cc9-11e5-b3e2-f01faf1b32a8/
exit 0
