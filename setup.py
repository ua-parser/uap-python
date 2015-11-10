#!/usr/bin/env python
from setuptools import setup
from setuptools.command.develop import develop as _develop
from setuptools.command.sdist import sdist as _sdist
import subprocess


def install_regexes():
    print('Copying regexes.yaml to package directory...')
    import os
    cwd = os.path.abspath(os.path.dirname(__file__))
    yaml_src = os.path.join(cwd, 'uap-core', 'regexes.yaml')
    if not os.path.exists(yaml_src):
        raise RuntimeError(
            'Unable to find regexes.yaml, should be at %r' % yaml_src)

    print('Converting regexes.yaml to regexes.json...')
    import json
    import yaml
    json_dest = os.path.join(cwd, 'ua_parser', 'regexes.json')
    with open(yaml_src, 'rb') as fp:
        regexes = yaml.safe_load(fp)
    with open(json_dest, "w") as f:
        json.dump(regexes, f)


def checkout_submodule():
    print("Checkout submodule - uap-core")
    return subprocess.check_output(['git', 'submodule', 'update', '--init'])


class develop(_develop):
    def run(self):
        checkout_submodule()
        install_regexes()
        _develop.run(self)


class sdist(_sdist):
    def run(self):
        checkout_submodule()
        install_regexes()
        _sdist.run(self)


setup(
    name='ua-parser',
    version='0.5.0',
    description="Python port of Browserscope's user agent parser",
    author='PBS',
    author_email='no-reply@pbs.org',
    packages=['ua_parser'],
    package_dir={'': '.'},
    license='LICENSE.txt',
    zip_safe=False,
    url='https://github.com/ua-parser/uap-python',
    include_package_data=True,
    package_data={'ua_parser': ['regexes.json']},
    setup_requires=['pyyaml'],
    install_requires=[],
    cmdclass={
        'develop': develop,
        'sdist': sdist,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
