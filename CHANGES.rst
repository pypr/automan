0.5
~~~~

* Release date: still in development.


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
