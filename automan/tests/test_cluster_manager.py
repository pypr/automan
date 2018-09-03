from __future__ import print_function

import json
import os
from os.path import dirname
import shutil
import sys
import tempfile
from textwrap import dedent
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from automan.jobs import Job
from automan.cluster_manager import ClusterManager
from automan.conda_cluster_manager import CondaClusterManager
from automan.edm_cluster_manager import EDMClusterManager
from .test_jobs import wait_until


ROOT_DIR = dirname(dirname(dirname(__file__)))


class MyClusterManager(ClusterManager):

    BOOTSTRAP = dedent("""\
        #!/bin/bash

        set -e
        python3 -m venv --system-site-packages envs/{project_name}
        """)

    UPDATE = dedent("""\
         #!/bin/bash
         echo "update"
         """)

    def _get_helper_scripts(self):
        return None


class TestClusterManager(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.cwd)
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    def _get_config(self):
        with open(os.path.join(self.root, 'config.json'), 'r') as fp:
            data = json.load(fp)
        return data

    def test_new_config_created_on_creation(self):
        # Given/When
        ClusterManager()

        # Then
        config = self._get_config()

        self.assertEqual(config.get('root'), 'automan')
        self.assertEqual(config.get('project_name'),
                         os.path.basename(self.root))
        self.assertEqual(os.path.realpath(config.get('sources')[0]),
                         os.path.realpath(self.root))
        workers = config.get('workers')
        self.assertEqual(len(workers), 1)
        self.assertEqual(workers[0]['host'], 'localhost')

    @mock.patch.object(ClusterManager, '_bootstrap')
    def test_add_worker(self, mock_bootstrap):
        # Given
        cm = ClusterManager()

        # When
        cm.add_worker('host', home='/home/foo', nfs=False)

        # Then
        mock_bootstrap.assert_called_with('host', '/home/foo')
        config = self._get_config()
        workers = config.get('workers')
        self.assertEqual(len(workers), 2)
        hosts = sorted(x['host'] for x in workers)
        self.assertEqual(hosts, ['host', 'localhost'])

    @mock.patch.object(ClusterManager, '_bootstrap')
    def test_create_scheduler(self, mock_bootstrap):
        # Given
        cm = ClusterManager()
        cm.add_worker('host', home='/home/foo', nfs=False)

        # When
        s = cm.create_scheduler()

        # Then
        confs = s.worker_config
        hosts = sorted([x['host'] for x in confs])
        self.assertEqual(hosts, ['host', 'localhost'])

    @mock.patch.object(ClusterManager, '_bootstrap')
    @mock.patch.object(ClusterManager, '_update_sources')
    @mock.patch.object(ClusterManager, '_rebuild')
    def test_update(self, mock_rebuild, mock_update_sources, mock_bootstrap):
        # Given
        cm = ClusterManager()
        cm.add_worker('host', home='/home/foo', nfs=False)

        # When
        cm.update()

        # Then
        mock_update_sources.assert_called_with('host', '/home/foo')
        mock_rebuild.assert_called_with('host', '/home/foo')

    @mock.patch.object(ClusterManager, 'add_worker')
    @mock.patch.object(ClusterManager, 'update')
    def test_cli(self, mock_update, mock_add_worker):
        # Given
        cm = ClusterManager()

        # When
        cm.cli(['-a', 'host', '--home', 'home', '--nfs'])

        # Then
        mock_add_worker.assert_called_with('host', 'home', True)

    @unittest.skipIf((sys.version_info < (3, 3)) or
                     sys.platform.startswith('win'),
                     'Test requires Python 3.x and a non-Windows system.')
    def test_remote_bootstrap_and_sync(self):
        # Given
        cm = MyClusterManager(exclude_paths=['outputs/'], testing=True)
        output_dir = os.path.join(self.root, 'outputs')
        os.makedirs(output_dir)

        # Remove the default localhost worker.
        cm.workers = []

        # When
        cm.add_worker('host', home=self.root, nfs=False)

        # Then
        self.assertEqual(len(cm.workers), 1)
        worker = cm.workers[0]
        self.assertEqual(worker['host'], 'host')
        project_name = cm.project_name
        self.assertEqual(project_name, os.path.basename(self.root))
        py = os.path.join(self.root, 'automan', 'envs', project_name,
                          'bin', 'python')
        self.assertEqual(worker['python'], py)
        chdir = os.path.join(self.root, 'automan', project_name)
        self.assertEqual(worker['chdir'], chdir)

        # Given
        cmd = ['python', '-c', 'import sys; print(sys.executable)']
        job = Job(command=cmd, output_dir=output_dir)

        s = cm.create_scheduler()

        # When
        proxy = s.submit(job)

        # Then
        wait_until(lambda: proxy.status() != 'done')

        self.assertEqual(proxy.status(), 'done')
        output = proxy.get_stdout().strip()
        self.assertEqual(os.path.realpath(output), os.path.realpath(py))

        # Test to see if updating works.

        # When
        with open(os.path.join(self.root, 'script.py'), 'w') as f:
            f.write('print("hello")\n')

        cm.update()

        # Then
        dest = os.path.join(self.root, 'automan', project_name, 'script.py')
        self.assertTrue(os.path.exists(dest))


class TestCondaClusterManager(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.cwd)
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    @mock.patch("automan.conda_cluster_manager.CondaClusterManager.CONDA_ROOT",
                'TEST_ROOT')
    def test_overloaded_methods(self):
        # Given
        cm = CondaClusterManager()

        # When/Then
        python = cm._get_python('foo', 'blah')
        name = os.path.basename(self.root)
        self.assertEqual(python, os.path.join(
            'blah', 'TEST_ROOT', 'envs/{name}/bin/python'.format(name=name)
        ))

        code = cm._get_bootstrap_code()
        self.assertTrue('TEST_ROOT' in code)

        code = cm._get_update_code()
        self.assertTrue('TEST_ROOT' in code)

        self.assertEqual(cm._get_helper_scripts(), '')


class TestEDMClusterManager(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.cwd)
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    @mock.patch("automan.edm_cluster_manager.EDMClusterManager.EDM_ROOT",
                'TEST_ROOT')
    def test_overloaded_methods(self):
        # Given
        cm = EDMClusterManager()

        # When/Then
        python = cm._get_python('foo', 'bar')
        name = os.path.basename(self.root)
        self.assertEqual(python, os.path.join(
            'bar', 'TEST_ROOT', 'envs/{name}/bin/python'.format(name=name)
        ))

        code = cm._get_bootstrap_code()
        self.assertTrue('TEST_ROOT' in code)

        code = cm._get_update_code()
        self.assertTrue('TEST_ROOT' in code)

        self.assertEqual(cm._get_helper_scripts(), '')
