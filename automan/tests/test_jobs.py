import psutil
import multiprocessing
import shutil
import sys
import os
import tempfile
import time
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

try:
    from automan import jobs
except ImportError:
    raise unittest.SkipTest('test_jobs requires psutil')


def safe_rmtree(*args, **kw):
    if sys.platform.startswith('win'):
        try:
            shutil.rmtree(*args, **kw)
        except WindowsError:
            pass
    else:
        try:
            shutil.rmtree(*args, **kw)
        except OSError:
            pass


def test_cores_required():
    with mock.patch('automan.jobs.total_cores', return_value=4.0):
        assert jobs.cores_required(0) == 0
        assert jobs.cores_required(1) == 1
        assert jobs.cores_required(3) == 3
        assert jobs.cores_required(-1) == 4
        assert jobs.cores_required(-2) == 2
        assert jobs.cores_required(-4) == 1


def test_threads_required():
    with mock.patch('automan.jobs.total_cores', return_value=4.0):
        # n_thread, n_core
        assert jobs.threads_required(1, 1) == 1
        assert jobs.threads_required(2, 2) == 2
        assert jobs.threads_required(2, -1) == 2
        assert jobs.threads_required(-1, -1) == 4
        assert jobs.threads_required(-2, -1) == 8
        assert jobs.threads_required(-2, -2) == 4
        assert jobs.threads_required(-4, -1) == 16


class TestJob(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.root):
            safe_rmtree(self.root)

    def test_job_can_handle_string_command(self):
        # Given
        command = '''\
        python -c 'import sys;sys.stdout.write("1");sys.stderr.write("2")' '''
        j = jobs.Job(command=command, output_dir=self.root)

        # When
        j.run()
        j.join()

        # Then.
        self.assertTrue(isinstance(j.command, list))
        self.assertTrue(j.status(), 'done')
        self.assertEqual(j.get_stdout(), '1')
        self.assertEqual(j.get_stderr(), '2')

    def test_simple_job(self):
        # Given
        command = ['python', '-c',
                   'import sys;sys.stdout.write("1");sys.stderr.write("2")']
        j = jobs.Job(command=command, output_dir=self.root)

        # When
        j.run()
        j.join()

        # Then
        self.assertEqual(j.status(), 'done')
        self.assertEqual(j.output_dir, self.root)
        self.assertEqual(j.n_core, 1)
        self.assertEqual(j.n_thread, 1)
        self.assertEqual(j.get_stdout(), '1')
        self.assertEqual(j.get_stderr(), '2')
        state = j.to_dict()
        expect = dict(
            command=command, output_dir=self.root, n_core=1,
            n_thread=1, env=None
        )
        expect['command'][0] = sys.executable
        self.assertDictEqual(state, expect)

    def test_job_substitute_in_command(self):
        # Given
        j = jobs.Job(command=['python', '-c',  'print(123)'],
                     output_dir=self.root)

        # When
        sub = '/usr/bin/python'
        j.substitute_in_command('python', sub)

        # Then
        self.assertEqual(j.command[0], sub)

    def test_job_status(self):
        # Given/When
        j = jobs.Job(
            [sys.executable, '-c', 'import time; time.sleep(0.25)'],
            output_dir=self.root
        )

        # Then
        self.assertEqual(j.status(), 'not started')

        # When
        j.run()

        # Then
        self.assertEqual(j.status(), 'running')

        # When
        j.join()
        self.assertEqual(j.status(), 'done')

        # Given
        j = jobs.Job(
            [sys.executable, '-c', 'asdf'],
            output_dir=self.root
        )
        # When
        j.run()
        j.join()

        # Then
        self.assertEqual(j.status(), 'error')
        self.assertTrue('NameError' in j.get_stderr())

    def test_proc_reset_when_job_done(self):
        # Given/When
        j = jobs.Job(
            [sys.executable, '-c', 'import time; time.sleep(0.25)'],
            output_dir=self.root
        )

        # Then
        self.assertEqual(j.status(), 'not started')
        self.assertIsNone(j.proc)

        # When
        j.run()

        # Then
        self.assertEqual(j.status(), 'running')
        self.assertIsNotNone(j.proc)

        # When
        j.join()
        self.assertEqual(j.status(), 'done')
        self.assertIsNone(j.proc)

    def test_reset_proc_when_job_status_error(self):
        j = jobs.Job(
            [sys.executable, '--junk'],
            output_dir=self.root,
            n_thread=4,
        )

        # Then
        self.assertEqual(j.status(), 'not started')
        self.assertIsNone(j.proc)

        # When
        j.run()

        self.assertEqual(j.status(), 'running')
        self.assertIsNotNone(j.proc)

        # When
        j.join()

        # Then
        self.assertEqual(j.status(), 'error')
        self.assertIsNone(j.proc)

    def test_that_job_sets_env_var(self):
        # Given/When
        j = jobs.Job(
            [sys.executable, '-c', 'import os;print(os.environ.get("FOO"))'],
            output_dir=self.root,
            env=dict(FOO='hello')
        )
        j.run()
        j.join()

        # Then
        print(j.get_stdout(), j.get_stderr())
        self.assertEqual(j.status(), 'done')
        self.assertEqual(j.get_stdout().strip(), 'hello')

    @mock.patch('automan.jobs.total_cores', return_value=2.0)
    def test_that_job_sets_omp_var(self, mock_total_cores):
        j = jobs.Job(
            [sys.executable, '-c',
             'import os;print(os.environ.get("OMP_NUM_THREADS"))'],
            output_dir=self.root,
            n_thread=4,
        )
        j.run()
        j.join()

        # Then
        self.assertEqual(j.status(), 'done')
        self.assertEqual(j.get_stdout().strip(), '4')
        self.assertEqual(j.env.get('OMP_NUM_THREADS'), '4')

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'print(1)'],
            output_dir=self.root,
            n_thread=None,
        )

        # Then
        self.assertFalse('OMP_NUM_THREADS' in j.env)

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'print(1)'],
            output_dir=self.root,
            n_thread=-2, n_core=1
        )

        # Then
        self.assertEqual(j.env.get('OMP_NUM_THREADS'), '2')

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'print(1)'],
            output_dir=self.root,
            n_thread=-2, n_core=-1
        )

        # Then
        self.assertEqual(j.env.get('OMP_NUM_THREADS'), '4')

    def test_free_cores(self):
        n = jobs.free_cores()
        self.assertTrue(n >= 0)
        self.assertTrue(n <= multiprocessing.cpu_count())

    def test_total_cores(self):
        n = jobs.total_cores()
        self.assertTrue(n >= 0)
        self.assertTrue(n <= multiprocessing.cpu_count())

    def test_status_when_job_is_incorrect(self):
        j = jobs.Job(
            [sys.executable, '--junk'],
            output_dir=self.root,
            n_thread=4,
        )
        j.run()
        j.join()

        # Then
        self.assertEqual(j.status(), 'error')
        info = j.get_info()
        self.assertEqual(info['status'], 'error')
        self.assertTrue(info['exitcode'] != 0)

        # Now retry and the status should be the same.
        j1 = jobs.Job(
            [sys.executable, '--junk'],
            output_dir=self.root,
            n_thread=4,
        )

        self.assertEqual(j1.status(), 'error')

    def test_status_when_job_is_rerun(self):
        # Given
        command = ['python', '-c', 'print(123)']
        j = jobs.Job(command=command, output_dir=self.root)
        j.run()
        j.join()

        # When
        j1 = jobs.Job(command=command, output_dir=self.root)

        # Then
        self.assertEqual(j1.status(), 'done')

    def test_clean_removes_new_output_directory(self):
        # Given
        out_dir = os.path.join(self.root, 'junk')
        command = ['python', '-c', 'print(123)']
        j = jobs.Job(command=command, output_dir=out_dir)
        j.run()
        j.join()

        # When
        j.clean()

        # Then
        self.assertFalse(os.path.exists(out_dir))

    def test_clean_does_not_remove_existing_output_directory(self):
        # Given
        command = ['python', '-c', 'print(123)']
        j = jobs.Job(command=command, output_dir=self.root)
        j.run()
        j.join()

        # When
        j.clean()

        # Then
        self.assertFalse(os.path.exists(j.stdout))
        self.assertFalse(os.path.exists(j.stderr))
        self.assertTrue(os.path.exists(self.root))

    def test_job_status_when_process_killed(self):
        # Given
        cmd = ['python', '-c', 'import time; time.sleep(100)']
        j = jobs.Job(command=cmd, output_dir=self.root)
        j.run()
        wait_until(lambda: j.get_info()['pid'] is None)

        # When

        # Kill the Python process the job is running, as well as its subprocess.
        pid = j.get_info()['pid']
        proc = psutil.Process(pid)
        j.proc.kill()
        proc.kill()

        def _check_proc():
            try:
                proc.status()
                return True
            except psutil.NoSuchProcess:
                return False

        wait_until(_check_proc)

        j = jobs.Job(command=cmd, output_dir=self.root)

        # Then
        self.assertEqual(j.status(), 'error')


def wait_until(cond, timeout=1, wait=0.1):
    t = 0.0
    while cond():
        time.sleep(wait)
        t += wait
        if t > timeout:
            break


class TestLocalWorker(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        safe_rmtree(self.root)

    @mock.patch('automan.jobs.total_cores', return_value=4.0)
    @mock.patch('automan.jobs.free_cores', return_value=2.0)
    def test_worker_computes_correct_cores_required(
            self, mock_free_cores, mock_total_cores
    ):
        # Given
        w = jobs.Worker()
        self.assertEqual(w.total_cores(), 4.0)
        self.assertEqual(w.free_cores(), 2.0)

        # When/Then
        self.assertEqual(w.cores_required(1), 1)
        self.assertEqual(w.cores_required(2), 2)
        self.assertEqual(w.cores_required(0), 0)
        self.assertEqual(w.cores_required(-1), 4)
        self.assertEqual(w.cores_required(-2), 2)

        self.assertEqual(w.can_run(0), True)
        self.assertEqual(w.can_run(1), True)
        self.assertEqual(w.can_run(2), True)
        self.assertEqual(w.can_run(-2), True)
        self.assertEqual(w.can_run(-1), False)

    @mock.patch('automan.jobs.free_cores', return_value=2.0)
    def test_scheduler_works_with_local_worker(self, mock_free_cores):
        # Given
        s = jobs.Scheduler(worker_config=[dict(host='localhost')])

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'import time; time.sleep(0.05); print(1)'],
            output_dir=self.root
        )
        proxy = s.submit(j)

        # Then
        wait_until(lambda: proxy.status() != 'done', timeout=2)
        self.assertEqual(proxy.status(), 'done')
        self.assertEqual(proxy.get_stderr(), '')
        self.assertEqual(proxy.get_stdout().strip(), '1')
        info = proxy.get_info()
        self.assertEqual(info['status'], 'done')
        self.assertEqual(info['exitcode'], 0)


class TestRemoteWorker(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        try:
            import execnet
        except ImportError:
            raise unittest.SkipTest('This test requires execnet')

    def tearDown(self):
        safe_rmtree(self.root)

    def test_free_cores(self):
        # Given
        r = jobs.RemoteWorker(
            host='localhost', python=sys.executable, testing=True
        )
        # Then.
        n = r.free_cores()
        self.assertTrue(n >= 0)
        self.assertTrue(n <= multiprocessing.cpu_count())

    def test_simple(self):
        # Given
        r = jobs.RemoteWorker(
            host='localhost', python=sys.executable, testing=True
        )

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'import time; time.sleep(0.05); print(1)'],
            output_dir=self.root
        )
        proxy = r.run(j)

        # Then
        wait_until(lambda: proxy.status() != 'done')
        self.assertEqual(proxy.status(), 'done')
        self.assertEqual(proxy.get_stderr(), '')
        self.assertEqual(proxy.get_stdout().strip(), '1')
        info = proxy.get_info()
        self.assertEqual(info['status'], 'done')
        self.assertEqual(info['exitcode'], 0)

    def test_remote_worker_does_not_copy_when_nfs_is_set(self):
        # Given
        r = jobs.RemoteWorker(
            host='localhost', python=sys.executable, testing=True, nfs=True
        )

        # When
        j = jobs.Job(
            [sys.executable, '-c', 'import time; time.sleep(0.05); print(1)'],
            output_dir=self.root
        )
        proxy = r.run(j)
        wait_until(lambda: proxy.status() != 'done')

        # Now set testing to False and check the copying
        r.testing = False
        ret = r.copy_output(proxy.job_id, '.')

        # Then
        self.assertEqual(ret, None)


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.count = 0
        try:
            import execnet
        except ImportError:
            raise unittest.SkipTest('This test requires execnet')

    def tearDown(self):
        safe_rmtree(self.root)

    def _make_dummy_job(self, n_core=1, sleep=0.05):
        output = os.path.join(self.root, 'job%d' % self.count)
        job = jobs.Job(
            [sys.executable, '-c',
             'import time; time.sleep(%f); print(1)' % sleep],
            output_dir=output,
            n_core=n_core
        )
        self.count += 1
        return job

    @mock.patch('automan.jobs.LocalWorker')
    def test_scheduler_does_not_start_worker_when_created(self, mock_lw):
        # Given
        config = [dict(host='localhost')]

        # When
        s = jobs.Scheduler(worker_config=config)

        # Then
        self.assertEqual(mock_lw.call_count, 0)
        self.assertEqual(len(s.workers), 0)

    @mock.patch('automan.jobs.LocalWorker')
    def test_scheduler_starts_worker_on_submit(self, mock_lw):
        attrs = {'host': 'localhost', 'free_cores.return_value': 2}
        mock_lw.return_value = mock.MagicMock(**attrs)

        # Given
        config = [dict(host='localhost')]
        s = jobs.Scheduler(worker_config=config)
        j = jobs.Job(
            [sys.executable, '-c', 'print(1)'],
            output_dir=self.root
        )

        # When
        s.submit(j)

        # Then
        self.assertEqual(mock_lw.call_count, 1)
        self.assertEqual(len(s.workers), 1)

    @mock.patch.object(jobs.RemoteWorker, 'free_cores', return_value=2.0)
    def test_scheduler_only_creates_required_workers(self, mock_remote_worker):
        # Given
        config = [
            dict(host='host1', python=sys.executable, testing=True),
            dict(host='host2', python=sys.executable, testing=True),
        ]
        s = jobs.Scheduler(worker_config=config)
        j = self._make_dummy_job()

        # When
        proxy = s.submit(j)

        # Then
        self.assertEqual(len(s.workers), 1)
        self.assertEqual(proxy.worker.host, 'host1')

        # Wait for this job to end and then see what happens
        # When a new job is submitted.
        self._wait_while_not_done(proxy, 25)

        # When
        j = self._make_dummy_job()
        s.submit(j)

        # Then
        self.assertEqual(len(s.workers), 1)
        self.assertEqual(proxy.worker.host, 'host1')

        # Running two jobs in a row should produce two workers.
        # When
        j = self._make_dummy_job()
        proxy = s.submit(j)

        # Then
        self.assertEqual(len(s.workers), 2)
        self.assertEqual(proxy.worker.host, 'host2')

        # Adding more should work.

        # When
        j = self._make_dummy_job()
        proxy = s.submit(j)
        j = self._make_dummy_job()
        proxy1 = s.submit(j)

        # Then
        self.assertEqual(len(s.workers), 2)
        self._wait_while_not_done(proxy, 15)
        self._wait_while_not_done(proxy1, 15)

        self.assertEqual(proxy.status(), 'done')
        self.assertEqual(proxy.worker.host, 'host1')
        self.assertEqual(proxy1.worker.host, 'host2')

    @mock.patch('automan.jobs.total_cores', return_value=2.0)
    @mock.patch('automan.jobs.free_cores', return_value=2.0)
    def test_scheduler_should_not_overload_worker(self, m_total_cores,
                                                  m_free_cores):
        # Given
        n_core = jobs.total_cores()
        config = [dict(host='localhost')]
        s = jobs.Scheduler(worker_config=config, wait=0.5)

        j1 = self._make_dummy_job(n_core, sleep=0.5)
        j2 = self._make_dummy_job(n_core, sleep=0.5)
        j3 = self._make_dummy_job(n_core, sleep=0.5)
        j4 = self._make_dummy_job(0, sleep=0.5)

        # When
        proxy1 = s.submit(j1)
        proxy2 = s.submit(j2)
        proxy3 = s.submit(j3)
        proxy4 = s.submit(j4)

        # Then
        self.assertEqual(len(s.workers), 1)
        # Basically, submit will wait for the existing jobs to complete.
        # Therefore when s.submit(j3) is called it should wait until a
        # free worker is available.
        self.assertEqual(proxy1.status(), 'done')
        self.assertEqual(proxy2.status(), 'done')
        self.assertEqual(proxy3.status(), 'running')

        # Proxy4 will be running since it needs no cores.
        self.assertEqual(proxy4.status(), 'running')
        self._wait_while_not_done(proxy3, 20)
        self.assertEqual(proxy3.status(), 'done')
        self._wait_while_not_done(proxy4, 15)
        self.assertEqual(proxy4.status(), 'done')

    def _wait_while_not_done(self, proxy, n_count, sleep=0.1):
        count = 0
        while proxy.status() != 'done' and count < n_count:
            time.sleep(sleep)
            count += 1
