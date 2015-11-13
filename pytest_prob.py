# -*- coding: utf-8 -*-

import pytest
import yaml
import pexpect
from subprocess import call
from io import BytesIO
import re
import os


def pytest_addoption(parser):
    group = parser.getgroup('prob')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default=2015,
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo

def pytest_collectstart(collector):
    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        prob = os.path.join(path, 'probcli')
        if os.path.isfile(prob):
            return
    else:
        pytest.fail("probcli not found in PATH")

def pytest_ignore_collect(path, config):
    return path.ext != ".yml"


def pytest_collect_file(path, parent):
    if not path.basename.startswith('test_'):
        return
    if path.ext == ".yml":
        return BTestFile(path, parent=parent)


class BTestFile(pytest.File):
    def __init__(self, fspath, parent=None, config=None, session=None):
        super(BTestFile, self).__init__(fspath, parent, config, session)
        self.name = self.fspath.purebasename
        self.raw = yaml.safe_load(self.fspath.open())

    def collect(self):
        if not self.raw:
            from warnings import warn
            warn(self.name + ' is empty')
            return

        for k,v in self.raw.items():
            if not k.startswith('test_'):
                continue
            assert 'flags' not in v
            test = v.get('test', '1=1')
            yield BItem(k, test, extra=v, parent=self)

    def setup(self):
        if 'machine' not in self.raw:
            # XXX print a warning
            print("machine not provided in test")
        self.machine = self.raw.get('machine', '')
        self.flags = self.raw.get('flags', '')

        if 'setup'  in self.raw:
            setup = self.raw['setup']
            env = os.environ.copy()
            if isinstance(setup, dict):
                cmd=setup['cmd'].split()
                if 'env' in setup:
                    for k,v in (i.split('=') for i in setup['env'].split()):
                        env[k] = v
            else:
                cmd=self.raw['setup'].split()
            call(cmd, env=env)

        self.process = pexpect.spawn('probcli -repl ' + self.flags + ' ' + self.machine)
        self.process.expect('>>>')

    def teardown(self):
        if 'teardown' not in self.raw:
            return
        cmd=self.raw['teardown'].split()
        return call(cmd)


class BItem(pytest.Item):

    def __init__(self, name, test, extra=None, parent=None, config=None, session=None):
        assert name.startswith('test_')
        super(BItem, self).__init__(name, parent, config, session)

        test = test.replace('\n', ' ')
        self.test = test
        #
        if extra is None:
            extra = {}
        self.extra = extra

    def _skip(self, skip):
        if skip:
            if isinstance(skip, str):
                raise pytest.skip(self.name + ': ' + skip)
            raise pytest.skip(self.name)

    def runtest(self):
        # 
        pattern = ['false/0,false_after_expansion/0,unknown/0,unknown_after_expansion/0', 'Predicate.*is TRUE', 'Expression Value =.*\nTRUE', 'Predicate is FALSE', 'Expression Value =\nFALSE', pexpect.TIMEOUT, pexpect.EOF]
        self._skip(self.extra.get('skip', False))
        #
        cli = self.parent.process
        #
        log = BytesIO()
        cli.logfile_read = log
        #
        cli.sendline(self.test)
        #
        timeout = self.extra.get('timeout', 5)
        result = cli.expect(pattern, timeout=timeout)
        #
        if result > 2: # index in the pattern list above.
                       # result < 2 indicates successful execution
            raise BTestException(self, log.getvalue())

    def __repr__(self):
        return "{name}: flags:{flags}|tests:{test}".format(**self.__dict__)

    def repr_failure(self, excinfo):
        return repr(self)+'\n'+excinfo.value.message

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, BTestException):
            errormsg = excinfo.value.result.decode()
            errormsg = errormsg.splitlines()

            return "\n".join(
                    ["Test execution failed",
                     "Failed: {}".format(excinfo.value.item.name)
                    ]
                    + errormsg)
        return super(BItem, self).repr_failure(excinfo)

    def reportinfo(self):
        return self.fspath, 0, "[probcli] %s" % self.name

    _handling_traceback = False


class BTestException(Exception):
    def __init__(self, item, result):
        self.item = item
        self.result = result
