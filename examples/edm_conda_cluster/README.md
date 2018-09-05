# EDM and Conda cluster manager example

This uses the example from the tutorial but shows how it can be used with the
remote computers running conda or edm.

## Conda example

The `environments.yml` is used to create the environment and there is also an
optional `requirements.txt` which will install packages using `pip`.

The example assumes that the remote computer has its conda root in `~/miniconda3`.

To run the example, let us say you have a remote computer running Linux/Mac OS
with password-less SSH setup, let us call this computer `remote_host`, then
you can do the following:

```
   $ python automate_conda.py -a remote_host
   [...]
   Bootstrapping remote_host succeeded!

   $ python automate_conda.py
   [...]
```

## EDM example

The ``requirements.txt`` is used to setup the environment. We assumne that the
edm root is at ~``~/.edm``.

Note that if you have already run the ``automate_conda.py`` example the
simulations will be complete, so remove the ``outputs`` and ``manuscript``
directories first before the following. To run the example you may do:

```
   $ python automate_edm.py -a remote_host
   [...]
   Bootstrapping remote_host succeeded!

   $ python automate_edm.py
   [...]
```
