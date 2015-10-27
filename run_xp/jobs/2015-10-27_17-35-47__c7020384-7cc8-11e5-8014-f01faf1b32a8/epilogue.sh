#!/bin/bash
echo "job finished, backing up files."
PBS_JOBID=$1
cp -f -R /tmp/$PBS_JOBID/* jobs/2015-10-27_17-35-47__c7020384-7cc8-11e5-8014-f01faf1b32a8/
exit 0
