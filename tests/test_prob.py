# -*- coding: utf-8 -*-
import os

TEST_MACHINE = os.path.join(os.path.dirname(__file__), 'TestMachine.mch')

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


@prob_plugin_test
def test_setup(testdir):
    path = testdir.tmpdir.join('setup.txt')
    testdir.makefile('.yml', test_setup="""
        setup: "touch {}"
        test_foo:
            test: "TRUE"
    """.format(path))
    result = testdir.runpytest()
    assert path.exists()


@prob_plugin_test
def test_teardown(testdir):
    path = testdir.tmpdir.join('TestMachine.mch')
    testdir.makefile('.yml', test_teardown="""
        setup: "cp  {source} {target}"
        teardown: "rm {target}"
        machine: {target}
        test_subset:
            test: "{{aa, bb}} <: TEST_SET"
    """.format(source=TEST_MACHINE, target=path))
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_subset PASSED',
    ])
    assert not path.exists()


@prob_plugin_test
def test_machine(testdir):
    testdir.makefile('.yml', test_machine="""
        machine: {}
        test_member:
            test: "aa : TEST_SET"
            """.format(TEST_MACHINE))
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_member PASSED',
    ])


@prob_plugin_test
def test_flags(testdir):
    testdir.makefile('.yml', test_machine="""
        machine: {}
        flags: -init
        test_constant:
            test: "cc = 23"
            """.format(TEST_MACHINE))
    result = testdir.runpytest('-v')

    result.stdout.fnmatch_lines([
        '*::test_constant PASSED',
    ])

@prob_plugin_test
def test_skip(testdir):
    testdir.makefile('.yml', test_machine="""
        test_skip:
            skip: lorem ipsum
            test: FALSE
            """)
    result = testdir.runpytest('-v')
    result2 = testdir.runpytest('-rs')

    result.stdout.fnmatch_lines([
        '*::test_skip SKIPPED',
    ])

    result2.stdout.fnmatch_lines([
        '*test_skip: lorem ipsum',
    ])
