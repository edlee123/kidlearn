""" module providing functions for basic evaluation of RCSI """

from world import World
from domains import domain_dict

from optimal_control import create_policy as create_policy_oc
from uct import create_policy as create_policy_uct
from planner import planner_evaluate

from rcsi import Rcsi
from policy_matching import Rpm
from NPSCIRL import RNPSCIRL
from blmril import Blmril
from tbril import Tbril
from boosted_policy_learning import BoostedPolicyLearning

import numpy as np
import random
import matplotlib.pyplot as plt
import json
import pickle
import os.path
from math import ceil, log

def create_expert_dataset(domain, policy, demos_params, exp_directory):
    dataset_expert = []
    if os.path.isfile(exp_directory + "/dataset_expert.pckl"):
        dataset_expert = pickle.load(open(exp_directory + "/dataset_expert.pckl", "r"))
    else:
        for i in range(demos_params["nb_episodes"]):
            initial_state = domain.get_random_state()
            world = World(initial_state, domain)
            while True:
                state = world.state
                action = policy(state)
                if random.random() < demos_params["noise"] / 100.:
                    action = random.choice(world.get_actions())

                world.apply_action(action)
                next_state = world.state
                dataset_expert.append((state, action, next_state))
                if action == "wait":
                    break
        with open(exp_directory + "/dataset_expert.pckl", "w") as expert_file:
            pickle.dump(dataset_expert, expert_file)

    return dataset_expert

def create_random_dataset(domain, policy, dynamics_param, exp_directory):
    dataset_random = []
    if os.path.isfile(exp_directory + "/dataset_random.pckl"):
        dataset_random = pickle.load(open(exp_directory + "/dataset_random.pckl", "r"))
    else:
        if dynamics_param["type"] == "random":
            for _ in range(dynamics_param["nb_episodes"]):
                initial_state = domain.get_random_state()
                world = World(initial_state, domain)
                for _ in range(1):
                    state = world.state
                    action = random.choice(domain.get_actions(state))
                    world.apply_action(action)
                    next_state = world.state
                    dataset_random.append((state, action, next_state))

        elif dynamics_param["type"] == "epsilon_greedy":
            while len(dataset_random) < dynamics_param["nb_episodes"]:
                initial_state = domain.get_random_state()
                world = World(initial_state, domain)
                while len(dataset_random) < dynamics_param["nb_episodes"]:
                    state = world.state
                    action_expert = policy(state)
                    if random.random() < dynamics_param["epsilon"]:
                        action = random.choice(world.get_actions())
                    else:
                        action = action_expert

                    world.apply_action(action)
                    next_state = world.state
                    dataset_random.append((state, action, next_state))
                    if action == "wait":
                        break

            print len(dataset_random)

        with open(exp_directory + "/dataset_random.pckl", "w") as random_file:
            pickle.dump(dataset_random, random_file)


    return dataset_random

def evaluate(domain, target_policy, learned_policy, reward_fun, eval_params):
    results = []

    for _ in range(eval_params["nb_episodes"]):
        initial_state = domain.get_random_state()
        rewards_list = []

        for policy in [target_policy, learned_policy]:
            curr_decay = 1.
            curr_reward = 0.

            world = World(initial_state, domain)

            i = 0
            while i < (log(eval_params["tol"]) / log(eval_params["decay_factor"])) and i != eval_params["nb_actions"]:
                state = world.state
                action = policy(state)
                world.apply_action(action)

                curr_reward += curr_decay * reward_fun(state, action)
                curr_decay *= eval_params["decay_factor"]
                i += 1

            while i < log(eval_params["tol"]) / log(eval_params["decay_factor"]):
                state = world.state
                action = reward_fun.optimal_policy(state)
                world.apply_action(action)

                curr_reward += curr_decay * reward_fun(state, action)
                curr_decay *= eval_params["decay_factor"]
                i += 1

            rewards_list.append(curr_reward)
        results.append(rewards_list)

    results = np.array(results)
    return list(np.mean(results, axis=0))

def evaluate_percentage_reward(domain, learned_reward, target_reward, eval_params):
    results = []

    for _ in range(eval_params["nb_episodes"]):
        initial_state = domain.get_random_state()
        action_list = domain.get_actions(initial_state)

        action_value_list = []
        for action_tested in action_list:
            curr_decay = 1.
            curr_reward = 0.

            world = World(initial_state, domain)

            curr_reward += curr_decay * learned_reward(initial_state, action_tested)
            curr_decay *= eval_params["decay_factor"]

            world.apply_action(action_tested)

            i = 1

            while i < log(eval_params["tol"]) / log(eval_params["decay_factor"]):
                state = world.state
                action = target_reward.optimal_policy(state)
                world.apply_action(action)

                curr_reward += curr_decay * learned_reward(state, action)
                curr_decay *= eval_params["decay_factor"]
                i += 1

            action_value_list.append(curr_reward)
        optimal_action_list = [a for a, v in zip(action_list, action_value_list) if (
            v == max(action_value_list))]

        if len([a for a in target_reward.optimal_actions(initial_state) if a in optimal_action_list]):
            results.append([1., 1.])
        else:
            results.append([1., 0.])
            domain.print_state(initial_state)
            print target_reward.optimal_actions(initial_state)
            print optimal_action_list
            print action_list
            print action_value_list
        print _
    results = np.array(results)
    return list(np.mean(results, axis=0))

def evaluate_percentage_policy(domain, learned_policy, target_reward, eval_params):
    results = []

    for _ in range(eval_params["nb_episodes"]):
        state = domain.get_random_state()
        if learned_policy(state) in target_reward.optimal_actions(state):
            results.append([1., 1.])
        else:
            results.append([1., 0.])
    results = np.array(results)
    return list(np.mean(results, axis=0))

def experiment(exp_directory, redo=False):
    """ Do an experiment (or load it from file) over blocks dataset and plot it """

    results_file_name = exp_directory + "/results.json"

    if not os.path.isfile(results_file_name) or redo:

        if os.path.isfile(os.path.join(exp_directory, "tmp_dir_name")):
            print "toto"
            with  open(os.path.join(exp_directory, "tmp_dir_name"), "r") as f:
                tmp_dir_name = f.read()
                if not os.path.isdir(tmp_dir_name):
                    os.makedirs(tmp_dir_name)
        else:
            tmp_dir_name = exp_directory
        print tmp_dir_name

        with open(exp_directory + "/params.json", "r") as  exp_params_file:
            content = exp_params_file.read()
        exp_params = json.loads(content)

        results = []

        if exp_params["evaluation"]["solver"] == "optimal_control":
            create_policy = create_policy_oc
        elif exp_params["evaluation"]["solver"] == "uct":
            create_policy = create_policy_uct

        domain_train = domain_dict[exp_params["domain_train"]["name"]].Domain(
            exp_params["domain_train"])
        reward_train = domain_train.rewards[exp_params["reward_train"]["name"]]
        try:
            assert not exp_params["domain_train"]["one_block_fixed"] and not exp_params["domain_train"]["random_dynamics"]
            target_policy_train = reward_train.optimal_policy
        except AttributeError:
            target_policy_train = create_policy(domain_train, reward_train, exp_params["evaluation"])

        domain_test = domain_dict[exp_params["domain_test"]["name"]].Domain(
            exp_params["domain_test"])
        reward_test = domain_test.rewards[exp_params["reward_test"]["name"]]
        try:
            assert not exp_params["domain_test"]["one_block_fixed"] and not exp_params["domain_test"]["random_dynamics"]
            target_policy_test = reward_test.optimal_policy
        except AttributeError:
            target_policy_test = create_policy(domain_test, reward_test, exp_params["evaluation"])

        dataset_expert = create_expert_dataset(domain_train, target_policy_train,
            exp_params["demonstrations"], exp_directory)
        dataset_random = create_random_dataset(domain_train, target_policy_train,
            exp_params["dynamics"], exp_directory)

        if exp_params["algorithm"]["output"] == "reward":
            if exp_params["algorithm"]["name"] == "RCSI":
                algorithm = Rcsi(domain_train, exp_params["algorithm"], tmp_dir_name)
            elif exp_params["algorithm"]["name"] == "RPM":
                algorithm = Rpm(domain_train, exp_params["algorithm"], tmp_dir_name)
            elif exp_params["algorithm"]["name"] == "RNPSCIRL":
                algorithm = RNPSCIRL(domain_train, exp_params["algorithm"], tmp_dir_name)
            algorithm.train(dataset_expert, dataset_random)

        elif exp_params["algorithm"]["output"] == "policy":
            if exp_params["algorithm"]["name"] == "BLMRIL":
                algorithm = Blmril(domain_train, exp_params["algorithm"], tmp_dir_name)
            elif exp_params["algorithm"]["name"] == "TBRIL":
                algorithm = Tbril(domain_train, exp_params["algorithm"], tmp_dir_name)
            elif exp_params["algorithm"]["name"] == "BPL":
                algorithm = BoostedPolicyLearning(domain_train, exp_params["algorithm"],
                    tmp_dir_name)
            algorithm.train(dataset_expert, dataset_random)
        else:
            assert False

        if exp_params["evaluation"]["solver"] == "percentage":
            if exp_params["algorithm"]["output"] == "reward":
                results = evaluate_percentage_reward(domain_test, algorithm.reward,
                    reward_test, exp_params["evaluation"])
            else:
                results = evaluate_percentage_policy(domain_test, algorithm.policy,
                    reward_test, exp_params["evaluation"])


        elif exp_params["evaluation"]["solver"] == "planner":
                assert exp_params["algorithm"]["output"] == "reward"
                assert exp_params["algorithm"]["name"] == "RCSI"
                assert exp_params["algorithm"]["nb_trees_reward"] == 1
                # results = planner_evaluate(domain_test, target_policy_test, reward_test,
                #     exp_directory, 0, 1,
                #     exp_params["evaluation"])
                results = planner_evaluate(domain_test, algorithm.learned_policy, reward_test,
                    exp_directory, algorithm._reward_trees[0].min, algorithm._reward_trees[0].max,
                    exp_params["evaluation"])

        else:
            if exp_params["algorithm"]["output"] == "reward":
                learned_policy = create_policy(domain_test, algorithm.reward, exp_params["evaluation"])
            elif exp_params["algorithm"]["output"] == "policy":
                learned_policy = algorithm.policy
            results = evaluate(domain_test, target_policy_test, learned_policy, reward_test,
                exp_params["evaluation"])


        print results

        with open(results_file_name, "w") as results_file:
            json.dump(results, results_file)

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        experiment(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[1] == "-f":
        experiment(sys.argv[2], True)        
    else:
        print "Usage : python {} [-f] <directory>".format(sys.argv[0])
