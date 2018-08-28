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

A simple example
-----------------

In this tutorial we take a rather trivial program to execute just to
illustrate the basic concepts. Our basic program is going to simply calculate
the square of a number passed to it on the command line. Here is how the code
looks:

.. literalinclude:: ../../examples/tutorial/square.py


You can execute this script like so::

  $ python square.py 2.0
  2.0 4.0

Yay, it works!

.. note::

    If you want to run these examples, they are included along with the
    example files in the automan source code. The files should be in
    ``examples/tutorial`` (`Browse online
    <https://github.com/pypr/automan/tree/master/examples/tutorial>`_).

This example does not produce any output files and doesn't really take any
configuration arguments. So we don't really need to do much about this.

Now let us say we want to automate the execution of this script with many
different arguments, let us say 2 different values for now (we can increase it later).

We can now do this with automan. First create a simple script for this, we
could call it ``automate1.py`` (this is just a convention, you could call it
anything you want).  The code is as shown below:

.. literalinclude:: ../../examples/tutorial/automate1.py
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

.. literalinclude:: ../../examples/tutorial/automate2.py
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

.. literalinclude:: ../../examples/tutorial/automate3.py
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

.. note::
   This example requires that you have matplotlib_ and NumPy_ installed.


.. _NumPy: https://www.numpy.org/
.. _matplotlib: https://matplotlib.org/


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


Doing things a bit better
----------------------------

The previous section demonstrated the basic ideas so you can get started
quickly. Our example problem was very simple and only produced command line
output. Our next example is a simple problem in the same directory called
``powers.py``. This problem is also simple but supports a few command line
arguments and is as follows:

.. literalinclude:: ../../examples/tutorial/powers.py
   :linenos:

Again, the example is very simple, bulk of the code is parsing command line
arguments. There are three arguments the code can take:

- ``--power power`` specifies the power to be computed.
- ``--max`` specifies the largest integer in sequence whose power is to be
  computed
- ``--output-dir`` is the directory where the output should be generated.

When executed, the script will create a ``results.npz`` file which contains
the results stored as NumPy_ arrays. This example also requires that
matplotlib_ and NumPy_ be installed.  Let us run the code::

  $ python powers.py

  $ ls results.npz
  results.npz

  $ python powers.py --power 3.5

On a Python interpreter we can quickly look at the results::

  $ python

  >>> import numpy as np
  >>> data = np.load('results.npz')
  >>> data['x']
  >>> data['y']

This looks about right, so let us move on to see how we can automate running
several cases of this script in a better way than what we had before. We will
continue to automate the previous ``squares.py`` script. This shows you how
you can use automan incrementally as you add more cases. We only show the
lines that are changed and do not reproduce the ``Squares`` problem class in
the listing below.


.. literalinclude:: ../../examples/tutorial/automate4.py
   :lines: 31-
   :lineno-match:

To see the complete file see `automate4.py
<https://github.com/pypr/automan/tree/master/examples/tutorial>`_. The key
points to note in the code are the following:

- As before ``get_name()`` simply returns a convenient name where the outputs
  will be stored.
- A new ``setup()`` method is used and this creates an instance attribute
  called ``self.cases`` which is a list of cases we wish to simulate. Instead
  of using strings in the ``get_commands`` we simply setup the ``cases`` and
  no longer need to create a ``get_commands``. We discuss ``Simulation``
  instances in greater detail below.
- The ``run()`` method is similar except it uses the ``cases`` attribute and
  some conveniences of the simulation objects for convenience.


The ``Simulation`` instances we create are more general purpose and are very
handy. A simulation instance's first argument is the the output directory and
the second is a basic command to execute. It takes a third optional argument
called ``job_info`` which specifies the number of cores and threads to use and
we discuss this later. For now let us ignore it. In addition any keyword
arguments one passes to this are automatically converted to command line
arguments. Let us try to create one of these on an interpreter to see what is
going on::

  >>> from automan.api import Simulation
  >>> s = Simulation(root='some_output/dir/blah',
  ...                base_command='python powers.py', power=3.5)
  >>> s.name
  'blah'
  >>> s.command
  'python powers.py --power=3.5'
  >>> s.params
  {'power': 3.5}

Notice that the name is simply the basename of the root path. You will see
that additional keyword argument ``power=3.5`` is converted to a suitable
command line argument. This is done by the
``Simulation.get_command_line_args`` method and can be overridden if you wish
to do something different. The ``Simulation.params`` attribute simply stores
all the keyword arguments so you could use it later while post-processing.

Now we want that each execution of this command produces output into the
correct directory. We could either roll this into the ``base_command``
argument by passing the correct output directory or there is a nicer way to do
this using the magic ``$output_dir`` argument that is automatically set the
output directory when the command is executed, for example::

  >>> from automan.api import Simulation
  >>> s = Simulation(root='some_output/dir/blah',
  ...                base_command='python powers.py --output-dir $output_dir', power=3.5)
  >>> s.name
  >>> s.command
  'python powers.py --output-dir $output_dir --power=3.5'

Note that the magic variable is not substituted at this point but later when
the program is about to be executed.

Given these details, the code in the ``run`` method should be fairly
straightforward to understand. Note that this organization of our code has
made us maximize reuse of our plotting code. The ``case.params`` attribute is
convenient when post-prprocessing. One can also filter the cases using the
``filter_cases`` function that is provided by ``automan``. We discuss this
later.

The last change to note is that we add the ``Powers`` class to the
``Automator``'s ``all_problems`` and we are done.Let us now run this::

  $ python automate4.py
  6 tasks pending and 0 tasks running
  ...
  Finished!

This only executes the new cases from the ``Powers`` class and makes the plot
in ``manuscript/figures/powers/powers.pdf``.

Using ``Simulation`` instances allows us to parametrize simulations with the
keyword arguments. In addition, it is handy while post-processing. We can also
subclass the ``Simulation`` instance to customize various things or share
code.

There are a few more conveniences that automan provides that are useful while
post-processing and these are discussed below.


Filtering and comparing cases
------------------------------

.. py:currentmodule:: automan.automation

``automan`` provides a couple of handy functions to help filter the different
cases based on the parameters or the name of the cases. One can also make
plots for a collection of cases and compare them easily.

- The :py:func:`filter_cases` function takes a sequence of cases
  and any additional keyword arguments with parameter values and filters out
  the cases having those parameter values. For example from our previous
  example in the ``Powers`` class, if we do the following::

   filtered_cases = filter_cases(cases, power=2)

  will return a list with a single case which uses ``power=2``. This is very
  handy. This function can also be passed a callable which returns ``True``
  for any acceptable case.  For example::

    filter_cases(cases, lambda x: x.params['power'] % 2)

  will return all the cases with odd powers.

- The :py:func:`filter_by_name` function filters the cases whose
  names match the list of names passed.  For example::

    filter_by_name(cases, ['1', '4'])

  will return the two simulations whose names are equal to ``'1'`` or ``'4'``.

- The :py:func:`compare_runs` function calls a method or callable
  with the given cases. This is very handy to make comparison plots.

With this information you should be in a position to automate your
computational simulations and analysis.

Next we look at setting up additional remote computers on which we can execute
our computations.
