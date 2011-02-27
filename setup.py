# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import os

version = '0.1.1'

setup(
    name='z3c.namedfile',
    version=version,
    description="File types and fields for images, files and blob files " \
                "with filenames.",
    long_description=open("README.txt").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='zope named file image blob',
    author='Thomas Massmann',
    author_email='thomas.massmann@inqbus.de',
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
    ],
    extras_require = {
        'blobs': ['z3c.blobfile', ],
#         'scales': ['plone.scale[storage] >=1.1dev', ],
    },
    entry_points={
    },
)
