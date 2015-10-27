#!/home/bclement/virtualenvs/test/bin/python
#PBS -o jobs/2015-10-27_17-35-47__c7020384-7cc8-11e5-8014-f01faf1b32a8/output.txt
#PBS -e jobs/2015-10-27_17-35-47__c7020384-7cc8-11e5-8014-f01faf1b32a8/error.txt
#PBS -l walltime=01:00:00
#PBS -l nodes=1:ppn=1
#PBS -N 2015-10-27_17-35-47__c7020384-7cc8-11e5-8014-f01faf1b32a8


import os
import sys
import shutil
import jsonpickle

PBS_JOBID = os.environ['PBS_JOBID']
job_dir = 'jobs/2015-10-27_17-35-47__c7020384-7cc8-11e5-8014-f01faf1b32a8'
work_dir = '/tmp/'+PBS_JOBID

shutil.copytree(job_dir, work_dir)
os.chdir(work_dir)

with open('job.b','r') as f:
	job = jsonpickle.loads(f.read())

job.path = '.'
job.run()

sys.exit(0)
