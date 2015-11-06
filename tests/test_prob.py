# -*- coding: utf-8 -*-
import os

def test_simple_predicate(testdir):
    testdir.makeconftest('pytest_plugins = "prob"')
    testdir.makefile('.yml', test_truth="""
        test_predicate:
            test: "1=1"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_predicate PASSED',
    ])


def test_simple_false_predicate(testdir):
    testdir.makeconftest('pytest_plugins = "prob"')
    testdir.makefile('.yml', test_truth="""
        test_predicate:
            test: "1 /= 1"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_predicate FAILED',
    ])


def test_missing_prob(testdir):
    path = os.environ['PATH']
    os.environ['PATH'] = ''
    try:
        testdir.makeconftest('pytest_plugins = "prob"')
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

def test_truth(testdir):
    testdir.makeconftest('pytest_plugins = "prob"')
    testdir.makefile('.yml', test_truth="""
        test_truth:
            test: "TRUE"
    """)
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_truth PASSED',
    ])
