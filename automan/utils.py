"""Utility functions handy when creating automation scripts.
"""
import itertools


def linestyles():
    """Cycles over a set of possible linestyles to use for plotting.
    """
    ls = [dict(color=x[0], linestyle=x[1]) for x in
          itertools.product("kbgr", ["-", "--", "-.", ":"])]
    return itertools.cycle(ls)


def compare_runs(sims, method, labels, exact=None, linestyles=linestyles):
    """Given a sequence of Simulation instances, a method name, the labels to
    compare and an optional method name for an exact solution, this calls the
    methods with the appropriate parameters for each simulation.

    **Parameters**

    sims: sequence
        Sequence of `Simulation` objects.
    method: str or callable
        Name of a method on each simulation method to call for plotting.
        Or a callable which is passed the simulation instance and any kwargs.
    labels: sequence
        Sequence of parameters to use as labels for the plot.
    exact: str or callable
        Name of a method that produces an exact solution plot
        or a callable that will be called.
    linestyles: callable: returns an iterator of linestyle keyword arguments.
        Defaults to the ``linestyles`` function defined in this module.
    """
    ls = linestyles()
    if exact is not None:
        if isinstance(exact, str):
            getattr(sims[0], exact)(**next(ls))
        else:
            exact(sims[0], **next(ls))
    for s in sims:
        if isinstance(method, str):
            m = getattr(s, method)
            m(label=s.get_labels(labels), **next(ls))
        else:
            method(s, label=s.get_labels(labels), **next(ls))


def filter_cases(runs, predicate=None, **params):
    """Given a sequence of simulations and any additional parameters, filter
    out all the cases having exactly those parameters and return a list of
    them.

    One may also pass a callable to filter the cases using the `predicate`
    keyword argument. If this is not a callable, it is treated as a parameter.
    If `predicate` is passed though, the other keyword arguments are ignored.

    """
    if predicate is not None:
        if callable(predicate):
            return list(filter(predicate, runs))
        else:
            params['predicate'] = predicate

    def _check_match(run):
        for param, expected in params.items():
            if param not in run.params or run.params[param] != expected:
                return False
        return True

    return list(filter(_check_match, runs))


def filter_by_name(cases, names):
    """Filter a sequence of Simulations by their names.  That is, if the case
    has a name contained in the given `names`, it will be selected.
    """
    if isinstance(names, str):
        names = [names]
    return sorted(
        [x for x in cases if x.name in names],
        key=lambda x: names.index(x.name)
    )
