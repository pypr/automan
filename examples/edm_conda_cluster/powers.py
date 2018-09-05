import argparse
import os

import numpy as np


def compute_powers(r_max, power):
    """Compute the powers of the integers upto r_max and return the result.
    """
    result = []
    for i in range(0, r_max + 1):
        result.append((i, i**power))
    x = np.arange(0, r_max + 1)
    y = np.power(x, power)
    return x, y


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--power', type=float, default=2.0,
        help='Power to calculate'
    )
    p.add_argument(
        '--max', type=int, default=10,
        help='Maximum integer that we must raise to the given power'
    )
    p.add_argument(
        '--output-dir', type=str, default='.',
        help='Output directory to generate file.'
    )
    opts = p.parse_args()

    x, y = compute_powers(opts.max, opts.power)

    fname = os.path.join(opts.output_dir, 'results.npz')
    np.savez(fname, x=x, y=y)


if __name__ == '__main__':
    main()
