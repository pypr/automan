import os
import sys
from textwrap import dedent
import subprocess
import re

from .cluster_manager import ClusterManager


class EdmClusterManager(ClusterManager):  # pragma: no cover

    # The path to edm root on the remote, this is a relative path
    # and is relative to the home directory.
    EDM_ROOT = '.edm'

    BOOTSTRAP = dedent("""\
    #!/bin/bash

    set -e
    EDM_ROOT=%s
    ENV_FILE="{project_name}/bundled_env.json"
    EDM_EXE=~/$EDM_ROOT/bin/edm

    if ! $EDM_EXE envs exists {project_name} ; then
        if [ -f $ENV_FILE ] ; then
            $EDM_EXE -q envs import --force {project_name} -f $ENV_FILE
        else
            $EDM_EXE -q envs create --force {project_name} --version 3.6
            $EDM_EXE -q install psutil execnet -y -e {project_name}
        fi
    fi

    source ~/$EDM_ROOT/bin/edm-activate {project_name}
    pip install automan

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        pip install -r requirements.txt
    fi
    """ % EDM_ROOT)

    UPDATE = dedent("""\
    #!/bin/bash

    set -e
    EDM_ROOT=%s
    ENV_FILE="{project_name}/bundled_env.json"
    EDM_EXE=~/$EDM_ROOT/bin/edm

    if [ -f $ENV_FILE ] ; then
        $EDM_EXE -q envs import --force {project_name} -f $ENV_FILE
    fi

    source ~/$EDM_ROOT/bin/edm-activate {project_name}

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        pip install -r requirements.txt
    fi

    """ % EDM_ROOT)

    def _get_virtualenv(self):
        return None

    def _get_edm_env_root(self, host):
        cmd = [
            'ssh', host,
            '~/{edm_root}/bin/edm info'.format(edm_root=self.EDM_ROOT),
        ]
        info = subprocess.check_output(cmd).strip()
        if type(info) is bytes:
            info = info.decode('utf-8')
        info = re.split(':|\n', info)
        path = info[info.index('root directory') + 1].strip()
        return path

    def add_worker(self, host, home, nfs):
        if host == 'localhost':
            self.workers.append(dict(host=host, home=home, nfs=nfs))
        else:
            root = self.root
            curdir = os.path.basename(os.getcwd())
            if nfs:
                python = sys.executable
                chdir = curdir
            else:
                edm_root = self._get_edm_env_root(host)
                python = os.path.join(
                    edm_root, 'envs/{project_name}/bin/python'.format(
                        project_name=self.project_name
                    )
                )
                chdir = os.path.join(home, root, curdir)
            self.workers.append(
                dict(host=host, home=home, nfs=nfs, python=python, chdir=chdir)
            )

        self._write_config()
        if host != 'localhost' and not nfs:
            self._bootstrap(host, home)
