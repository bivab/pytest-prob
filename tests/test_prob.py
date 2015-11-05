# -*- coding: utf-8 -*-

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
