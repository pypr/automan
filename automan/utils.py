"""Utility functions for automation scripts.
"""
import collections
import itertools as IT


def dprod(a, b):
    '''Multiplies the given list of dictionaries `a` and `b`.

    This makes a list of new dictionaries which is the product of the given
    two dictionaries.

    **Example**

    >>> dprod(mdict(a=[1, 2], b=['xy']), mdict(c='ab'))
    [{'a': 1, 'b': 'xy', 'c': 'a'},
     {'a': 1, 'b': 'xy', 'c': 'b'},
     {'a': 2, 'b': 'xy', 'c': 'a'},
     {'a': 2, 'b': 'xy', 'c': 'b'}]

    '''
    return [
        dict(IT.chain(x.items(),  y.items())) for x, y in IT.product(a, b)
    ]


def styles(sims):
    """Cycles over a set of possible styles to use for plotting.

    The method is passed a sequence of the Simulation instances. This should
    return an iterator which produces a dictionary each time containing a set
    of keyword arguments to be used for a particular plot.

    **Parameters**

    sims: sequence
        Sequence of `Simulation` objects.

    **Returns**

    An iterator which produces a dictionary containing a set of kwargs to be
    used for the plotting. Can also return an iterable containing
    dictionaries.

    """
    ls = [dict(color=x[0], linestyle=x[1]) for x in
          IT.product("kbgr", ["-", "--", "-.", ":"])]
    return IT.cycle(ls)


def compare_runs(sims, method, labels, exact=None, styles=styles):
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
    styles: callable: returns an iterator/iterable of style keyword arguments.
        Defaults to the ``styles`` function defined in this module.
    """
    ls = styles(sims)
    if isinstance(ls, collections.abc.Iterable):
        ls = iter(ls)
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


def mdict(**kw):
    '''Expands out the passed kwargs into a list of dictionaries.

    Each kwarg value is expected to be a sequence. The resulting list of
    dictionaries is the product of the different values and the same keys.

    **Example**

    >>> mdict(a=[1, 2], b='xy')
    [{'a': 1, 'b': 'x'},
     {'a': 1, 'b': 'y'},
     {'a': 2, 'b': 'x'},
     {'a': 2, 'b': 'y'}]

    '''
    keys = list(kw.keys())
    return [dict(zip(keys, opts)) for opts in IT.product(*kw.values())]


def opts2path(opts, keys=None, ignore=None, kmap=None):
    '''Renders the given options as a path name.

    **Parameters**

    opts: dict
        dictionary of options
    keys: list
        Keys of the options use.
    ignore: list
        Ignore these keys in the options.
    kmap: dict
        map the key names through this dict.

    **Examples**

    >>> opts2path(dict(x=1, y='hello', z=0.1))
    'x_1_hello_z_0.1'
    >>> opts2path(dict(x=1, y='hello', z=0.1), keys=['x'])
    'x_1'
    >>> opts2path(dict(x=1, y='hello', z=0.1), ignore=['x'])
    'hello_z_0.1'
    >>> opts2path(dict(x=1, y='hello', z=0.1), kmap=dict(x='XX'))
    'XX_1_hello_z_0.1'
    '''
    keys = set(opts.keys()) if keys is None else set(keys)
    ignore = [] if ignore is None else ignore
    keymap = {} if kmap is None else kmap
    for x in ignore:
        keys.discard(x)
    keys = sorted(x for x in keys if x in opts)

    def _key2name(k):
        v = opts[k]
        r = keymap.get(k, '')
        if r:
            return f'{r}_{v}'
        elif isinstance(v, str):
            return v
        else:
            return f'{k}_{v}'

    return '_'.join([_key2name(k) for k in keys])
