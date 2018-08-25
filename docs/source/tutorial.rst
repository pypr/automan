Tutorial
=========

Automan is best suited for numerical computations that take a lot of time to
run. It is most useful when you have to manage the execution of many of these
numerical computations. Very often one needs to process the output of these
simulations to either compare the results and then assemble a variety of plots
or tables for a report or manuscript.

The numerical simulations can be in the form of any executable code, either in
the form of a binary or a script. In this tutorial we will assume that the
programs being executed are in the form of Python scripts.

There are three general recommendations we make for your numerical programs to
be able to use automan effectively.

1. They should be configurable using command line arguments.
2. They should generate their output files into a directory specified on the
   command line.
3. Any post-processed data should be saved into an easy to load datafile to
   facilitate comparisons with other simulations.

None of these is strictly mandatory.

Step 1: a simple example
-------------------------

In this tutorial we take a rather trivial program to execute just to
illustrate the basic concepts. Our basic program is going to simply calculate
the square of a number passed to it on the command line. Here is how the code
looks:

.. literalinclude:: ../../examples/step1/square.py


You can execute this script like so::

  $ python square.py 2.0
  2.0 4.0

Yay, it works!

.. note::

    If you want to run these examples, they are included along with the
    example files in the automan source code. The files should be in
    ``examples/step1`` (`Browse online
    <https://github.com/pypr/automan/tree/master/examples/step1>`_).

This example does not produce any output files and doesn't really take any
configuration arguments. So we don't really need to do much about this.

Now let us say we want to automate the execution of this script with many
different arguments, let us say 2 different values for now (we can increase it later).

We can now do this with automan. First create a simple script for this, we
could call it ``automate1.py`` (this is just a convention, you could call it
anything you want).  The code is as shown below:

.. literalinclude:: ../../examples/step1/automate1.py
   :linenos:


Note the following:

- The ``Squares`` class derives from :py:class:`automan.automation.Problem`.
  This encapsulates all the simulations where we wish to find the square of
  some number.
- The ``get_name`` method returns a subdirectory for all the outputs of this
  problem.
- The ``get_commands`` returns a list of tuples of the following form,
  ``(directory_name, command, job_info)``. In this case we don't pass any job
  information and we'll get to this later. Notice that the two commands
  specified are essentially what we'd have typed on the terminal.
- The ``run`` command does nothing much except create a directory. For now let
  us leave this alone.


Let us execute this to see what it does::

  $ python automate1.py

  Enter PySPH source directory (empty for none):
  Invalid pysph directory, please edit config.json.
  Writing config.json
  4 tasks pending and 0 tasks running

  Running task <automan.automation.CommandTask object at 0x10628d978>...
  Starting worker on localhost.
  Job run by localhost
  Running /path/to/bin/python square.py 2

  Running task <automan.automation.CommandTask object at 0x10628d9b0>...
  Job run by localhost
  Running /path/to/bin/python square.py 1
  2 tasks pending and 2 tasks running
  Running task <automan.automation.SolveProblem object at 0x10628d940>...

  Running task <automan.automation.RunAll object at 0x10628d908>...
  Finished!

It will first ask you about the PySPH sources and you can safely just press
enter here. Once that is done it should try to execute the various commands
and be done.

.. note::
   This will change later and it will not prompt you for anything.

Let us see the output directories::

  $ tree
  .
  ├── automate1.py
  ├── config.json
  ├── manuscript
  │   └── figures
  │       └── squares
  ├── outputs
  │   └── squares
  │       ├── 1
  │       │   ├── job_info.json
  │       │   ├── stderr.txt
  │       │   └── stdout.txt
  │       └── 2
  │           ├── job_info.json
  │           ├── stderr.txt
  │           └── stdout.txt
  └── square.py

  7 directories, 9 files

Let us summarize what just happened:

- The two commands we asked for were executed and the respective outputs of
  each invocation were placed into ``outputs/squares/1`` and
  ``outputs/squares/2``. Notice that there are ``stdout.txt, stderr.txt`` and
  a ``job_info.json`` file here too.
- A manuscript directory called ``manuscript/figures/squares`` is created.
- There is also a new ``config.json`` that we can safely ignore for now.

Let us see the contents of the files in the outputs directory::

  $ cat outputs/squares/1/stdout.txt
  1.0 1.0

  $ cat outputs/squares/1/job_info.json
  {"start": "Fri Aug 24 01:11:46 2018", "end": "Fri Aug 24 01:11:46 2018", "status": "done", "exitcode": 0, "pid": 20381}

As you can see, the standard output has the output of the command. The
``job_info.json`` has information about the actual execution of the code. This
is very useful in general.

Thus automan has executed the code, organized the output directories and
collected the standard output and information about the execution of the
tasks.

Now, let us run the automation again::

  $ python automate1.py
  0 tasks pending and 0 tasks running
  Finished!

It does not re-run the code as it detects that everything is complete.

Adding some post-processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let us say we want to create a plot that either compares the individual runs
or assembles the runs into a single plot or collects the data into a single
file. We can easily do this by adding more code into the ``run`` method of our
``Squares`` class. Let us also add a couple of more computations.

.. literalinclude:: ../../examples/step1/automate2.py
   :linenos:

Let us examine this code a little carefully:

- In ``get_commands``, we have simply added two more cases.

- In ``run``, we have added some simple code to just iterate over the 4
  directories we should have and then read the standard output into a list and
  finally we write that out into an ``output.txt`` file.

- We also moved the ``automator`` object creation and execution so we can
  import our ``automate2.py`` script if we wish to.

The two new methods you see here are ``self.input_path(...)`` which makes it
easy to access any paths inside the simulation directories and the
``self.output_path(...)`` which does the same but inside the output path. Let
us see what these do, inside the directory containing the ``automate2.py`` if
you start up a Python interpreter (IPython_ would be much nicer), you can do
the following::

  >>> import automate2
  >>> squares = automate2.Squares(
  ...    simulation_dir='outputs',
  ...    output_dir='manuscript/figures/'
  ... )

  >>> squares.input_path('1')
  'outputs/squares/1'

  >>> squares.input_path('1', 'stdout.txt')
  'outputs/squares/1/stdout.txt'

  >>> squares.output_path('output.txt')
  'manuscript/figures/squares/output.txt'

.. _IPython: ://ipython.org/

As you can see, these are just conveniences for finding the input file paths
and the output file paths.  Now let us run this new script::

  $ python automate2.py
  0 tasks pending and 0 tasks running
  Finished!

Whoa! That doesn't seem right? What happens is that since the last time we ran
the automate script, it created the output, it assumes that there is nothing
more to do as the final result (the ``manuscript/figures/squares``) was
successfully created so it does not run anything new.  If you do this::

  $ python automate2.py -h

You'll see an option ``-f`` which basically redoes the post-processing by
removing any old plots, so let us try that::

  $ python automate2.py -f
  4 tasks pending and 0 tasks running
  ...
  Finished!

Now it actually ran just the new simulations (you can see the commands in the
output it prints), it will not re-run the already executed cases. Now let us
see if the output is collected::

  $ cat manuscript/figures/squares/output.txt
  [['1.0', '1.0'], ['2.0', '4.0'], ['3.0', '9.0'], ['4.0', '16.0']]

So what automan did was to execute the newly added cases and then executed our
post-processing code in the ``run`` method to produce the output.

Building on this we have a slightly improved script, called ``automate3.py``,
which makes a plot:

.. literalinclude:: ../../examples/step1/automate3.py
   :linenos:

This version simplifies the command generation by using a list-comprehension,
so reduces several lines of code. It then makes a matplotlib plot with the
collected data.  Let us run this::

  $ python automate3.py -f
  5 tasks pending and 0 tasks running
  ...
  Finished!

  $ ls manuscript/figures/squares/
  squares.pdf


As you can see, the old ``output.txt`` is gone and our plot is available.

If you wanted to change the plotting style in any way, you can do so and
simply re-run ``python automate3.py -f`` and it will only regenerate the final
plot without re-executing the actual simulations.

So what if you wish to re-run any of these cases? In this case you will need
to manually remove the particular simulation (or even all of them). Let us try
this::

  $ rm -rf outputs/squares/3

  $ python automate3.py -f
  3 tasks pending and 0 tasks running
  ...
  Finished!

It will just run the missing case and re-generate the plots.

While this may not seem like much, we've fully automated our simulation and
analysis.


Step 2: doing things a bit better
---------------------------------

- Use ``Simulation`` instances
- Show how to parametrize things.
- Show how to filter and compare cases.

XXX
