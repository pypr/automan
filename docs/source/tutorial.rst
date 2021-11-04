A tutorial on using ``automan``
================================

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

None of these is strictly mandatory but we strongly recommend doing it this
way.

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

  Writing config.json
  4 tasks pending and 0 tasks running

  Running task CommandTask with output directory: 2 ...
  Starting worker on localhost.
  Job run by localhost
  Running python square.py 2

  Running task CommandTask with output directory: 1 ...
  Job run by localhost
  Running python square.py 1
  2 tasks pending and 2 tasks running
  Running task Problem named squares...

  Running task <automan.automation.RunAll object at 0x10628d908>...
  Finished!

So the script executes and seems to have run the requested computations. Let
us see the output directories::

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
----------------------------

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

The two new methods you see here are ``self.input_path(...)`` (you could also
use ``self.simulation_path(...)``) which makes it easy to access any paths
inside the simulation directories and the ``self.output_path(...)`` which does
the same but inside the output path. Let us see what these do, inside the
directory containing the ``automate2.py`` if you start up a Python interpreter
(IPython_ would be much nicer), you can do the following::

  >>> import automate2
  >>> squares = automate2.Squares(
  ...    simulation_dir='outputs',
  ...    output_dir='manuscript/figures/'
  ... )

  >>> squares.input_path('1')
  'outputs/squares/1'

  >>> squares.input_path('1', 'stdout.txt')
  'outputs/squares/1/stdout.txt'

  >>> squares.simulation_path('1', 'stdout.txt')
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


The :py:class:`automan.automation.Simulation` instances we create are more
general purpose and are very handy. A simulation instance's first argument is
the the output directory and the second is a basic command to execute. It
takes a third optional argument called ``job_info`` which specifies the number
of cores and threads to use and we discuss this later. For now let us ignore
it. In addition any keyword arguments one passes to this are automatically
converted to command line arguments. Let us try to create one of these on an
interpreter to see what is going on::

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

Using :py:class:`automan.automation.Simulation` instances allows us to
parametrize simulations with the keyword arguments. In addition, it is handy
while post-processing. We can also subclass the ``Simulation`` instance to
customize various things or share code.

There are a few more conveniences that automan provides that are useful while
post-processing and these are discussed below.


Generating simulations for parameter sweeps
-------------------------------------------

.. py:currentmodule:: automan.utils

.. versionadded:: 0.5

One of the primary advantages of automan is the ease with which one can
perform parameter sweeps. The biggest difficulty in this case is to generate
all the simulations easily from a set of parameters of interest. ``automan``
provides a few convenient utility functions that make this very easy to do.

We explain these functions with a simple example. Let us say we wish to
execute a simulation with two values of a parameter (``re = 100, 200``), for
two different set of resolutions (``nx = 50, 100``). Normally, one would need
to create the simulations in a for loop. The :py:func:`mdict` function makes
this very easy to do as follows::

  >>> from automan.api import mdict
  >>> opts = mdict(nx=[50, 100], re=[100, 200])
  >>> opts
  [{'nx': 50, 're': 100},
  {'nx': 50, 're': 200},
  {'nx': 100, 're': 100},
  {'nx': 100, 're': 200}]

As you can see this creates a list of dictionaries, each with the required set
of parameters that can be passed to a :py:class:`Simulation` instance. This
expands to any number of parameters. Note that the arguments to ``mdict``
should be sequences which are expanded out as a product.

Often you have a set of parameters that go together. For example, if we have
two optimizers, say ``Adam`` and ``LBFGS`` and then you have to choose
different learning rates for each, you can do the following::

  >>> opts2 = mdict(optimizer=['Adam'], lr=[1e-2, 1e-3]) + \
  ...         mdict(optimizer=['LBFGS'], lr=[1.0, 0.1])

Now, let us say we want to take the product of the ``opts`` above (for the
``nx, re`` values) along with the ``opts2`` above, we can easily do this using
the :py:func:`dprod` like so::

  >>> from automan.api import dprod
  >>> options = dprod(opts, opts2)
  >>> type(options)
  list
  >>> len(options)
  16

This will be the product of all the options and will produce 16 different
cases as a list of dictionaries. Notice that this just takes 4 lines of code.
We can use these list of dictionaries to create the necessary simulations
easily. For example::

  cases = [
     Simulation(
         root=self.input_path('unique_directory_name'),
         base_command='python code.py',
         **kw
     )
     for kw in options
  ]

With that you can create a huge number of simulations. The only issue here is
that you need to create a unique directory name to dump the output of each
simulation into. The :py:func:`opts2path` function provides a very convenient
way to do this. It takes a dictionary and optional keyword arguments to
convert the set of parameters in the dictionary into a string for use as a
unique directory. Here is a quick example::

  >>> from automan.api import opts2path
  >>> opts2path(dict(x=1, y='hello', z=0.1))
  'x_1_hello_z_0.1'

This renders each parameter out. We can limit the string to only use certain
keys using the ``keys`` keyword argument::

  >>> opts2path(dict(x=1, y='hello', z=0.1), keys=['x'])
  'x_1'

Or we could ``ignore`` some keys::

  >>> opts2path(dict(x=1, y='hello', z=0.1), ignore=['x'])
  'hello_z_0.1'

Or we could map the keys to some other string::

  >>> opts2path(dict(x=1, y='hello', z=0.1), kmap=dict(x='XX'))
  'XX_1_hello_z_0.1'


Using this makes it very easy to generate simulation instances like so::

  cases = [
     Simulation(
         root=self.input_path(opts2path(kw)),
         base_command='python code.py',
         **kw
     )
     for kw in options
  ]

These utility functions therefore make it very easy to easily generate a huge
number of cases. The next section shows you how to filter these cases and then
make comparison plots from these easily.



Filtering and comparing cases
------------------------------

.. py:currentmodule:: automan.utils

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

- The :py:func:`compare_runs` function calls a method or callable with the
  given cases. One can also pass a set of labels which are used to annotate
  the plots made as well as an optional function to compute an exact result.
  This is very handy to make comparison plots. Only if a simulation has a
  particular label will it be used, otherwise it will be ignored. The idea is
  that very often making a comparison plot requires the same kind of plot to
  be made for different simulations. The only thing that changes between these
  is the data, the label used, and the line styles. These can be extracted
  from the cases automatically.

A simple example helps clarify this.  Consider the following::

  class Sim(Simulation):
      def l1_error(self, **kw):
          data = read_data_file(self.input_path('results.dat'))
          plt.plot(data['t'], data['l1err'], **kw)

  class MyProblem(Problem):
      def run(self):
          self.make_output_dir()
          # We assume that self.cases has `Sim` instances
          plt.figure()
          compare_runs(self.cases, 'l1_error', labels=['param1', 'param2'])
          plt.savefig(self.output_path('result.pdf'))
          plt.close()

In this case, we assume that the problem creates a collection of ``Sim``
instances. The ``l1_error`` method defines a common plot method, this could
also be a generic callable which is passed the simulation instance. So the
``compare_runs`` function will loop over all the cases given to it, in the
specified order, and call the ``l1_error`` method/function for each case.
``compare_runs`` also takes a ``styles`` keyword argument that is passed the
sequence of simulations and should return an iterator of any matplotlib style
options. The idea employed here is very general and while the above uses
matplotlib, one could in principle use anything else. See the function
documentation for more information. Here is a short example that demonstrates
how one may use the ``styles`` keyword argument. We look at the default
implementation for the styles. The idea is that for each plot you want a
different plotting style, say a different line style or color or marker. The
default implementation is::

  import itertools as IT

  def styles(sims):
      ls = [dict(color=x[0], linestyle=x[1]) for x in
            IT.product("kbgr", ["-", "--", "-.", ":"])]
      return IT.cycle(ls)

Let us see what this does::

  >>> from automan.utils import styles
  >>> x = styles([])
  >>> next(x)
  {'color': 'k', 'linestyle': '-'}
  >>> next(x)
  {'color': 'k', 'linestyle': '--'}

As you can see it is simply producing a dictionary of keyword arguments that
are used. You can use any kind of arguments you wish. If you prefer to create
more colorful plots you could modify this like so::

  def styles(sims):
      ls = [dict(linestyle=x[0], color=x[1]) for x in
            IT.product(["-", "--", "-.", ":"], 'kbgrycm')]
      return IT.cycle(ls)

This will iterate over the colors and will first loop over the colors and then
the linestyles (try it and see). It is also possible to generate styles that
iterate over different markers for example::

  def mystyles(sims):
      ls = [dict(color=x[1], linestyle='-',
                 marker=x[0], markevery=5) for x in
            IT.product([None, '^', 'o'], 'kbgrcmy')]
      return IT.cycle(ls)

Note that in the above we did not use the passed arguments of the simulations.
We could if we wish, choose to color different simulations based on some
criterion. For example let us say if we want to use a specific color for a
specific value of a parameter (say ``re``), we could do the following::

  def mystyles(sims):
      colors = {100: 'b', 200: 'g', 400: 'r'}
      ls = IT.cycle(["-", "--", "-.", ":"])
      styles = [dict(color=colors[s.params['re']], linestyle=next(ls))
                for s in sims]
      return iter(styles)

Note that here, we use the ``s.params`` attribute for each simulation and set
the color according to this. We return an iterator over the list as expected
by the ``compare_runs`` function. However, we could just return an iterable
like a list or tuple and it would still work, for example::

  def mystyles(sims):
      colors = {100: 'b', 200: 'g', 400: 'r'}
      ls = IT.cycle(["-", "--", "-.", ":"])
      return [dict(color=colors[s.params['re']], linestyle=next(ls))
              for s in sims]

This is easier to write for customized styles especially if you are not
familiar with Python iterators.

You could now use ``compare_runs`` like so::

  compare_runs(self.cases, 'l1_error', labels=['param1', 'param2'],
               styles=mystyles)

This approach is ideal when you have many plots for a large number of
variations. For customized plots where you wish to have much finer grained
control you can always write your own customized functions.

With this information you should be in a position to automate your
computational simulations and analysis.

Next we look at setting up additional remote computers on which we can execute
our computations.

Adding arbitrary tasks
------------------------

.. py:currentmodule:: automan.automation

The :py:class:`Automator` class also supports adding arbitrary Tasks and
Problems to the automation. For example if you want to run latex on a
manuscript, one could do the following::

    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Squares, Powers]
    )

    from automan.api import FileCommandTask
    task = FileCommandTask(
      'latexmk manuscript/paper.tex -pdf -outdir=manuscript',
      ['manuscript/paper.pdf']
    )
    automator.add_task(task, name='pdf', post_proc=True)

    automator.run()

Here, the task added uses the :py:class:`FileCommandTask` which only creates
some files in a directory. It is a convenience as the :py:class:`CommandTask`
assumes that the entire output directory is generated by the task. Here any
job related output (stderr, stdout) will be written to a directory
``manuscript/paper.pdf.job_info``.

The task added here is assigned a name, "pdf", when this is done, the task is
run only when explicitly requested, for example::

  $ python automate.py pdf

Will run the task. Since ``post_proc=True``, it will only be run once all the
problems are completed. If ``post_proc=False`` then it does not depend on
anything else. The usual rules for dependencies of tasks hold, so if you
create a set of tasks with mutual dependencies, those will be honored.

If no name was passed when the task was added, for example::

    automator.add_task(task, post_proc=True)

then this task will always be executed when all the problems are executed.

Note that when ``post_proc=True`` the :py:class:`RunAll` task is added to the
``task.depends`` list allowing you to do what you wish with it. You can
therefore add custom commands if needed. The ``automator.add_task`` method
also accepts :py:class:`Problem` classes or instances.

The automator is also usable interactively, so one could also do the
following::

    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[]
    )

    automator.add_task(MyProblem1)
    automator.run([])

    automator.add_task(MyProblem2)
    automator.run([])

Here we pass ``[]`` to the run method so as to ensure that no command line
processing is done which could be a mess. We can add tasks and problems in
this fashion and reuse the automation code to illustrate some ideas in a
jupyter notebook with this approach.



Using additional computational resources
----------------------------------------

Wouldn't it be nice if we could easily run part of the simulations on one or
more remote computers? ``automan`` makes this possible. Let us see how with
our last example.

Let us first remove all the generated outputs and files so we can try this::

  $ rm -rf outputs/ manuscript/figures config.json

Running the simulations on a remote machine requires a few things:

- the computer should be running either Mac OS or Linux/Unix.
- you should have an account on the computer, and be able to ``ssh`` into it
  without a password (see `article on password-less ssh
  <http://askubuntu.com/questions/46930/how-can-i-set-up-password-less-ssh-login>`_.
- the computer should have a working basic Python interpreter.
- on Linux the remote ``libpython*.so`` should be built as a shared library.
  If you are building Python from source you must do
  ``./configure --enable-shared`` or use a packaged Python like conda/miniconda/edm.
- Make sure that the python interpreter is in the $PATH and that the
  library directory is in $LD_LIBRARY_PATH -- again this applies only for a
  Python binary that you have built by yourself.
- while running commands from the host computer, remove the following from the
  remote computer's .bashrc::

   case $- in
   *i*) ;;
   *) return;;
   esac

For more complex dependencies, you need to make sure the remote machine has
the necessary software.


Assuming you have these requirements on a computer accessible on your network
you can do the following::

  $ python automate4.py -a host_name
  [...]

Where ``host_name`` is either the computer's name or IP address. This will
print a lot of output and attempt to setup a virtual environment on the remote
machine. If it fails, it will print out some instructions for you to fix.

If this succeeds, you can now simply use the automation script just as before
and it will now run some of the code on the remote machine depending on its
availability.  For example::

   $ python automate4.py
   14 tasks pending and 0 tasks running

   Running task CommandTask with output directory: 4 ...
   Starting worker on localhost.
   Job run by localhost
   Running python powers.py --output-dir outputs/powers/4 --power=4.0

   Running task CommandTask with output directory: 3 ...
   Starting worker on 10.1.10.242.
   Job run by 10.1.10.242
   Running python powers.py --output-dir outputs/powers/3 --power=3.0
   ...


Note that you can add new machines at any point. For example you may have
finished running a few simulations already and are simulating a new problem
that you wish to distribute, you can add a new machine and fire the automation
script and it will use it for the new simulations.

When you add a new remote host ``automan`` does the following:

- Creates an ``automan`` directory in the remote machine home directory (you
  can set a different home using ``python automate4.py -a host --home
  other_home``.)
- Inside this directory it copies the current project directory, ``tutorial``
  in the present case.
- It then copies over a ``bootstrap.sh`` and ``update.sh`` and runs the
  ``bootstrap.sh`` script. These scripts are inside a ``.automan/`` directory
  on your localhost and you may edit these if you need to.

The bootstrap code does the following:

- It creates a virtualenv_ called ``tutorial`` on this computer using the
  system Python and puts this in ``automan/envs/tutorial``.
- It then activates this environment, installs ``automan`` and also runs any
  ``requirements.txt`` if they exist in the tutorial directory.

If for some reason this script fails, you may edit it on the remote host and
re-run it.

When executing the code, automan copies over the files from the remote host to
your computer once the simulation is completed and also deletes the output
files on the remote machine.

If your remote computer shares your file-system via nfs or so, you can specify
this when you add the host as follows::

  $ python automate4.py -a host_sharing_nfs_files --nfs

In this case, files will not be copied back and forth from the remote host.


.. _virtualenv: https://virtualenv.pypa.io/

Now lets say you update files inside your project you can update the remote
hosts using::

   $ python automate4.py -u

This will update all remote workers and also run the ``update.sh`` script on
all of them. It will also copy your local modifications to the scripts in
``.automan``. It will then run any simulations.

Lets say you do not want to use a particular host, you can remove the entry
for this in the ``config.json`` file.

When ``automan`` distributes tasks to machines, local and remote, it needs
some information about the task and the remote machines. Recall that when we
created the ``Simulation`` instances we could pass in a ``job_info`` keyword
argument. The ``job_info`` is an optional dictionary with the following
optional keys:

- ``'n_core'``: the number of cores that this simulation requires. This is
  used for scheduling tasks. For example if you set ``n_core=4`` and have a
  computer with only 2 cores, automan will not be able to run this job on this
  machine at all. On the other hand if the task does indeed consume more than
  one core and you set the value to one, then the scheduler will run the job
  on a computer with only one core available. When ``n_core`` is set to a
  negative integer then the scheduler treats this as
  ``total_cores_on_machine/(-n_core)``. So for example if the value is -1, it
  will use all the cores on the machine, if it is -2, it will use half the
  cores. This is convenient when you have different computers with different
  core counts and when you wish to run only a single or limited number of jobs
  on the computer.
- ``'n_thread'``: the number of threads to use. This is used to set the
  environment variable ``OMP_NUM_THREADS`` for OpenMP executions. When this
  value is set to ``None``, it does not set the environment variable at all
  and this will imply that the default used by OpenMP will be used. If the
  number is set to a negative integer then it multiplies the absolute value of
  the specified number by the number of cores used, for example if
  ``n_core=4`` and ``n_thread=-2``, then the number of threads is set to 8. If
  ``n_core=-1`` and ``n_thread=-2``, then depending on the computer being
  used, the number of threads will be set to twice the number of physical
  cores on the computer.


As an example, here is how one would use this::

  Simulation(root=self.input_path('3.5'),
             base_command='python powers.py',
             job_info=dict(n_core=1, n_thread=1),
             power=3.5
  )

This job requires only a single core. So when automan tries to execute the job
on a computer it looks at the load on the computer and if one core is free, it
will execute the job.

If for some reason you are not happy with how the remote computer is managed
and wish to customize it, you can feel free to subclass the
:py:class:`automan.cluster_manager.ClusterManager` class. You may pass this in
to the :py:class:`automan.automation.Automator` class as the
``cluster_manager_factory`` and it will use it. This is useful if for example
you wish to use conda or some other tool to manage the Python environment on
the remote computer.

We provide two simple environment managers, one is a based on Anaconda's
conda_ and the other is on Enthought's edm_, the following contains details on
how to use them.

.. _edm: https://docs.enthought.com/edm
.. _conda: https://conda.io/

A simple :py:class:`automan.conda_cluster_manager.CondaClusterManager` which
will setup a remote computer so long as it has conda_ on it. If your project
directory has an ``environments.yml`` and/or a ``requirements.txt`` it will use
those to setup the environment. This is really a prototype and you may feel
free to customize this. To use the conda cluster manager you could do the
following in the tutorial example::

    from automan.api import CondaClusterManager

    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Squares, Powers],
        cluster_manager_factory=CondaClusterManager
    )
    automator.run()


A simple :py:class:`automan.edm_cluster_manager.EDMClusterManager` which will
setup a remote computer so long as it has edm_ on it. If your project directory
has an ``bundled_envs.json`` and/or a ``requirements.txt`` it will use those to
setup the environment. You can change the file names by accessing ``ENV_FILE``
class variable . By default this assumes the edm executable location to be in
``~/.edm`` to change this point the ``EDM_ROOT`` variable to the correct
location relative to ``~`` (the current user home folder) not including the
symbol ``~``. To use the edm cluster manager you could do the following in the
tutorial example::

    from automan.api import EDMClusterManager

    automator = Automator(
        simulation_dir='outputs',
        output_dir='manuscript/figures',
        all_problems=[Squares, Powers],
        cluster_manager_factory=EDMClusterManager
    )
    automator.run()

You may also subclass these or customize the bootstrap code and use that.

A complete example of each of these is available in the
``examples/edm_conda_cluster`` directory that you can see here
https://github.com/pypr/automan/tree/master/examples/edm_conda_cluster

The README in the directory tells you how to run the examples.


Specifying simulation dependencies
-----------------------------------

.. versionadded:: 0.4
   Specifying simulation dependencies was added in the 0.4 version.

There are times when one simulation uses the output from another and you wish
to execute them in the right order. This can be quite easily achieved. Here is
a simple example from the test suite that illustrates this::

  class MyProblem(Problem):
      def setup(self):
          cmd = 'python -c "import time; print(time.time())"'
          s1 = Simulation(self.input_path('1'), cmd)
          s2 = Simulation(self.input_path('2'), cmd, depends=[s1])
          s3 = Simulation(self.input_path('3'), cmd, depends=[s1, s2])
          self.cases = [s1, s2, s3]

Notice the extra keyword argument, ``depends=`` which specifies a list of
other simulations. In the above case, we could have also used ``self.cases =
[s3]`` and that would have automatically picked up the other simulations.

When this problem is run, ``s1`` will run first followed by ``s2`` and then by
``s3``. Note that this will only execute ``s1`` once even though it is
declared as a dependency for two other simulations. This makes it possible to
easily define inter-dependent tasks/simulations. In general, the dependencies
could be any :py:class:`automan.automation.Simulation` or
:py:class:`automan.automation.Task` instance.

Internally, these simulations create suitable task instances that support
dependencies see :py:class:`automan.automation.CommandTask`


Specifying inter-problem dependencies
--------------------------------------

.. versionadded:: 0.4
   Specifying problem dependencies was added in the 0.4 version.

Sometimes you may have a situation where one problem depends on the output of
another. These may be done by overriding the ``Problem.get_requires`` method.
Here is an example from the test suite::

  class A(Problem):
      def get_requires(self):
          cmd = 'python -c "print(1)"'
          ct = CommandTask(cmd, output_dir=self.sim_dir)
          return [('task1', ct)]

  class B(Problem):
      def get_requires(self):
          # or return Problem instances ...
          return [('a', A(self.sim_dir, self.out_dir))]

  class C(Problem):
      def get_requires(self):
          # ... or Problem subclasses
          return [('a', A), ('b', B)]

Normally, the ``get_requires`` method automatically creates tasks from the
simulations specified but in the above example we show a case (problem ``A``)
where we explicitly create command tasks. In the above example, the problem
``B`` depends on the problem ``A`` and simply returns an instance of ``A``. On
the other hand ``C`` only returns the problem class and not an instance. This
shows how one can specify inter problem dependencies.

Note that if the problem performs some simulations (by setting
``self.cases``), you should call the parent method (via ``super``) and add
your additional dependencies to this.

Also note that the dependencies are resolved based on the "outputs" of a task.
So two tasks with the same outputs are treated as the same. This is consistent
with the design of automan where each simulation's output goes in its own
directory.


Using docker
------------

It should be possible to use automan from within a Docker_ container. This can
be done either by specifying commands to be run within suitable ``docker run``
invocations. Alternatively, one can install automan and run scripts within the
docker container and this will work correctly.

One could use docker on the remote computers also but this is not yet fully
tested.

.. _Docker: https://www.docker.com/

Learning more
-------------

If you wish to learn more about automan you may find the following useful:

- Read the `automan paper
  <http://doi.ieeecomputersociety.org/10.1109/MCSE.2018.05329818>`_ or a `draft
  of the paper <https://arxiv.org/abs/1712.04786>`_.

- The paper mentions another manuscript which was fully automated using
  automan, the sources for this are at https://gitlab.com/prabhu/edac_sph/ and
  this demonstrates a complete real-world example of using automan to automate
  an entire research paper.

- Olivier Mesnard has created a nice example as part of the review of this
  paper that can be seen here: https://github.com/mesnardo/automan-example the
  example also nicely shows how automan can be used from within a docker
  container for a completely reproducible workflow.
