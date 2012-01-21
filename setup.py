# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

version = '0.1.4'

#---[ START Server locking]--------------------------------------------------
LOCK_PYPI_SERVER = "http://mypypi.inqbus.de"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def check_server(server):
    if not server:
        return

    COMMANDS_WATCHED = ('register', 'upload')

    changed = False

    for command in COMMANDS_WATCHED:
        if command in sys.argv:
            # Found one command, check for -r or --repository.
            commandpos = sys.argv.index(command)
            i = commandpos + 1
            repo = None
            while i < len(sys.argv) and sys.argv[i].startswith('-'):
                # Check all following options (not commands).
                if (sys.argv[i] == '-r') or (sys.argv[i] == '--repository'):
                    # Next one is the repository itself.
                    try:
                        repo = sys.argv[i + 1]
                        if repo.lower() != server.lower():
                            print "You tried to %s to %s, while this package "\
                                  "is locked to %s" % (command, repo, server)
                            sys.exit(1)
                        else:
                            # Repo is OK.
                            pass
                    except IndexError:
                        # End of args.
                        pass
                i = i + 1

            if repo is None:
                # No repo found for the command.
                print "Adding repository %s to the command %s" % (
                    server, command)
                sys.argv[commandpos + 1: commandpos + 1] = ['-r', server]
                changed = True

    if changed:
        print "Final command: %s" % (' '.join(sys.argv))

check_server(LOCK_PYPI_SERVER)
#---[ END Server locking]----------------------------------------------------

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
        # 'plone.scale',
        'zope.app.file',
    ],
    extras_require = {
        'blobs': ['z3c.blobfile', ],
    },
)
