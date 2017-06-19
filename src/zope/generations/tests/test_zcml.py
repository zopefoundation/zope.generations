##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
""" Tests that ZCML can be loaded.
"""
import unittest


class ZCMLTests(unittest.TestCase):

    from zope.component.testing import setUp  # noqa
    from zope.component.testing import tearDown  # noqa

    def test_loadable(self):
        # N.B.:  this test deliberately avoids any "ftesting" / layers
        #        support:  its purpose is to ensure that the package's
        #        ZCML file is loadable *without* loading any other ZCML.
        import zope.configuration.xmlconfig
        import zope.generations
        zope.configuration.xmlconfig.file(
            'configure.zcml', package=zope.generations)
        zope.configuration.xmlconfig.file(
            'subscriber.zcml', package=zope.generations)
