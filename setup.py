# -*- coding: utf-8 -*-
"""Setup for z3c.namedfile package."""

from setuptools import (
    find_packages,
    setup,
)

version = '0.4.dev0'
description = 'File types and fields for images, files and blob files ' \
              'with filenames.'

long_description = ('\n'.join([
    open('README.rst').read(),
    'Contributors',
    '------------\n',
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
]))

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'zope.app.file',
]

setup(
    name='z3c.namedfile',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Zope",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='zope named file image blob',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://bitbucket.org/it_spirit/z3c.namedfile',
    download_url='http://pypi.python.org/pypi/z3c.namedfile',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=dict(
        blobs=[
            'z3c.blobfile',
        ],
        test=[
            'Pillow',
        ],
    ),
)
