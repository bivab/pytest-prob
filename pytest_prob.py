# -*- coding: utf-8 -*-

import pytest
import yaml
import pexpect
from subprocess import call
from io import BytesIO
import os


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

    def _warn(self, msg):
        args = dict(code="PROB", message=msg,
                    nodeid=self.nodeid, fslocation=self.nodeid)
        self.ihook.pytest_logwarning.call_historic(kwargs=args)

    def collect(self):
        if not self.raw:
            self._warn(self.name + ' is empty')
            return

        for k, v in self.raw.items():
            if not k.startswith('test_'):
                continue
            assert 'flags' not in v
            test = v.get('test', '1=1')
            yield BItem(k, test, extra=v, parent=self)

    def setup(self):
        if 'machine' not in self.raw:
            self._warn("Machine not provided in test")
        self.machine = self.raw.get('machine', '')
        self.flags = self.raw.get('flags', '')
        self.timeout = self.raw.get('load_timeout', 30)

        if 'setup' in self.raw:
            setup = self.raw['setup']
            if not isinstance(setup, list):
                setup = [setup]
            for s in setup:
                env = os.environ.copy()
                if isinstance(s, dict):
                    cmd = s['cmd'].split()
                    if 'env' in s:
                        for k, v in (i.split('=') for i in s['env'].split()):
                            env[k] = v
                else:
                    cmd = s.split()
                call(cmd, env=env)

        self.process = pexpect.spawn('probcli -repl ' + self.flags + ' ' + self.machine)
        self.process.expect('>>>', timeout=self.timeout)

    def teardown(self):
        if 'teardown' not in self.raw:
            return
        teardown = self.raw['teardown']
        if not isinstance(teardown, list):
            teardown = [teardown]
        for s in teardown:
            cmd = s.split()
            call(cmd)


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
        pattern = ['false/0,false_after_expansion/0,unknown/0,unknown_after_expansion/0',
                   'Predicate.+is.+TRUE', 'Expression Value =.*\nTRUE',
                   'Predicate.+is.+FALSE', 'Expression Value =.*\nFALSE',
                   pexpect.TIMEOUT, pexpect.EOF]
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
        # index in the pattern list above. result < 3 indicates successful
        # execution
        if result > 2:
            raise BTestException(self, log.getvalue()[-1000:])

    def __repr__(self):
        return "{name}: flags:{flags}|tests:{test}".format(**self.__dict__)

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, BTestException):
            errormsg = excinfo.value.result.decode()
            errormsg = errormsg.splitlines()
            failuremsg = "Failed: {}".format(excinfo.value.item.name)
            return "\n".join(["Test execution failed", failuremsg] + errormsg)

        return super(BItem, self).repr_failure(excinfo)

    def reportinfo(self):
        return self.fspath, 0, "[probcli] %s" % self.name

    _handling_traceback = False


class BTestException(Exception):
    def __init__(self, item, result):
        self.item = item
        self.result = result
