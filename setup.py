from setuptools import setup, find_packages
import sys


def get_version():
    import os
    data = {}
    fname = os.path.join('automan', '__init__.py')
    exec(compile(open(fname).read(), fname, 'exec'), data)
    return data.get('__version__')


install_requires = ['psutil', 'execnet']
tests_require = ['pytest']
if sys.version_info.major < 3:
    tests_require.append('mock')
    install_requires.append('mock')

classes = """
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: End Users/Desktop
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries
Topic :: Utilities
"""

classifiers = [x.strip() for x in classes.splitlines() if x]

setup(
    name='automan',
    version=get_version(),
    author='Prabhu Ramachandran',
    author_email='prabhu@aero.iitb.ac.in',
    description='A simple Python-based automation framework.',
    long_description=open('README.rst').read(),
    license="BSD",
    url='https://github.com/pypr/automan',
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'automan': 'automan'},
)
