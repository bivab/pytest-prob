pytest-prob
===========

.. image:: https://travis-ci.org/bivab/pytest-prob.svg?branch=master
    :target: https://travis-ci.org/bivab/pytest-prob
    :alt: See Build Status on Travis CI

Pytest plug-in to run B predicates and expressions as tests on `ProB`_.

*Current Version*: 0.4.0-dev

----

About
-----

Evaluate B predicates and expressions as unit tests using pytest. Tests are
defined in YAML files and can be executed in the context of a B machine or
independently.

An example test file might look like this: ::

  machine: TestMachine.mch
  setup: cp tmp/data.mch data.mch
  teardown: rm data.mch

  test_one:
    test: "1 > 0"

On the top level the following keys are supported. All keys are optional.

- *machine:* B machine to be loaded as context for the tests.
- *load_timeout*: The number of seconds after which loading the B machine for the test is considered as failed.
- *flags:* command line flags passed to the ProB cli.
- *setup:* shell command or list of commands to run before starting the tests.
- *teardown:* shell command or list of commands run after executing the tests.

Declaring tests
~~~~~~~~~~~~~~~

Test are defined using keys that start with ``test\_``.  The test body is defined using a ``test`` sub-key.

- *test:* code to be evaluated for each test.
- *skip:* if present the test is skipped, the value is used as the reason for skipping the test.
- *timeout:* the number of seconds after which the test is considered as failed in case it has not terminated by then. 

Example
~~~~~~~

::

  machine: TestMachine.mch
  flags: -p CLPFD TRUE
  load_timeout: 20
  setup: cp tmp/data.mch data.mch
  teardown: rm data.mch

  test_one:
    test: "1 > 0"

  test_long:
    timeout: 50
    test: "long_running_computation()"

  test_condition:
    skip: Updated changed API
    test: "calling_something[{1}]"

Testing
-------

Tests can be run with `tox`_. The tests expect to find a probcli binary in your
``$PATH`` variable. use ``bin/prepare_testing.sh`` to download and unpack ProB
for you platform.

Requirements
------------

See `requirements.txt`_ for runtime dependencies and `requirements/dev.txt`_ for development dependencies.

Installation
------------

You can install "pytest-prob" via `pip`_ from `github`_::

    $ pip install git+https://github.com/bivab/pytest-prob.git

Or from source by running::

    $ python setup.py install

License
-------

Distributed under the terms of the `ISC`_ license.


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`ProB`: http://www3.hhu.de/stups/prob/
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`file an issue`: https://github.com/bivab/pytest-prob/issues
.. _`ISC`: LICENSE
.. _`requirements.txt`: requirements.txt
.. _`requirements/dev.txt`: requirements/dev.txt
.. _`github`: https://github.com/bivab/pytest-prob
