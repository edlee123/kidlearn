import os
import json

class JobQueue:
    def __init__(self):
        pass

    def add_job(self, directory):
        pass

    def is_launched(self, directory):
        pass

    def is_done(self, directory):
        pass

    def get_results(self, directory):
        pass

import zmq
import threading
import subprocess

BROCKER_BACKEND = "ipc://brocker_backend.ipc"
BROCKER_FRONTEND = "ipc://brocker_frontend.ipc"

def worker_routine(exp_script):
    """Worker routine"""
    context = zmq.Context.instance()

    socket = context.socket(zmq.REQ)
    socket.connect(BROCKER_BACKEND)

    while True:
        socket.send(b"READY")
        request = socket.recv()
        subprocess.call(["python", exp_script, request],
            stdin=open(os.devnull, 'r'), stdout=open("out", 'w'), stderr=open("err", 'w'))

def broker_routine():
    context = zmq.Context.instance()

    frontend = context.socket(zmq.PULL)
    frontend.bind(BROCKER_FRONTEND)

    backend = context.socket(zmq.ROUTER)
    backend.bind(BROCKER_BACKEND)

    poller = zmq.Poller()
    poller.register(backend, zmq.POLLIN)
    poller.register(frontend, zmq.POLLIN)

    workers_list = []

    while True:
        socks = dict(poller.poll())
        # Handle worker activity on backend
        if (backend in socks and socks[backend] == zmq.POLLIN):
            message = backend.recv_multipart()

            # First frame is worker adress
            workers_list.append(message[0])
            # Second frame is empty
            assert message[1] == ""
            # Third frame is READY
            assert message[2] == "READY"

        # poll on frontend only if workers are available
        if len(workers_list) > 0:
            if (frontend in socks and socks[frontend] == zmq.POLLIN):
                worker_id = workers_list.pop()
                backend.send_multipart([worker_id, "", frontend.recv()])

    frontend.close()
    backend.close()
    context.term()

import time

class LocalJobQueue(JobQueue):
    def __init__(self, exp_script, nb_worker=1):
        self.exp_script = exp_script
        self.advise_sleep = 10

        self._context = zmq.Context.instance()
        self._socket = self._context.socket(zmq.PUSH)
        self._socket.connect(BROCKER_FRONTEND)

        for i in range(nb_worker):
            worker = threading.Thread(target=worker_routine, args=(self.exp_script,))
            worker.daemon = True
            worker.start()

        broker = threading.Thread(target=broker_routine)
        broker.daemon = True
        broker.start()

    def add_job(self, directory):
        self._socket.send(directory)
        
    def is_launched(self, directory):
        return self.is_done(directory)

    def is_done(self, directory):
        return os.path.isfile(directory + "/results.json")

    def get_results(self, directory):
        with open(directory + "/results.json", "r") as results_file:
            results = json.load(results_file)
        return results

class RetrieveJobQueue(JobQueue):
    def __init__(self):
        pass
        
    def add_job(self, directory):
        print "RetrieveJobQueue cannot add job."
        assert False
        
    def is_launched(self, directory):
        return self.is_done(directory)

    def is_done(self, directory):
        return os.path.isfile(directory + "/results.json")

    def get_results(self, directory):
        with open(directory + "/results.json", "r") as results_file:
            results = json.load(results_file)
        return results


class InteractiveJobQueue(JobQueue):
    def __init__(self, exp_script):
        self.exp_script = exp_script

    def add_job(self, directory):
        subprocess.call(["python {} {}".format(self.exp_script, directory)], shell=True)
        
    def is_launched(self, directory):
        return self.is_done(directory)

    def is_done(self, directory):
        return os.path.isfile(directory + "/results.json")

    def get_results(self, directory):
        with open(directory + "/results.json", "r") as results_file:
            results = json.load(results_file)
        return results

import subprocess
from expy.ssh import SSHSession

class AvakasJobQueue(JobQueue):
    def __init__(self, exp_script, max_time="2:00:00"):
        self._session = SSHSession("avakas.mcia.univ-bordeaux.fr", "thimunzer", key_file=open("/home/tmunzer/.ssh/no_passphrase", "r"))
        self._session.command("module load torque")
        self.exp_script = exp_script
        self.advise_sleep = 60
        if isinstance(max_time, str):
            self.max_time = max_time
        else:
            assert isinstance(max_time, int)
            self.max_time = str(max_time) + ":00:00"

    def add_job(self, directory):
        # print
        # print "add_job : ", directory
        with open(directory + "/job.pbs", "w") as job_file:
            job_file.write("\
#PBS -o Repos/Inria/thibaut/{0}/out\n\
#PBS -e Repos/Inria/thibaut/{0}/err\n\
#PBS -l walltime={1}\n\
#PBS -l nodes=1:ppn=2\n\
#PBS -N {2}\n\
\n\
printf \"/tmp/$PBS_JOBID\" > Repos/Inria/thibaut/{0}/tmp_dir_name\n\
source virtualenvs/py2.7/bin/activate;\n\
cd Repos/Inria/thibaut/;\n\
python {3} {0};\n\
sleep 1;\n\
touch {0}/finished\n".format(directory, self.max_time, directory[:-10], self.exp_script))

        self._session.create_path("Repos/Inria/thibaut/{}".format(directory))
        self._session.put("{}/params.json".format(directory),
            "Repos/Inria/thibaut/{}/params.json".format(directory))
        self._session.put("{}/job.pbs".format(directory),
            "Repos/Inria/thibaut/{}/job.pbs".format(directory))

        self._session.command("qsub Repos/Inria/thibaut/{}/job.pbs".format(directory))

    def is_launched(self, directory):
        return self._session.path_exists("Repos/Inria/thibaut/{}".format(directory))

    def is_done(self, directory):
        # print
        # print "is_done : ", directory
        if os.path.isfile(directory + "/results.json"):
            return True
        # elif not self._session.is_dir("Repos/Inria/thibaut/{}".format(directory)):
        #     return False
        elif not self._session.path_exists("Repos/Inria/thibaut/{}/finished".format(directory)):
            # print "not done :", directory
            # self._session.command("qsub Repos/Inria/thibaut/{}/job.pbs".format(directory))
            return False
        else:
            if self._session.path_exists("Repos/Inria/thibaut/{}/results.json".format(directory)):
                self._session.get("Repos/Inria/thibaut/{}/results.json".format(directory),
                    "{}/results.json".format(directory))
                return True
            else:
                print "relaunch : ", directory
                # assert False
                # self._session.command("rm Repos/Inria/thibaut/{}/finished".format(directory))
                # self._session.command("qsub Repos/Inria/thibaut/{}/job.pbs".format(directory))
                return False

    def get_results(self, directory):
        # print
        # print "get_results : ", directory
        with open(directory + "/results.json", "r") as results_file:
            results = json.load(results_file)
        return results

