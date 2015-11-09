# -*- coding: utf-8 -*-
import os


def prob_plugin_test(f):
    def test_func(testdir):
        testdir.makeconftest('pytest_plugins = "prob"')
        f(testdir)
    return test_func


@prob_plugin_test
def test_simple_predicate(testdir):
    testdir.makefile('.yml', test_truth="""
        test_predicate:
            test: "1=1"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_predicate PASSED',
    ])


@prob_plugin_test
def test_simple_false_predicate(testdir):
    testdir.makefile('.yml', test_truth="""
        test_predicate:
            test: "1 /= 1"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_predicate FAILED',
    ])


@prob_plugin_test
def test_missing_prob(testdir):
    path = os.environ['PATH']
    os.environ['PATH'] = ''
    try:
        testdir.makefile('.yml', test_truth="""
            test_predicate:
                test: "1=1"
        """)
        result = testdir.runpytest('-v')

        result.stdout.fnmatch_lines([
            '*probcli not found in PATH',
        ])
    finally:
        os.environ['PATH'] = path


@prob_plugin_test
def test_truth(testdir):
    testdir.makefile('.yml', test_truth="""
        test_truth:
            test: "TRUE"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_truth PASSED',
    ])
