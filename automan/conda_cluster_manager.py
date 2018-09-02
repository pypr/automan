import os
from textwrap import dedent

from .cluster_manager import ClusterManager


class CondaClusterManager(ClusterManager):

    # The path to conda root on the remote, this is a relative path
    # and is relative to the home directory.
    CONDA_ROOT = 'miniconda3'

    BOOTSTRAP = dedent("""\
    #!/bin/bash

    set -e
    CONDA_ROOT={conda_root}
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
    """)

    UPDATE = dedent("""\
    #!/bin/bash

    set -e
    CONDA_ROOT={conda_root}
    ENV_FILE="{project_name}/environments.yml"
    if [ -f $ENV_FILE ] ; then
        ~/$CONDA_ROOT/bin/conda env update -q -f $ENV_FILE -n {project_name}
    fi

    source ~/$CONDA_ROOT/bin/activate {project_name}

    cd {project_name}
    if [ -f "requirements.txt" ] ; then
        pip install -r requirements.txt
    fi
    """)

    def _get_bootstrap_code(self):
        return self.BOOTSTRAP.format(
            project_name=self.project_name, conda_root=self.CONDA_ROOT
        )

    def _get_python(self, host, home):
        return os.path.join(
            home, self.CONDA_ROOT,
            'envs/{project_name}/bin/python'.format(
                project_name=self.project_name
            )
        )

    def _get_update_code(self):
        return self.UPDATE.format(
            project_name=self.project_name, conda_root=self.CONDA_ROOT
        )

    def _get_helper_scripts(self):
        """Return a space separated string of script files that you need copied over to
        the remote host.

        When overriding this, you can return None or '' if you do not need any.

        """
        return ''
