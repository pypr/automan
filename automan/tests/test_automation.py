from __future__ import print_function

import os
import shutil
import sys
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from automan.automation import (
    Automator, CommandTask, PySPHProblem, Simulation, SolveProblem,
    TaskRunner, compare_runs, filter_cases
)
try:
    from automan.jobs import Scheduler, RemoteWorker
except ImportError:
    raise unittest.SkipTest('test_jobs requires psutil')

from automan.cluster_manager import ClusterManager

from automan.tests.test_jobs import wait_until, safe_rmtree


class MySimulation(Simulation):
    @property
    def data(self):
        if self._results is None:
            with open(self.input_path('results.dat')) as fp:
                self._results = fp.read()
        return self._results


class EllipticalDrop(PySPHProblem):
    """We define a simple example problem which we will run using the automation
    framework.

    In this case we run two variants of the elliptical drop problem.

    The setup method defines the cases to run which are simply Simulation
    instances.

    The get_commands returns the actual commands to run.

    The run method does the post-processing, after the simulations are done.

    """

    def get_name(self):
        return 'elliptical_drop'

    def setup(self):
        # Two cases, one with update_h and one without.
        cmd = 'python -m automan.tests.example'

        # If self.cases is set, the get_requires method will do the right
        # thing.
        self.cases = [
            MySimulation(
                root=self.input_path('update_h'),
                base_command=cmd,
                job_info=dict(n_core=1, n_thread=1),
                update_h=None
            ),
            MySimulation(
                root=self.input_path('no_update_h'),
                base_command=cmd,
                job_info=dict(n_core=1, n_thread=1),
                no_update_h=None
            ),
        ]

    def run(self):
        self.make_output_dir()
        no_update = self.cases[0].data
        update = self.cases[1].data
        output = open(self.output_path('result.txt'), 'w')
        output.write('no_update_h: %s\n' % no_update)
        output.write('update_h: %s\n' % update)
        output.close()


class TestAutomationBase(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        self.sim_dir = 'sim'
        self.output_dir = 'output'
        patch = mock.patch(
            'automan.jobs.free_cores', return_value=2
        )
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self):
        os.chdir(self.cwd)
        if os.path.exists(self.root):
            safe_rmtree(self.root)


class TestLocalAutomation(TestAutomationBase):
    def _make_scheduler(self):
        worker = dict(host='localhost')
        s = Scheduler(root='.', worker_config=[worker])
        return s

    def test_automation(self):
        # Given.
        problem = EllipticalDrop(self.sim_dir, self.output_dir)
        s = self._make_scheduler()
        t = TaskRunner(tasks=[SolveProblem(problem=problem)], scheduler=s)

        # When.
        t.run(wait=1)

        # Then.
        sim1 = os.path.join(self.root, self.sim_dir,
                            'elliptical_drop', 'no_update_h')
        self.assertTrue(os.path.exists(sim1))
        sim2 = os.path.join(self.root, self.sim_dir,
                            'elliptical_drop', 'update_h')
        self.assertTrue(os.path.exists(sim2))

        results = os.path.join(self.root, self.output_dir,
                               'elliptical_drop', 'result.txt')
        self.assertTrue(os.path.exists(results))
        data = open(results).read()
        self.assertTrue('no_update_h' in data)
        self.assertTrue('update_h' in data)

        # When.
        problem = EllipticalDrop(self.sim_dir, self.output_dir)
        t = TaskRunner(tasks=[SolveProblem(problem=problem)], scheduler=s)

        # Then.
        self.assertEqual(len(t.todo), 0)

        # When
        problem.clean()

        # Then.
        out1 = os.path.join(self.root, self.output_dir,
                            'elliptical_drop', 'update_h')
        out2 = os.path.join(self.root, self.output_dir,
                            'elliptical_drop', 'no_update_h')
        self.assertFalse(os.path.exists(out1))
        self.assertFalse(os.path.exists(out2))
        self.assertTrue(os.path.exists(sim1))
        self.assertTrue(os.path.exists(sim2))

    def test_nothing_is_run_when_output_exists(self):
        # Given.
        s = self._make_scheduler()
        output = os.path.join(self.output_dir, 'elliptical_drop')
        os.makedirs(output)

        # When
        problem = EllipticalDrop(self.sim_dir, self.output_dir)
        t = TaskRunner(tasks=[SolveProblem(problem=problem)], scheduler=s)

        # Then.
        self.assertEqual(len(t.todo), 0)


class TestRemoteAutomation(TestLocalAutomation):
    def setUp(self):
        super(TestRemoteAutomation, self).setUp()
        self.other_dir = tempfile.mkdtemp()
        p = mock.patch.object(
            RemoteWorker, 'free_cores', return_value=2.0
        )
        p.start()
        self.addCleanup(p.stop)

    def tearDown(self):
        super(TestRemoteAutomation, self).tearDown()
        if os.path.exists(self.other_dir):
            safe_rmtree(self.other_dir)

    def _make_scheduler(self):
        workers = [
            dict(host='localhost'),
            dict(host='test_remote',
                 python=sys.executable, chdir=self.other_dir, testing=True)
        ]
        try:
            import execnet
        except ImportError:
            raise unittest.SkipTest('This test requires execnet')
        return Scheduler(root=self.sim_dir, worker_config=workers)

    def test_job_with_error_is_handled_correctly(self):
        # Given.
        problem = EllipticalDrop(self.sim_dir, self.output_dir)
        problem.cases[0].base_command += ' --xxx'
        s = self._make_scheduler()
        t = TaskRunner(tasks=[SolveProblem(problem=problem)], scheduler=s)

        # When.
        try:
            t.run(wait=1)
        except RuntimeError:
            pass

        # Then.

        # Ensure that the directories are copied over when they have errors.
        sim1 = os.path.join(self.root, self.sim_dir,
                            'elliptical_drop', 'no_update_h')
        self.assertTrue(os.path.exists(sim1))
        sim2 = os.path.join(self.root, self.sim_dir,
                            'elliptical_drop', 'update_h')
        self.assertTrue(os.path.exists(sim2))

        # Ensure that all the correct but already scheduled jobs are completed.
        task_status = t.task_status
        status_values = list(task_status.values())
        self.assertEqual(status_values.count('error'), 1)
        self.assertEqual(status_values.count('done'), 1)
        self.assertEqual(status_values.count('not started'), 1)
        for t, s in task_status.items():
            if s == 'done':
                self.assertTrue(t.complete())
            if s == 'error':
                self.assertFalse(t.complete())


class TestCommandTask(TestAutomationBase):
    def _make_scheduler(self):
        worker = dict(host='localhost')
        s = Scheduler(root='.', worker_config=[worker])
        return s

    def test_command_tasks_executes_simple_command(self):
        # Given
        s = self._make_scheduler()
        cmd = 'python -c "print(1)"'
        t = CommandTask(cmd, output_dir=self.sim_dir)

        self.assertFalse(t.complete())

        # When
        t.run(s)
        wait_until(lambda: not t.complete())

        # Then
        self.assertTrue(t.complete())
        self.assertEqual(t.job_proxy.status(), 'done')
        self.assertEqual(t.job_proxy.get_stdout().strip(), '1')

    def test_command_tasks_converts_dollar_output_dir(self):
        # Given
        s = self._make_scheduler()
        cmd = '''python -c "print('$output_dir')"'''
        t = CommandTask(cmd, output_dir=self.sim_dir)

        self.assertFalse(t.complete())

        # When
        t.run(s)
        wait_until(lambda: not t.complete())

        # Then
        self.assertTrue(t.complete())
        self.assertEqual(t.job_proxy.status(), 'done')
        self.assertEqual(t.job_proxy.get_stdout().strip(), self.sim_dir)

    def test_command_tasks_handles_errors_correctly(self):
        # Given
        s = self._make_scheduler()
        cmd = 'python --junk'
        t = CommandTask(cmd, output_dir=self.sim_dir)

        self.assertFalse(t.complete())

        # When
        t.run(s)
        try:
            wait_until(lambda: not t.complete())
        except RuntimeError:
            pass

        # Then
        self.assertFalse(t.complete())
        self.assertEqual(t.job_proxy.status(), 'error')

        # A new command task should still detect that the run failed, even
        # though the output directory exists.
        # Given
        t = CommandTask(cmd, output_dir=self.sim_dir)
        # When/Then
        self.assertFalse(t.complete())


def test_simulation_get_labels():
    # Given
    s = Simulation(
        'junk', 'pysph run taylor_green',
        nx=25, perturb=0.1, correction=None
    )

    # When
    l = s.get_labels('nx')

    # Then
    assert l == r'nx=25'

    # When
    l = s.get_labels(['nx', 'perturb', 'correction'])

    # Then
    assert l == r'nx=25, perturb=0.1, correction'


def test_compare_runs_calls_methods_when_given_names():
    # Given
    sims = [mock.MagicMock(), mock.MagicMock()]
    s0, s1 = sims
    s0.get_labels.return_value = s1.get_labels.return_value = 'label'

    # When
    compare_runs(sims, 'fig', labels=['x'], exact='exact')

    # Then
    s0.exact.assert_called_once_with(color='k', linestyle='-')
    s0.fig.assert_called_once_with(color='k', label='label', linestyle='--')
    s0.get_labels.assert_called_once_with(['x'])
    assert s1.exact.called is False
    s1.fig.assert_called_once_with(color='k', label='label', linestyle='-.')
    s1.get_labels.assert_called_once_with(['x'])


def test_compare_runs_works_when_given_callables():
    # Given
    sims = [mock.MagicMock()]
    s0 = sims[0]
    s0.get_labels.return_value = 'label'

    func = mock.MagicMock()
    exact = mock.MagicMock()

    # When
    compare_runs(sims, func, labels=['x'], exact=exact)

    # Then
    exact.assert_called_once_with(s0, color='k', linestyle='-')
    func.assert_called_once_with(s0, color='k', label='label', linestyle='--')
    s0.get_labels.assert_called_once_with(['x'])


def test_filter_cases_works_with_params():
    # Given
    sims = [Simulation(root='', base_command='python', param1=i, param2=i+1)
            for i in range(5)]
    # When
    result = filter_cases(sims, param1=2)

    # Then
    assert len(result) == 1
    assert result[0].params['param1'] == 2

    # When
    result = filter_cases(sims, param1=2, param2=2)

    # Then
    assert len(result) == 0

    # When
    result = filter_cases(sims, param1=3, param2=4)

    # Then
    assert len(result) == 1
    assert result[0].params['param1'] == 3
    assert result[0].params['param2'] == 4


def test_filter_cases_works_with_predicate():
    # Given
    sims = [Simulation(root='', base_command='python', param1=i, param2=i+1)
            for i in range(5)]

    # When
    result = filter_cases(
        sims, predicate=lambda x: x.params.get('param1', 0) % 2
    )

    # Then
    assert len(result) == 2
    assert result[0].params['param1'] == 1
    assert result[1].params['param1'] == 3

    # When
    result = filter_cases(
        sims, predicate=2
    )

    # Then
    assert len(result) == 0

    # Given
    sims = [Simulation(root='', base_command='python', predicate=i)
            for i in range(5)]

    # When
    result = filter_cases(
        sims, predicate=2
    )

    # Then
    assert len(result) == 1
    assert result[0].params['predicate'] == 2


class TestAutomator(TestAutomationBase):
    def setUp(self):
        super(TestAutomator, self).setUp()

    def test_automator_accepts_cluster_manager(self):
        # Given/When
        a = Automator('sim', 'output', [EllipticalDrop],
                      cluster_manager_factory=ClusterManager)

        # Then
        self.assertEqual(a.cluster_manager_factory, ClusterManager)

    @mock.patch.object(TaskRunner, 'run')
    def test_automator(self, mock_run):
        # Given
        a = Automator('sim', 'output', [EllipticalDrop])

        # When
        a.run([])

        # Then
        mock_run.assert_called_with()
        self.assertEqual(len(a.runner.todo), 4)

        expect = ['RunAll', 'SolveProblem', 'PySPHTask', 'PySPHTask']
        names = [x.__class__.__name__ for x in a.runner.todo]
        self.assertEqual(names, expect)

        # When
        # Given
        a = Automator('sim', 'output', [EllipticalDrop])
        a.run(['-m', '*no_up*'])

        # Then
        mock_run.assert_called_with()
        self.assertEqual(len(a.runner.todo), 3)

        expect = ['RunAll', 'SolveProblem', 'PySPHTask']
        names = [x.__class__.__name__ for x in a.runner.todo]
        self.assertEqual(names, expect)
        out_dir = os.path.basename(a.runner.todo[-1].output_dir)
        self.assertEqual(out_dir, 'no_update_h')
