import json
import os
import sys


def write_pysph_data(directory):
    info_fname = os.path.join(directory, 'example.info')
    data = {
        'completed': True,
        'output_dir': directory,
        'fname': 'example'
    }
    with open(info_fname, 'w') as fp:
        json.dump(data, fp)

    with open(os.path.join(directory, 'results.dat'), 'w') as fp:
        fp.write(str(sys.argv[1:]))


def main():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument(
        '-d', '--directory', default='example_output',
        help='Output directory'
    )
    p.add_argument(
        '--update-h', action="store_true", dest='update_h',
        help='Update h'
    )
    p.add_argument(
        '--no-update-h', action="store_false", dest='update_h',
        help='Do not update h'
    )
    o = p.parse_args()

    if not os.path.exists(o.directory):
        os.mkdir(o.directory)

    write_pysph_data(o.directory)


if __name__ == '__main__':
    main()
