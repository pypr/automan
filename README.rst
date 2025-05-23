automan: a simple automation framework
--------------------------------------

|CI Status|  |Coverage Status|  |Documentation Status|

.. |CI Status| image:: https://github.com/pypr/automan/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/pypr/automan/actions

.. |Coverage Status| image:: https://codecov.io/gh/pypr/automan/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/pypr/automan

.. |Documentation Status| image:: https://readthedocs.org/projects/automan/badge/?version=latest
  :target: https://automan.readthedocs.io/en/latest/?badge=latest


This framework allows you to automate your computational pipelines.
``automan`` is open source and distributed under the terms of the 3-clause BSD
license.

Features
--------

It is designed to automate the drudge work of managing many numerical
simulations. As an automation framework it does the following:

- helps you organize your simulations.
- helps you orchestrate running simulations and then post-processing the
  results from these.
- helps you reuse code for the post processing of your simulation data.
- execute all your simulations and post-processing with one command.
- optionally distribute your simulations among other computers on your
  network.

This greatly facilitates reproducibility. Automan is written in pure Python
and is easy to install.


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

Documentation for this project is available at https://automan.rtfd.io

There is a paper on ``automan`` that motivates and describes the software:

- Prabhu Ramachandran, "automan: A Python-Based Automation Framework for
  Numerical Computing," in Computing in Science & Engineering, vol. 20, no. 5,
  pp. 81-97, 2018. `doi:10.1109/MCSE.2018.05329818
  <http://doi.ieeecomputersociety.org/10.1109/MCSE.2018.05329818>`_

A draft of this paper is available here: https://arxiv.org/abs/1712.04786

There are more than ten research publications that use automan to automate the
entire paper. To see complete examples of these research publications using
this framework, see the following:

- The EDAC-SPH paper: https://gitlab.com/prabhu/edac_sph
- All the repositories/papers here: https://gitlab.com/pypr
- ML/AI related research paper using automan: https://github.com/nn4pde/SPINN

The ``README.rst`` in these repositories will document how to set everything
up. The automation script will typically be called ``automate.py``.

A simpler example project which uses automan is here:
https://github.com/mesnardo/automan-example



The package name
----------------

The name automan comes from an old serial with the same name.  Most
other names were taken on pypi.
