=========
 CHANGES
=========

4.1.0 (2018-10-23)
==================

- Add support for Python 3.7.


4.0.0 (2017-07-20)
==================

- Dropped support for Python 2.6 and 3.3.

- Added support for Python 3.4, 3.5, 3.6, PyPy2 and PyPy3.


4.0.0a1 (2013-02-25)
====================

- Added support for Python 3.3.

- Replaced deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Dropped support for Python 2.4 and 2.5.


3.7.1 (2011-12-22)
==================

- Removed buildout part which was used during development but does not
  compile on Windows.

- Generation scripts add a transaction note.


3.7.0 (2010-09-18)
==================

- Initial release extracted from `zope.app.generations`.

- Generations key (stored in database root) has been changed from
  ``zope.app.generations`` to ``zope.generations``.  Migration is done when
  ``evolve`` is run the first time by coping the exisiting generations data
  over to the new key. So the old and the new key can be used in parallel.
