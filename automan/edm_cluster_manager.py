import os
from textwrap import dedent

from .cluster_manager import ClusterManager


class EDMClusterManager(ClusterManager):

    # The path to edm root on the remote, this is a relative path
    # and is relative to the home directory.
    EDM_ROOT = '.edm'

    ENV_FILE = "bundled_env.json"

    BOOTSTRAP = dedent("""\
    #!/bin/bash

    set -e
    ENV_FILE="{project_name}/{env_file}"

    if hash edm 2>/dev/null; then
        EDM_EXE=edm
    else
        EDM_EXE=~/{edm_root}/bin/edm
    fi

    if [ -f $ENV_FILE ] ; then
        $EDM_EXE -q envs import --force {project_name} -f $ENV_FILE
    else
        $EDM_EXE -q envs create --force {project_name} --version 3.6
        $EDM_EXE -q install psutil execnet -y -e {project_name}
    fi

    $EDM_EXE run -e {project_name} -- pip install automan

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        $EDM_EXE run -e {project_name} -- pip install -r requirements.txt
    fi
    """)

    UPDATE = dedent("""\
    #!/bin/bash

    set -e
    ENV_FILE="{project_name}/{env_file}"

    if hash edm 2>/dev/null; then
        EDM_EXE=edm
    else
        EDM_EXE=~/{edm_root}/bin/edm
    fi

    if [ -f $ENV_FILE ] ; then
        $EDM_EXE -q envs import --force {project_name} -f $ENV_FILE
    fi

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        $EDM_EXE run -e {project_name} -- pip install -r requirements.txt
    fi
    """)

    def _get_bootstrap_code(self):
        return self.BOOTSTRAP.format(
            project_name=self.project_name, edm_root=self.EDM_ROOT,
            env_file=self.ENV_FILE
        )

    def _get_python(self, host, home):
        return os.path.join(
            home, self.EDM_ROOT,
            'envs/{project_name}/bin/python'.format(
                project_name=self.project_name
            )
        )

    def _get_update_code(self):
        return self.UPDATE.format(
            project_name=self.project_name, edm_root=self.EDM_ROOT,
            env_file=self.ENV_FILE
        )

    def _get_helper_scripts(self):
        """Return a space separated string of script files that you need copied over to
        the remote host.

        When overriding this, you can return None or '' if you do not need any.

        """
        return ''
