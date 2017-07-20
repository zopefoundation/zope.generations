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
import re
import unittest
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 2 bytes has no "b".
    (re.compile("b('.*?')"),
     r"\1"),
    (re.compile('b(".*?")'),
     r"\1"),
    (re.compile('ModuleNotFoundError:'), 'ImportError:'),
    (re.compile(
        "No module named '?zope.nonexistingmodule'?"),
     'No module named nonexistingmodule'),
])


def tearDownREADME(test):
    zope.component.testing.tearDown(test)
    test.globs['db'].close()


def test_suite():
    flags = \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.ELLIPSIS | \
        doctest.IGNORE_EXCEPTION_DETAIL
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=zope.component.testing.setUp,
            tearDown=tearDownREADME,
            package='zope.generations',
            checker=checker
            ),
        doctest.DocTestSuite(
                'zope.generations.generations',
                checker=checker, optionflags=flags),
        doctest.DocTestSuite(
                'zope.generations.utility'),
        ))
