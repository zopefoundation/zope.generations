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
"""Support for application database generations."""
import logging
import transaction
import zope.component
import zope.interface

from .interfaces import GenerationTooHigh, GenerationTooLow, UnableToEvolve
from .interfaces import ISchemaManager, IInstallableSchemaManager


logger = logging.getLogger('zope.generations')
old_generations_key = 'zope.app.generations'
generations_key = 'zope.generations'


@zope.interface.implementer(IInstallableSchemaManager)
class SchemaManager(object):
    """Schema manager

       Schema managers implement `IInstallableSchemaManager` using
       scripts provided as module methods.  You create a schema
       manager by providing mimumum and maximum generations and a
       package providing modules named ``evolveN``, where ``N`` is a
       generation number.  Each module provides a function, ``evolve``
       that evolves a database from the previous generation.

       For the sake of the example, we'll use the demo package defined
       in here. See the modules there for simple examples of evolution
       scripts.

       So, if we'll create a SchemaManager:

         >>> manager = SchemaManager(1, 3, 'zope.generations.demo')

       and we'll create a test database and context:

         >>> from ZODB.MappingStorage import DB
         >>> db = DB()
         >>> context = Context()
         >>> context.connection = db.open()

       Then we'll evolve the database from generation 1 to 3:

         >>> import transaction
         >>> tx = transaction.begin()
         >>> manager.evolve(context, 2)
         >>> manager.evolve(context, 3)
         >>> tx.commit()

       The demo evolvers simply record their data in a root key:

         >>> from zope.generations.demo import key
         >>> tx = transaction.begin()
         >>> conn = db.open()
         >>> conn.root()[key]
         (2, 3)

       You can get the information for each evolver by specifying the
       destination generation of the evolver as argument to the `getInfo()`
       method:

         >>> manager.getInfo(1)
         'Evolver 1'
         >>> manager.getInfo(2)
         'Evolver 2'
         >>> manager.getInfo(3) is None
         True

       If a package provides an install script, then it will be called
       when the manager's intall method is called:

         >>> tx.abort()
         >>> tx = transaction.begin()
         >>> del conn.root()[key]
         >>> tx.commit()
         >>> tx = transaction.begin()
         >>> conn.root().get(key)

         >>> manager.install(context)
         >>> tx.commit()
         >>> tx = transaction.begin()
         >>> conn.root()[key]
         ('installed',)

       If there is not install script, the manager will do nothing on
       an install:

         >>> manager = SchemaManager(1, 3, 'zope.generations.demo2')
         >>> manager.install(context)

       We handle ImportErrors within the script specially, so they get
       promoted:

         >>> manager = SchemaManager(1, 3, 'zope.generations.demo3')
         >>> manager.install(context)
         Traceback (most recent call last):
         ImportError: No module named nonexistingmodule

       We'd better clean up:

         >>> tx.abort()
         >>> context.connection.close()
         >>> conn.close()
         >>> db.close()


       """

    def __init__(self, minimum_generation=0, generation=0, package_name=None):
        if generation < minimum_generation:
            raise ValueError("generation is less than minimum_generation",
                             generation, minimum_generation)
        if minimum_generation < 0:
            raise ValueError("generations must be non-negative",
                             minimum_generation)

        if generation and not package_name:
            raise ValueError("A package name must be supplied if the"
                             " generation is non-zero")

        self.minimum_generation = minimum_generation
        self.generation = generation
        self.package_name = package_name

    def evolve(self, context, generation):
        """Evolve a database to reflect software/schema changes."""
        name = "%s.evolve%d" % (self.package_name, generation)

        evolver = __import__(name, {}, {}, ['*'])

        evolver.evolve(context)

    def install(self, context):
        """Evolve a database to reflect software/schema changes."""
        if self.package_name is None:
            return

        name = "%s.install" % self.package_name

        try:
            evolver = __import__(name, {}, {}, ['*'])
        except ImportError as m:
            if str(m) not in ('No module named %s' % name,
                              "No module named '%s'" % name,
                              'No module named install'):
                # This was an import error *within* the module, so we re-raise.
                raise
        else:
            evolver.evolve(context)

    def getInfo(self, generation):
        """Get the information from the evolver function's doc string."""
        evolver = __import__(
            "%s.evolve%d" % (self.package_name, generation),
            {}, {}, ['*'])
        return evolver.evolve.__doc__


class Context(object):
    connection = None


def findManagers():
    # Hook to let Chris use this for Zope 2
    return zope.component.getUtilitiesFor(ISchemaManager)


def PersistentDict():
    # Another hook to let Chris use this for Zope 2
    import persistent.mapping
    return persistent.mapping.PersistentMapping()


#: Constant for the *how* argument to `evolve` indicating
#: to evolve to the current generation.
#:
#: .. seealso:: `evolveSubscriber`
EVOLVE = 'EVOLVE'
#: Constant for the *how* argument to `evolve` indicating
#: to perform no evolutions.
#:
#: .. seealso:: `evolveNotSubscriber`
EVOLVENOT = 'EVOLVENOT'
#: Constant for the *how* argument to `evolve` indicating
#: to evolve to the minimum required generation.
#:
#: .. seealso:: `evolveMinimumSubscriber`
EVOLVEMINIMUM = 'EVOLVEMINIMUM'


def evolve(db, how=EVOLVE):
    """Evolve a database

    We evolve a database using registered application schema managers.
    Here's an example (silly) schema manager:

      >>> from zope.generations.interfaces import ISchemaManager
      >>> @zope.interface.implementer(ISchemaManager)
      ... class FauxApp(object):
      ...
      ...     erron = None # Raise an error is asked to evolve to this
      ...
      ...     def __init__(self, name, minimum_generation, generation):
      ...         self.name, self.generation = name, generation
      ...         self.minimum_generation = minimum_generation
      ...
      ...     def evolve(self, context, generation):
      ...         if generation == self.erron:
      ...             raise ValueError(generation)
      ...
      ...         context.connection.root()[self.name] = generation

    Evolving a database will cause log messages to be written, so we need a
    logging handler:

      >>> from zope.testing import loggingsupport
      >>> loghandler = loggingsupport.InstalledHandler('zope.generations')
      >>> def print_log():
      ...    print(loghandler)
      ...    loghandler.clear()

    Now, we'll create and register some handlers:

      >>> import zope.component
      >>> app1 = FauxApp('app1', 0, 1)
      >>> zope.component.provideUtility(app1, ISchemaManager, name='app1')
      >>> app2 = FauxApp('app2', 5, 11)
      >>> zope.component.provideUtility(app2, ISchemaManager, name='app2')

    If we create a new database, and evolve it, we'll simply update
    the generation data:

      >>> from ZODB.MappingStorage import DB
      >>> db = DB(database_name='testdb')
      >>> evolve(db)
      >>> conn = db.open()
      >>> root = conn.root()
      >>> root[generations_key]['app1']
      1
      >>> root[generations_key]['app2']
      11

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVE

    But nothing will have been done to the database:

      >>> root.get('app1')
      >>> root.get('app2')

    Now if we increase the generation of one of the apps:

      >>> app1.generation += 1
      >>> evolve(db)

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVE
      zope.generations INFO
        testdb/app1: currently at generation 1, targetting generation 2
      zope.generations DEBUG
        testdb/app1: evolving to generation 2
      zope.generations DEBUG
        testdb/app2: up-to-date at generation 11

    We'll see that the generation data has updated:

      >>> root[generations_key]['app1']
      2
      >>> root[generations_key]['app2']
      11

    And that the database was updated for that application:

      >>> root.get('app1')
      2
      >>> root.get('app2')

    And that the transaction record got a note

      >>> [it.description for it in conn.db().storage.iterator()][-1]
      u'app1: evolving to generation 2'

    If there is an error updating a particular generation, but the
    generation is greater than the minimum generation, then we won't
    get an error from evolve, but we will get a log message.

      >>> app1.erron = 4
      >>> app1.generation = 7
      >>> evolve(db)

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVE
      zope.generations INFO
        testdb/app1: currently at generation 2, targetting generation 7
      zope.generations DEBUG
        testdb/app1: evolving to generation 3
      zope.generations DEBUG
        testdb/app1: evolving to generation 4
      zope.generations ERROR
        testdb/app1: failed to evolve to generation 4
      zope.generations DEBUG
        testdb/app2: up-to-date at generation 11

    The database will have been updated for previous generations:

      >>> root[generations_key]['app1']
      3
      >>> root.get('app1')
      3

    If we set the minimum generation for app1 to something greater than 3:

      >>> app1.minimum_generation = 4

    Then we'll get an error if we try to evolve, since we can't get
    past 3 and 3 is less than 4:

      >>> evolve(db)
      Traceback (most recent call last):
      ...
      UnableToEvolve: (4, u'app1', 7)

    We'll also get a log entry:

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVE
      zope.generations INFO
        testdb/app1: currently at generation 3, targetting generation 7
      zope.generations DEBUG
        testdb/app1: evolving to generation 4
      zope.generations ERROR
        testdb/app1: failed to evolve to generation 4

    So far, we've used evolve in its default policy, in which we evolve
    as far as we can up to the current generation.  There are two
    other policies:

    EVOLVENOT -- Don't evolve, but make sure that the application is
      at the minimum generation

    EVOLVEMINIMUM -- Evolve only to the minimum generation

    Let's change unset erron for app1 so we don't get an error when we
    try to evolve.

      >>> app1.erron = None

    Now, we'll call evolve with EVOLVENOT:

      >>> evolve(db, EVOLVENOT)
      Traceback (most recent call last):
      ...
      GenerationTooLow: (3, u'app1', 4)

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVENOT
      zope.generations ERROR
        testdb/app1: current generation too low (3 < 4) but mode is EVOLVENOT

    We got an error because we aren't at the minimum generation for
    app1.  The database generation for app1 is still 3 because we
    didn't do any evolution:

      >>> root[generations_key]['app1']
      3
      >>> root.get('app1')
      3

    Now, if we use EVOLVEMINIMUM instead, we'll evolve to the minimum
    generation:

      >>> evolve(db, EVOLVEMINIMUM)
      >>> root[generations_key]['app1']
      4
      >>> root.get('app1')
      4

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVEMINIMUM
      zope.generations INFO
        testdb/app1: currently at generation 3, targetting generation 4
      zope.generations DEBUG
        testdb/app1: evolving to generation 4
      zope.generations DEBUG
        testdb/app2: up-to-date at generation 11

    If we happen to install an app that has a generation that is less
    than the database generation, we'll get an error, because there is
    no way to get the database to a generation that the app
    understands:

      >>> app1.generation = 2
      >>> app1.minimum_generation = 0
      >>> evolve(db)
      Traceback (most recent call last):
      ...
      GenerationTooHigh: (4, u'app1', 2)

      >>> print_log()
      zope.generations INFO
        testdb: evolving in mode EVOLVE
      zope.generations ERROR
        testdb/app1: current generation too high (4 > 2)

    We'd better clean up:

      >>> from zope.testing.cleanup import tearDown
      >>> loghandler.uninstall()
      >>> conn.close()
      >>> db.close()
      >>> tearDown()

    """
    db_name = db.database_name or 'main db'
    logger.info('%s: evolving in mode %s',
                db_name, how)
    conn = db.open()
    try:
        context = Context()
        context.connection = conn
        with transaction.manager:
            root = conn.root()
            generations = root.get(generations_key)
            if generations is None:
                # backward compatibility with zope.app.generations
                generations = root.get(old_generations_key)
                if generations is not None:
                    # switch over to new generations_key
                    root[generations_key] = generations
                else:
                    generations = root[generations_key] = PersistentDict()

        for key, manager in sorted(findManagers()):
            with transaction.manager as tx:
                generation = generations.get(key)

                if generation == manager.generation:
                    logger.debug('%s/%s: up-to-date at generation %s',
                                 db_name, key, generation)
                    continue

                if generation is None:
                    # This is a new database, so no old data

                    if IInstallableSchemaManager.providedBy(manager):
                        try:
                            tx.note('%s: running install generation'
                                    % key)
                            logger.info("%s/%s: running install generation",
                                        db_name, key)
                            manager.install(context)
                        except:  # noqa: E722 do not use bare 'except'
                            logger.exception("%s/%s: failed to run install",
                                             db_name, key)
                            raise

                    generations[key] = manager.generation
                    continue

            if generation > manager.generation:
                logger.error('%s/%s: current generation too high (%d > %d)',
                             db_name, key,
                             generation, manager.generation)
                raise GenerationTooHigh(generation, key, manager.generation)

            if generation < manager.minimum_generation:
                if how == EVOLVENOT:
                    logger.error('%s/%s: current generation too low '
                                 '(%d < %d) but mode is %s',
                                 db_name, key,
                                 generation, manager.minimum_generation,
                                 how)
                    raise GenerationTooLow(
                        generation, key, manager.minimum_generation)
            else:
                if how != EVOLVE:
                    continue

            if how == EVOLVEMINIMUM:
                target = manager.minimum_generation
            else:
                target = manager.generation

            logger.info(
                '%s/%s: currently at generation %d, targetting generation %d',
                db_name, key, generation, target)

            while generation < target:
                generation += 1
                tx = transaction.begin()
                try:
                    tx.note('%s: evolving to generation %d'
                            % (key, generation))
                    logger.debug('%s/%s: evolving to generation %d',
                                 db_name, key, generation)
                    manager.evolve(context, generation)
                    generations[key] = generation
                    tx.commit()
                except:  # noqa: E722 do not use bare 'except'
                    # An unguarded handler is intended here
                    tx.abort()
                    logger.exception(
                        "%s/%s: failed to evolve to generation %d",
                        db_name, key, generation)

                    if generation <= manager.minimum_generation:
                        raise UnableToEvolve(generation, key,
                                             manager.generation)
                    break
    finally:
        conn.close()


def evolveSubscriber(event):
    """
    A subscriber for :class:`zope.processlifetime.IDatabaseOpenedWithRoot` that
    evolves all components to their current generation.

    If you want to use this subscriber, you must register it.
    """
    evolve(event.database, EVOLVE)


def evolveNotSubscriber(event):
    """
    A subscriber for :class:`zope.processlifetime.IDatabaseOpenedWithRoot` that
    does no evolution, merele verifying that all components are at the required
    minimum version.

    If you want to use this subscriber, you must register it.
    """
    evolve(event.database, EVOLVENOT)


def evolveMinimumSubscriber(event):
    """
    A subscriber for :class:`zope.processlifetime.IDatabaseOpenedWithRoot` that
    evolves all components to their required minimum version.

    This is registered in this package's ``subscriber.zcml`` file.
    """
    evolve(event.database, EVOLVEMINIMUM)
