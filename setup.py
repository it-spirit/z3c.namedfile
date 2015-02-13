# -*- coding: utf-8 -*-
"""Setup for z3c.namedfile package."""
from setuptools import setup, find_packages
import os

version = '0.2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
)

setup(
    name='z3c.namedfile',
    version=version,
    description='File types and fields for images, files and blob files '
                'with filenames.',
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='zope named file image blob',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='http://pypi.python.org/pypi/z3c.namedfile',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        # 'plone.scale',
        'zope.app.file',
    ],
    extras_require={
        'blobs': [
            'z3c.blobfile',
        ],
        'scales': [
            'plone.scale',
        ],
        'test': [],
    },
)
