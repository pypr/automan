0.6
~~~~

* Release date: 9th July, 2024
* Fix virtualenv download link.
* Fix tests to run on Python 3.12 and to run from an installation.
* Fix bug with job status not working for killed processes.
* Seven PRs were merged.

0.5
~~~~

* Release date: 4th November, 2021
* Provide some handy functions to `generate many simulations from parameters
  <https://automan.readthedocs.io/en/latest/tutorial.html#generating-simulations-for-parameter-sweeps>`_.
* Add ability to `add arbitrary tasks/problems to the automator
  <https://automan.readthedocs.io/en/latest/tutorial.html#adding-arbitrary-tasks>`_
  using the ``add_task`` method.
* Allow specification of negative ``n_core`` and ``n_thread`` for the job
  information. This is documented in the section on `additional computational
  resources
  <https://automan.readthedocs.io/en/latest/tutorial.html#using-additional-computational-resources>`_.
* Improve ability to customize the styles used with ``compare_runs``.
* Add a ``--rm-remote-output`` argument to the command line arguments.
* Add a convenient ``FileCommandTask``.
* Improve ability to customize command line arguments.
* Fix issue with too many processes and open files.
* Fix an issue with command tasks executing on a remote host and waiting.
* Use github actions for tests.
* 12 PRs were merged.


0.4
~~~~

* Release date: 26th November, 2018.
* Support for inter Problem/Simulation/Task dependencies.
* Print more useful messages when running tasks.
* Fix bug with computing the available cores.
* Improve handling of cases when tasks fail with errors.
* Fix a few subtle bugs in the task runner.
* Minor bug fixes.


0.3
~~~~

* Release date: 5th September, 2018.
* Complete online documentation and examples.
* Much improved and generalized cluster management with support for conda and
  edm in addition to virtualenvs.
* Support multiple projects that use different bootstrap scripts.
* Better testing for the cluster management.
* Do not rewrite the path to python executables and run them as requested by
  the user.
* Removed any lingering references or use of ``pysph``.
* Change the default root to ``automan`` instead of ``pysph_auto``.
* Support filtering cases with a callable.
* Fix bug where a simulation with an error would always be re-run.
* Fix bug caused due to missing ``--nfs`` option to automator CLI.


0.2
~~~~

* Release date: 28th August, 2017.
* First public release of complete working package with features described in
  the paper.
