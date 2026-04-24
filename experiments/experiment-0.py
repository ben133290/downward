#! /usr/bin/env python3

import os
import custom_parser

from lab.environments import LocalEnvironment, BaselSlurmEnvironment
from lab.experiment import Experiment

from downward.experiment import FastDownwardExperiment

import common_setup
from common_setup import IssueConfig, IssueExperiment

DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.environ["DOWNWARD_REPO_ISSUE1146"]
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISIONS = ["main", "issue1146"]
BUILDS = ["release"]
CONFIG_NICKS = [
    ("astar-blind", ["--search", "astar(blind())"]),
]
CONFIGS = [
    IssueConfig(
        config_nick,
        config,
        build_options=[build],
        driver_options=['--search-time-limit', '5m', "--build", build])
    for build in BUILDS
    for config_nick, config in CONFIG_NICKS
]

SUITE = list(set(common_setup.EXAMPLE_SUITE))
ENVIRONMENT = BaselSlurmEnvironment(
    partition="infai_2",
    email="ben.heuser@unibas.ch",
    export=["PATH"],
)

# if common_setup.is_test_run():
#    SUITE = IssueExperiment.DEFAULT_TEST_SUITE
#    ENVIRONMENT = LocalEnvironment(processes=4)
#
#
print(BENCHMARKS_DIR)
print(REPO_DIR)

exp = FastDownwardExperiment(path=REPO_DIR, environment=ENVIRONMENT)

exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(exp.PLANNER_PARSER)
# exp.add_parser(custom_parser.get_parser())

exp.add_step('build', exp.build)
exp.add_step('start', exp.start_runs)
exp.add_step('parse', exp.parse)
exp.add_fetcher(name='fetch')

exp.add_algorithm("base", REPO_DIR, REVISIONS, ["--translate-options", "--eliminate-disjunctions=none", "--search-options"], build_options=None, driver_options=None)

#exp.add_absolute_report_step(attributes=exp.DEFAULT_TABLE_ATTRIBUTES + ["search_start_time"])
# exp.add_comparison_table_step(attributes=exp.DEFAULT_TABLE_ATTRIBUTES + ["search_start_time"])
# exp.add_scatter_plot_step(relative=True, attributes=["total_time", "memory", "search_start_time"])

exp.run_steps()
