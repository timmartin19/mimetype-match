from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup, find_packages

version = '1.0.1'

setup(
    author='Tim Martin',
    author_email='tim.martin@vertical-knowledge.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='A tool to make finding the appropriate mimetype to return easy',
    entry_points={
        'console_scripts': [
            'mimetype-match = accept_header_match:cli'
        ]
    },
    extras_require={
        'dev': [
            'sphinx',
            'zest.releaser'
        ]
    },
    install_requires=[
        'six'
    ],
    keywords='HTTP python Accept Header HTTP_ACCEPT mimetype match Content-Type content type',
    name='mimetype-match',
    packages=find_packages(include=['accept_header_match']),
    tests_require=[
        'mock',
        'tox',
        'unittest2'
    ],
    test_suite="tests",
    url='https://github.com/timmartin19/mimetype-match',
    version=version
)
