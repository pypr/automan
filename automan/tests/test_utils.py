from unittest import mock
from automan.automation import Simulation
from automan.utils import (compare_runs, dprod, filter_cases, mdict,
                           opts2path)


def test_compare_runs_calls_methods_when_given_names():
    # Given
    sims = [mock.MagicMock(), mock.MagicMock()]
    s0, s1 = sims
    s0.get_labels.return_value = s1.get_labels.return_value = 'label'

    # When
    compare_runs(sims, 'fig', labels=['x'], exact='exact')

    # Then
    s0.exact.assert_called_once_with(color='k', linestyle='-')
    s0.fig.assert_called_once_with(color='k', label='label', linestyle='--')
    s0.get_labels.assert_called_once_with(['x'])
    assert s1.exact.called is False
    s1.fig.assert_called_once_with(color='k', label='label', linestyle='-.')
    s1.get_labels.assert_called_once_with(['x'])


def test_compare_runs_works_when_given_callables():
    # Given
    sims = [mock.MagicMock()]
    s0 = sims[0]
    s0.get_labels.return_value = 'label'

    func = mock.MagicMock()
    exact = mock.MagicMock()

    # When
    compare_runs(sims, func, labels=['x'], exact=exact)

    # Then
    exact.assert_called_once_with(s0, color='k', linestyle='-')
    func.assert_called_once_with(s0, color='k', label='label', linestyle='--')
    s0.get_labels.assert_called_once_with(['x'])


def test_compare_runs_uses_given_styles():
    # Given
    sims = [mock.MagicMock()]
    s0 = sims[0]
    s0.get_labels.return_value = 'label'

    func = mock.MagicMock()
    styles = mock.MagicMock()
    styles.return_value = iter([dict(linestyle=':', color='b')])

    # When
    compare_runs(sims, func, labels=['x'], styles=styles)

    # Then
    func.assert_called_once_with(s0, color='b', label='label', linestyle=':')
    s0.get_labels.assert_called_once_with(['x'])
    styles.assert_called_once_with()


def test_dprod():
    # Given/When
    res = dprod(mdict(a=[1, 2], b=['xy']), mdict(c='ab'))
    # Then
    exp = [{'a': 1, 'b': 'xy', 'c': 'a'},
           {'a': 1, 'b': 'xy', 'c': 'b'},
           {'a': 2, 'b': 'xy', 'c': 'a'},
           {'a': 2, 'b': 'xy', 'c': 'b'}]
    assert res == exp


def test_filter_cases_works_with_params():
    # Given
    sims = [Simulation(root='', base_command='python', param1=i, param2=i+1)
            for i in range(5)]
    # When
    result = filter_cases(sims, param1=2)

    # Then
    assert len(result) == 1
    assert result[0].params['param1'] == 2

    # When
    result = filter_cases(sims, param1=2, param2=2)

    # Then
    assert len(result) == 0

    # When
    result = filter_cases(sims, param1=3, param2=4)

    # Then
    assert len(result) == 1
    assert result[0].params['param1'] == 3
    assert result[0].params['param2'] == 4


def test_filter_cases_works_with_predicate():
    # Given
    sims = [Simulation(root='', base_command='python', param1=i, param2=i+1)
            for i in range(5)]

    # When
    result = filter_cases(
        sims, predicate=lambda x: x.params.get('param1', 0) % 2
    )

    # Then
    assert len(result) == 2
    assert result[0].params['param1'] == 1
    assert result[1].params['param1'] == 3

    # When
    result = filter_cases(
        sims, predicate=2
    )

    # Then
    assert len(result) == 0

    # Given
    sims = [Simulation(root='', base_command='python', predicate=i)
            for i in range(5)]

    # When
    result = filter_cases(
        sims, predicate=2
    )

    # Then
    assert len(result) == 1
    assert result[0].params['predicate'] == 2


def test_mdict():
    exp = [{'a': 1, 'b': 'x'},
           {'a': 1, 'b': 'y'},
           {'a': 2, 'b': 'x'},
           {'a': 2, 'b': 'y'}]
    assert mdict(a=[1, 2], b='xy') == exp


def test_opts2path():
    assert opts2path(dict(x=1, y='hello', z=0.1)) == 'x_1_hello_z_0.1'
    assert opts2path(dict(x=1, y='hello', z=0.1), keys=['x']) == 'x_1'
    res = opts2path(dict(x=1, y='hello', z=0.1), ignore=['x'])
    assert res == 'hello_z_0.1'
    res = opts2path(dict(x=1, y='hello', z=0.1), kmap=dict(x='XX'))
    assert res == 'XX_1_hello_z_0.1'
