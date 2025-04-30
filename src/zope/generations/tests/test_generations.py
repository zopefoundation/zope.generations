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

import doctest
import unittest

from zope.testing import cleanup


class TestSchemaManager(unittest.TestCase):

    def _getTargetClass(self):
        from zope.generations.generations import SchemaManager
        return SchemaManager

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_ctor_invalid_generation(self):
        with self.assertRaisesRegex(
                ValueError,
                'generation is less than minimum_generation'
        ):
            self._makeOne(generation=0, minimum_generation=1)

    def test_ctor_invalid_min_generation(self):
        with self.assertRaisesRegex(
                ValueError,
                'generations must be non-negative'
        ):
            self._makeOne(generation=-1, minimum_generation=-1)

    def test_ctor_invalid_generation_wo_package(self):
        with self.assertRaisesRegex(
                ValueError,
                'A package name must be supplied'
        ):
            self._makeOne(generation=1)


class TestEvolve(cleanup.CleanUp,
                 unittest.TestCase):

    def test_error_on_install_propagates(self):
        from ZODB.MappingStorage import DB

        from zope import component
        from zope import interface
        from zope.generations.generations import evolve
        from zope.generations.interfaces import IInstallableSchemaManager

        class MyException(Exception):
            pass

        @interface.implementer(IInstallableSchemaManager)
        class Manager:
            generation = 0

            def install(self, context):
                raise MyException

        component.provideUtility(Manager(), IInstallableSchemaManager)

        db = DB()
        self.addCleanup(db.close)

        with self.assertRaises(MyException):
            evolve(db)

    def test_evolve_min_twice(self):
        from ZODB.MappingStorage import DB

        from zope import component
        from zope import interface
        from zope.generations.generations import EVOLVEMINIMUM
        from zope.generations.generations import evolve
        from zope.generations.interfaces import ISchemaManager

        @interface.implementer(ISchemaManager)
        class Manager:
            generation = 1
            minimum_generation = None
            evolved = ()

            def evolve(self, context, generation):
                self.evolved += (generation,)

        manager = Manager()
        component.provideUtility(manager, ISchemaManager)

        db = DB()
        self.addCleanup(db.close)
        evolve(db, EVOLVEMINIMUM)
        # First time through we install
        self.assertEqual(manager.evolved, ())

        # Now bump the generation
        manager.generation = 2
        # And provide a minimum that's the same. We'll be called.
        manager.minimum_generation = 2

        evolve(db, EVOLVEMINIMUM)
        self.assertEqual(manager.evolved, (2,))

        # Now bump, but leave the min the same. We won't be called.
        manager.generation = 3
        evolve(db, EVOLVEMINIMUM)
        self.assertEqual(manager.evolved, (2,))


class TestEvolveExplicit(TestEvolve):

    def setUp(self):
        super().setUp()
        import transaction
        self.txm = transaction.manager
        self.txm_explicit = self.txm.explicit
        self.txm.explicit = True

    def tearDown(self):
        self.txm.explicit = self.txm_explicit


class TestSubscribers(unittest.TestCase):

    def setUp(self):
        from ZODB.MappingStorage import DB

        from zope.generations import generations
        self.evolve = generations.evolve
        generations.evolve = self.mock_evolve
        self.db = DB()
        self.expected_kind = None

    def tearDown(self):
        from zope.generations import generations
        generations.evolve = self.evolve
        self.db.close()

    def mock_evolve(self, db, kind):
        self.assertIs(db, self.db)
        self.assertEqual(kind, self.expected_kind)

    def test_evolveSubscriber(self):
        from zope.generations.generations import EVOLVE
        from zope.generations.generations import evolveSubscriber
        self.expected_kind = EVOLVE

        class Event:
            def __init__(self, db):
                self.database = db

        evolveSubscriber(Event(self.db))

    def test_evolveNotSubscriber(self):
        from zope.generations.generations import EVOLVENOT
        from zope.generations.generations import evolveNotSubscriber
        self.expected_kind = EVOLVENOT

        class Event:
            def __init__(self, db):
                self.database = db

        evolveNotSubscriber(Event(self.db))


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    flags = \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.ELLIPSIS | \
        doctest.IGNORE_EXCEPTION_DETAIL

    def setUpGeneric(test):
        cleanup.setUp()

    def tearDownGeneric(test):
        if 'db' in test.globs:
            test.globs['db'].close()
        cleanup.tearDown()

    def setUpExplicit(test):
        setUpGeneric(test)
        import transaction
        manager = test.globs['_txm'] = transaction.manager
        test.globs['_was_explicit'] = manager.explicit
        manager.explicit = True

    def tearDownExplicit(test):
        test.globs['_txm'] = test.globs['_was_explicit']
        tearDownGeneric(test)

    doc_tests = []

    for setUp, tearDown in (
            (setUpGeneric, tearDownGeneric),
            (setUpExplicit, tearDownExplicit),
    ):
        doc_tests.extend([
            doctest.DocFileSuite(
                'README.rst',
                setUp=setUp,
                tearDown=tearDown,
                package='zope.generations',
            ),
            doctest.DocTestSuite(
                'zope.generations.generations',
                optionflags=flags,
                setUp=setUp,
                tearDown=tearDown,
            ),
            doctest.DocTestSuite(
                'zope.generations.utility',
                setUp=setUp,
                tearDown=tearDown,
            ),
        ])

    suite.addTest(unittest.TestSuite(doc_tests))
    return suite
