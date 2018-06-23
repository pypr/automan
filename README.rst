automan: a simple automation framework
--------------------------------------

|Travis Status|  |Appveyor Status|  |Coverage Status|

.. |Travis Status| image:: https://travis-ci.org/pypr/automan.svg?branch=master
    :target: https://travis-ci.org/pypr/automan

.. |Appveyor Status| image:: https://ci.appveyor.com/api/projects/status/82mxewh71wodobdf
    :target: https://ci.appveyor.com/project/prabhuramachandran/automan

.. |Coverage Status| image:: https://codecov.io/gh/pypr/automan/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/pypr/automan


This framework allows you to automate your computational pipelines.
``automan`` is open source and distributed under the terms of the 3-clause BSD
license.

Features
--------

For a set of numerical simulations with a Python script one can:

- run all simulations and produce all figures with one command.
- distribute the simulations on a collection of idle computers.

Installation
-------------

You should be able to install automan using pip_ as::

  $ pip install automan

If you want to run on the bleeding edge, you may also clone this repository,
change directory into the created directory and run either::

  $ python setup.py install

or::

  $ python setup.py develop


.. _pip: https://pip.pypa.io/en/stable/


Documentation
-------------

Complete documentation for this framework is in the form of a paper that is
currently under review, you can see a draft here: https://arxiv.org/abs/1712.04786

The paper motivates and describes the software and how you can use it.

To see a complete example of a research publication using this framework, see
here: https://gitlab.com/prabhu/edac_sph

The ``README.rst`` in that repository documents how to set everything up. The
scripts to look at are in ``common.py`` and ``automate.py``.

A simpler example project which uses automan is here:
https://github.com/mesnardo/automan-example



The package name
----------------

The name automan comes from an old serial with the same name.  Most
other names were taken on pypi.
