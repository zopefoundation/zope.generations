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
"""Backward compatibility tests."""

import unittest

class BackwardCompatibilityTests(unittest.TestCase):

    def setUp(self):
        from zope.generations.generations import old_generations_key
        import ZODB.tests.util
        import persistent.mapping
        import transaction

        self.db = ZODB.tests.util.DB(database_name='testdb')
        self.conn = self.db.open()
        self.root = self.conn.root()
        generation_data = persistent.mapping.PersistentMapping()
        generation_data['app1'] = 3
        # Create a database using the old generations key:
        self.root[old_generations_key] = generation_data
        transaction.commit()

    def tearDown(self):
        import transaction

        transaction.abort()
        self.conn.close()
        self.db.close()

    def test_upgrade(self):
        # When evolve is called on a database which contains the old
        # generations key, it gets copied over to the new one:
        from zope.generations.generations import (
            evolve, generations_key, old_generations_key)

        evolve(self.db)
        self.assertEqual(self.root[old_generations_key],
                         self.root[generations_key])

        # The two dicts are the same, so changing one changes the other one,
        # too:
        self.root[old_generations_key]['app2'] = 2411
        self.assertEqual(2411, self.root[generations_key]['app2'])
