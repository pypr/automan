import os
import sys
from textwrap import dedent
import subprocess

from .cluster_manager import ClusterManager


class CondaClusterManager(ClusterManager):  # pragma: no cover

    # The path to conda root on the remote, this is a relative path
    # and is relative to the home directory.
    CONDA_ROOT = 'miniconda3'

    BOOTSTRAP = dedent("""\
    #!/bin/bash

    set -e
    CONDA_ROOT=%s
    ENV_FILE="{project_name}/environments.yml"
    if [ -f $ENV_FILE ] ; then
        ~/$CONDA_ROOT/bin/conda env create -q -f $ENV_FILE -n {project_name}
    else
        ~/$CONDA_ROOT/bin/conda create -y -q -n {project_name} psutil execnet
    fi

    source ~/$CONDA_ROOT/bin/activate {project_name}
    pip install automan

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        pip install -r requirements.txt
    fi
    """ % CONDA_ROOT)

    UPDATE = dedent("""\
    #!/bin/bash

    set -e
    CONDA_ROOT=%s
    ENV_FILE="{project_name}/environments.yml"
    if [ -f $ENV_FILE ] ; then
        ~/$CONDA_ROOT/bin/conda env update -q -f $ENV_FILE -n {project_name}
    fi

    source ~/$CONDA_ROOT/bin/activate {project_name}

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        pip install -r requirements.txt
    fi

    """ % CONDA_ROOT)

    def _get_virtualenv(self):
        return None

    def _get_conda_env_root(self, host):
        cmd = [
            'ssh', host,
            '~/{conda_root}/bin/conda info --base'.format(
                conda_root=self.CONDA_ROOT
            )
        ]
        path = subprocess.check_output(cmd).strip()
        if type(path) is bytes:
            path = path.decode('utf-8')
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
                conda_root = self._get_conda_env_root(host)
                python = os.path.join(
                    conda_root, 'envs/{project_name}/bin/python'.format(
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
