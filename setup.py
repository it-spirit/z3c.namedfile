# -*- coding: utf-8 -*-
"""Installer for the z3c.namedfile package."""

from setuptools import find_packages
from setuptools import setup


version = '0.4.dev0'
description = (
    'File types and fields for images, files and blob files with '
    'filenames.'
)
long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'zope.app.file',
]

test_requires = [
    'Pillow',
]

setup(
    name='z3c.namedfile',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Zope',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='zope named file image blob',
    author='it-spirit',
    author_email='development@it-spir.it',
    url='https://github.com/it-spirit/z3c.namedfile',
    download_url='https://pypi.python.org/pypi/z3c.namedfile',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'blobs': [
            'z3c.blobfile',
        ],
        'test': test_requires,
    },
)
