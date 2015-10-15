import os
import json
import hashlib
import subprocess
from multiprocessing import Pool
from copy import deepcopy
import time

from matplotlib import cm
import matplotlib
from matplotlib import pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d

import numpy as np

import domains.blocks as blks

from expy.job_queue import LocalJobQueue, AvakasJobQueue, RetrieveJobQueue

import brewer2mpl
try:
    from progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, Timer
except:
    pass

def generate_exp_hash(exp_params):
    params_string = json.dumps(exp_params, sort_keys=True)
    return hashlib.md5(params_string).hexdigest()

def set_param_value(params, key, value):
    key_list = key.split(":")
    for sub_key in key_list[:-1]:
        if sub_key not in params:
            params[sub_key] = {}
        params = params[sub_key]

    params[key_list[-1]] = deepcopy(value)

def get_param_value(params, key):
    key_list = key.split(":")
    for sub_key in key_list[:-1]:
        if not sub_key in params:
            return None
        params = params[sub_key]

    return params[key_list[-1]]

def launch_experiment(exp_params, root_path, job_queue, nb_trials=100, pbar=None):
    exp_name = generate_exp_hash(exp_params)
    exp_directory = root_path + "/" + exp_name
    if not os.path.exists(exp_directory):
        os.makedirs(exp_directory)

    if not os.path.isfile(exp_directory + "/results_{}.json".format(nb_trials)):
        for i in range(nb_trials):
            exp_trial_directory = exp_directory + "/{}".format(i)
            if not os.path.exists(exp_trial_directory):
                os.makedirs(exp_trial_directory)

            if not job_queue.is_launched(exp_trial_directory):
                with open(exp_trial_directory + "/params.json", "w") as  exp_params_file:
                    exp_params_file.write(json.dumps(exp_params, exp_params_file))

                job_queue.add_job(exp_trial_directory)
            
            if pbar is not None:
                pbar.update(pbar.currval + 1)

def get_progress(exp_params, root_path, job_queue, nb_trials=100):
    exp_name = generate_exp_hash(exp_params)
    exp_directory = root_path + "/" + exp_name

    if not os.path.isfile(exp_directory + "/results_{}.json".format(nb_trials)):
        nb_finished = 0
        for i in range(nb_trials):
            exp_trial_directory = exp_directory + "/{}".format(i)
            if job_queue.is_done(exp_trial_directory):
                nb_finished += 1
    else:
        nb_finished = nb_trials

    return nb_finished

def get_results(exp_params, root_path, job_queue, nb_trials=100):
    exp_name = generate_exp_hash(exp_params)
    exp_directory = root_path + "/" + exp_name

    results = []
    if not os.path.isfile(exp_directory + "/results_{}.json".format(nb_trials)):
        for i in range(nb_trials):
            exp_trial_directory = exp_directory + "/{}".format(i)
            results.append(job_queue.get_results(exp_trial_directory))
        with open(exp_directory + "/results_{}.json".format(nb_trials), "w") as results_exp_file:
            json.dump(results, results_exp_file)
    else:
        with open(exp_directory + "/results_{}.json".format(nb_trials), "r") as results_exp_file:
            results = json.load(results_exp_file)        

    return np.array(results)

def do_experiments(exp_params_list, nb_trials, root_path, exp_script="experiment.py", job_queue=None):
    if job_queue is None:
        job_queue = AvakasJobQueue(exp_script)

    pbar = ProgressBar(widgets=['Create jobs  :', Percentage(), ' ', Bar(), ETA(),
        '|', FileTransferSpeed()], maxval=nb_trials * len(exp_params_list)).start()

    for i, exp_params in enumerate(exp_params_list):
        launch_experiment(exp_params, root_path, job_queue, nb_trials=nb_trials, pbar=pbar)

    pbar.finish()

    pbar = ProgressBar(widgets=['Running jobs :', Percentage(), ' ', Bar(), Timer()],
        maxval=nb_trials * len(exp_params_list)).start()

    all_finished = False
    i = 0
    while not all_finished:
        i += 1
        all_finished = True
        total_nb_finished = 0
        for exp_params in exp_params_list:
            nb_finished = get_progress(exp_params, root_path, job_queue, nb_trials=nb_trials)
            all_finished &= (nb_finished == nb_trials)
            total_nb_finished += nb_finished
        pbar.update(total_nb_finished)
        if not all_finished:
            time.sleep(job_queue.advise_sleep)

    pbar.finish()

    results_list = []
    for exp_params in exp_params_list:
        results_list.append(get_results(exp_params, root_path, job_queue, nb_trials=nb_trials))

    return results_list

def pool_experiment(default_params, curves, nb_trials=100, pool_exp_name=None, root_path="results"):
    exp_params_list = []
    for curve_name in curves:
        curr_exp_params = deepcopy(default_params)
        for parameter_curve in curves[curve_name]:
            set_param_value(curr_exp_params, parameter_curve, curves[curve_name][parameter_curve])
        exp_params_list.append(curr_exp_params)

    results_list = do_experiments(exp_params_list, nb_trials, root_path)

    Rsd = {}

    i = 0
    for curve_name in curves:
        results = results_list[i]
        Rsd[curve_name] = np.mean(results[:, 1] / results[:, 0])
        i += 1

    for curve_name in curves:
        print "{} : {}".format(curve_name, Rsd[curve_name])

def pool_experiment_3d(default_params, parameters, valuess, curves, nb_trials=100,
    pool_exp_name=None, root_path="results", job_queue=None):
    if pool_exp_name is None:
        pool_exp_name = "_".join(parameters)

    print pool_exp_name

    exp_params_list = []
    for curve_name in curves:
        curr_exp_params = deepcopy(default_params)
        for parameter_curve in curves[curve_name]:
            set_param_value(curr_exp_params, parameter_curve, curves[curve_name][parameter_curve])

        for parameter_value0 in valuess[0]:
            for parameter_value1 in valuess[1]:
                set_param_value(curr_exp_params, parameters[0], parameter_value0)
                set_param_value(curr_exp_params, parameters[1], parameter_value1)
                exp_params_list.append(deepcopy(curr_exp_params))

    results_list = do_experiments(exp_params_list, nb_trials, root_path, job_queue=job_queue)
    results_set = {}

    Xsd = {}
    Ysd = {}
    Rsd = {}
    Qsd = {}

    i = 0
    for curve_name in curves:
        Xsd[curve_name] = []
        Ysd[curve_name] = []
        Rsd[curve_name] = []
        for parameter_value0 in valuess[0]:
            Xsd[curve_name].append([])
            Ysd[curve_name].append([])
            Rsd[curve_name].append([])
            for parameter_value1 in valuess[1]:
                results = results_list[i]
                Xsd[curve_name][-1].append(parameter_value0)
                Ysd[curve_name][-1].append(parameter_value1)
                Rsd[curve_name][-1].append(np.mean(results[:, 1] / results[:, 0]))
                i += 1

    fig = plt.figure(pool_exp_name)
    ax = fig.add_subplot(111, projection='3d')

    colors = brewer2mpl.get_map('Set1', 'Qualitative', 9).mpl_colors
    for curve_name, color in zip(curves, colors):
        ax.plot_wireframe(Xsd[curve_name], Ysd[curve_name], Rsd[curve_name], color=color, label=curve_name)

    ax.legend(loc=2)
    ax.set_xlabel(parameters[0])
    ax.set_ylabel(parameters[1])
    ax.set_zlabel("performance")
    ax.set_zlim(0, 1)


def plot_curve(x_values, results, color, axes, label):
    reward_performances = np.zeros((len(results)))
    reward_performances_std = np.zeros((len(results)))

    for i, performances in enumerate(results):
        reward_performances[i] = performances["means"]
        reward_performances_std[i] = performances["stds"]

    axes.plot(x_values, reward_performances, color=color, label=label)
    axes.fill_between(x_values, reward_performances + reward_performances_std,
        reward_performances - reward_performances_std, facecolor=color, alpha=0.1)

def pool_experiment_curves(default_params, parameter, values, curves, nb_trials=100,
    pool_exp_name=None, root_path="results", log_scale=False, color_index=0, job_queue=None):
    if pool_exp_name is None:
        pool_exp_name = parameter

    print pool_exp_name

    exp_params_list = []
    for curve_name in curves:
        curr_exp_params = deepcopy(default_params)
        for parameter_curve in curves[curve_name]:
            set_param_value(curr_exp_params, parameter_curve, curves[curve_name][parameter_curve])

        for parameter_value in values:
            set_param_value(curr_exp_params, parameter, parameter_value)
            exp_params_list.append(deepcopy(curr_exp_params))

            print curve_name, "with", parameter_value, ":", generate_exp_hash(curr_exp_params)

    results_list = do_experiments(exp_params_list, nb_trials, root_path, job_queue=job_queue)

    results_set = {}

    i = 0
    for curve_name in curves:
        results_set[curve_name] = []
        for parameter_value in values:
            results = results_list[i]
            results_set[curve_name].append(
            {
                "means" : np.mean(results[:, 1] / results[:, 0]),
                "stds" : np.std(results[:, 1] / results[:, 0]) / np.sqrt(nb_trials),
            })
            i += 1

    plt.figure(pool_exp_name)
    colors = brewer2mpl.get_map('Set1', 'Qualitative', 9).mpl_colors[color_index:]
    for curve_name, color in zip(curves, colors):
        plot_curve(values, results_set[curve_name], color, plt.axes(), curve_name)

    plt.legend(loc=4)
    plt.ylim([0, 1])
    plt.xlabel(parameter)
    plt.ylabel("performance")
    if log_scale:
        plt.xscale("log")
    plt.savefig(pool_exp_name + ".png")

def pool_experiment_curves_multi(default_params, parameter_list, values_list, absissa_list, curves,
    nb_trials=100, pool_exp_name=None, x_label=None, root_path="results", log_scale=False, color_index=0, job_queue=None):
    if pool_exp_name is None:
        pool_exp_name = parameter

    print pool_exp_name

    exp_params_list = []
    for curve_name in curves:
        curr_exp_params = deepcopy(default_params)
        for parameter_curve in curves[curve_name]:
            set_param_value(curr_exp_params, parameter_curve, curves[curve_name][parameter_curve])

        for param_values in values_list:
            for parameter, value in zip(parameter_list, param_values):
                set_param_value(curr_exp_params, parameter, value)
            exp_params_list.append(deepcopy(curr_exp_params))

            # print curve_name, "with", " ".join([str(p) for p in param_values]), ":", generate_exp_hash(curr_exp_params)

    results_list = do_experiments(exp_params_list, nb_trials, root_path, job_queue=job_queue)

    results_set = {}

    i = 0
    for curve_name in curves:
        results_set[curve_name] = []
        for absissa in absissa_list:
            results = results_list[i]
            results_set[curve_name].append(
            {
                "means" : np.mean(results[:, 1] / results[:, 0]),
                "stds" : np.std(results[:, 1] / results[:, 0]) / np.sqrt(nb_trials),
            })
            i += 1

    plt.figure(pool_exp_name)
    colors = brewer2mpl.get_map('Set1', 'Qualitative', 9).mpl_colors[color_index:]
    for curve_name, color in zip(curves, colors):
        plot_curve(absissa_list, results_set[curve_name], color, plt.axes(), curve_name)

    plt.legend(loc=4)
    plt.ylim([0, 1])
    plt.xlabel(x_label)
    plt.ylabel("performance")
    if log_scale:
        plt.xscale("log")
    plt.savefig(pool_exp_name + ".png")

def pool_experiment_curves_multi_interactive(default_params, curves, nb_trials, pool_exp_name,
    root_path="results", log_scale=False, color_index=0, job_queue=None):
    if pool_exp_name is None:
        pool_exp_name = parameter

    print pool_exp_name

    exp_params_list = []
    for curve_name in curves:
        curr_exp_params = deepcopy(default_params)
        for parameter_curve in curves[curve_name]:
            set_param_value(curr_exp_params, parameter_curve, curves[curve_name][parameter_curve])

        exp_params_list.append(deepcopy(curr_exp_params))

    logs_list = do_experiments(exp_params_list, nb_trials, root_path, job_queue=job_queue)

    results_set = {}
    # learning_progress_dict = {}
    gb_ratio_dict = {}
    number_errors_dict = {}
    nb_inputs = {}

    eval_list = range(0, default_params["interactions"]["nb"] + 1, default_params["evaluation"]["period"])

    i = 0
    for id_curve, curve_name in enumerate(curves):
        logs = logs_list[i]

        results_set[curve_name] = []
        results = np.array([log["results"] for log in logs])
        for id_eval in range(len(eval_list)):
            results_set[curve_name].append({
                "means" : np.mean(results[:, id_eval, 1] / results[:, id_eval, 0]),
                "stds" : np.std(results[:, id_eval, 1] / results[:, id_eval, 0]) / np.sqrt(nb_trials),
            })

        number_errors = np.array([np.cumsum([float(not c) for c in trial["correct_history"]]) for trial in logs])
        number_errors_dict[curve_name] = [{"means" : 0., "stds" : 0}]
        for id_step in range(exp_params_list[id_curve]["interactions"]["nb"]):
            number_errors_dict[curve_name].append({
                "means" : np.mean(number_errors[:, id_step]),
                "stds" : np.std(number_errors[:, id_step]) / np.sqrt(nb_trials),
            })

        # number_errors = np.array([[float(not c) for c in trial["correct_history"]] for trial in logs])
        # number_errors_dict[curve_name] = [{"means" : 1., "stds" : 0}] * 5
        # for id_step in range(5, exp_params_list[id_curve]["interactions"]["nb"]):
        #     number_errors_dict[curve_name].append({
        #         "means" : np.mean(np.sum(number_errors[:, id_step - 5:id_step], axis=1) / 5),
        #         "stds" : np.std(np.sum(number_errors[:, id_step - 5:id_step], axis=1) / 5) / np.sqrt(nb_trials),
        #     })

        number_goods = np.array([[float(s[0]) for s in trial["datasets_size"]] for trial in logs])
        number_bads = np.array([[s[1] for s in trial["datasets_size"]] for trial in logs])
        ratios = number_goods / (number_goods + number_bads)

        gb_ratio_dict[curve_name] = []
        for id_step in range(exp_params_list[id_curve]["interactions"]["nb"]):
            gb_ratio_dict[curve_name].append({
                "means" : np.mean(ratios[:, id_step]),
                "stds" : np.std(ratios[:, id_step]) / np.sqrt(nb_trials),
            })

        nb_inputs[curve_name] = [0.]
        for id_step in range(exp_params_list[id_curve]["interactions"]["nb"]):
            if id_step < exp_params_list[id_curve]["interactions"]["nb_demo"]:
                nb_inputs[curve_name].append(float(id_step))
            elif exp_params_list[id_curve]["teacher"]["corrections"]:
                nb_inputs[curve_name].append(np.mean(number_bads[:, id_step]) +
                    exp_params_list[id_curve]["interactions"]["nb_demo"])
            else:
                nb_inputs[curve_name].append(0.)

        i += 1

    plt.figure(pool_exp_name)
    colors = brewer2mpl.get_map('Set1', 'Qualitative', 9).mpl_colors[color_index:]

    # axes = plt.subplot(321)
    axes = plt.subplot(221)
    for curve_name, color in zip(curves, colors):
        plot_curve(eval_list, results_set[curve_name], color, axes, curve_name)
    plt.ylim([0, 1.05])
    plt.xlim([eval_list[0], eval_list[-1]])
    # plt.xlabel("number of actions")
    plt.ylabel("performance")
    if log_scale:
        plt.xscale("log")

    # axes = plt.subplot(323)
    axes = plt.subplot(223)
    for curve_name, color in zip(curves, colors):
        plot_curve(range(default_params["interactions"]["nb"] + 1), number_errors_dict[curve_name], color, axes, curve_name)
    plt.xlim([eval_list[0], eval_list[-1]])
    plt.xlabel("number of actions")
    plt.ylabel("number of errors")
    if log_scale:
        plt.xscale("log")

    # axes = plt.subplot(325)
    # for curve_name, color in zip(curves, colors):
    #     plot_curve(range(1, default_params["interactions"]["nb"] + 1), gb_ratio_dict[curve_name], color, axes, curve_name)
    # plt.ylim([0, 1])
    # plt.xlim([eval_list[0], eval_list[-1]])
    # plt.ylabel("datasets size ratio")
    # if log_scale:
    #     plt.xscale("log")
    # plt.xlabel("number of actions")


    # axes = plt.subplot(322)
    axes = plt.subplot(222)
    for curve_name, color in zip(curves, colors):
        plot_curve(nb_inputs[curve_name][::exp_params_list[id_curve]["evaluation"]["period"]], results_set[curve_name], color, axes, curve_name)
    plt.ylim([0, 1.05])
    plt.xlim([eval_list[0] - 1, eval_list[-1]])
    # plt.xlabel("number of inputs")
    # plt.ylabel("performance")
    if log_scale:
        plt.xscale("log")

    # axes = plt.subplot(324)
    axes = plt.subplot(224)
    for curve_name, color in zip(curves, colors):
        plot_curve(nb_inputs[curve_name], number_errors_dict[curve_name], color, axes, curve_name)
    plt.xlim([eval_list[0] - 1, eval_list[-1]])
    plt.xlabel("number of inputs")
    # plt.ylabel("number of errors")
    if log_scale:
        plt.xscale("log")

    plt.legend(loc=1, ncol=2)

    # axes = plt.subplot(326)
    # for curve_name, color in zip(curves, colors):
    #     plot_curve(nb_inputs[curve_name][1:], gb_ratio_dict[curve_name], color, axes, curve_name)
    # plt.ylim([0, 1])
    # plt.xlim([eval_list[0], eval_list[-1]])
    # plt.ylabel("datasets size ratio")
    # if log_scale:
    #     plt.xscale("log")
    # plt.xlabel("number of inputs")

    plt.savefig(pool_exp_name + ".png")
