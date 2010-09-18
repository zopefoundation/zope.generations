##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Schema-generation tests."""

import zope.component.testing
import doctest
import unittest


def tearDownREADME(test):
    zope.component.testing.tearDown(test)
    test.globs['db'].close()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=zope.component.testing.setUp,
            tearDown=tearDownREADME,
            package='zope.generations',
            ),
        doctest.DocTestSuite('zope.generations.generations'),
        doctest.DocTestSuite('zope.generations.utility'),
        ))
