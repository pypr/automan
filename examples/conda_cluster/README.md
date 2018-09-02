# Conda cluster manager example

This uses the example from the tutorial but shows how it can be used
with the remote computers running conda.  The `environments.yml` is used
to create the environment and there is also an optional
`requirements.txt` which will install packages using `pip`.

The example assumes that the remote computer has its conda root in `~/miniconda3`.

To run the example, let us say you have a remote computer running Linux/Mac OS
with password-less SSH setup, let us call this computer `remote_host`, then
you can do the following:

```
   $ python automate.py -a remote_host
   [...]
   Bootstrapping remote_host succeeded!

   $ python automate.py
   [...]
```
