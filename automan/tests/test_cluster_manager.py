from __future__ import print_function

import json
import os
import shutil
import sys
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from automan.cluster_manager import ClusterManager


class TestClusterManager(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        patch = mock.patch(
            'automan.cluster_manager.prompt', return_value=''
        )
        patch.start()
        self.addCleanup(patch.stop)

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

        self.assertEqual(config.get('root'), 'pysph_auto')
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
