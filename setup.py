##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.generations package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.generations',
      version='3.6.1dev',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Application Schema Generations',
      long_description=(
          read('README.txt')
          + '\n\n.. contents::\n\n' +
          '======================\n'
          'Detailed Documentation\n'
          '======================\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'generations', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 zodb schema generation",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.app.generations',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=[
          'zope.app.testing',
          'zope.app.zcmlfiles',
          'zope.login',
          'zope.publisher >= 3.12',
          'zope.securitypolicy',
          ]),
      install_requires=['setuptools',
                        'zope.app.renderer',
                        'zope.interface',
                        'zope.app.publication',
                        'ZODB3',
                        'zope.processlifetime',
                        'zope.applicationcontrol',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
