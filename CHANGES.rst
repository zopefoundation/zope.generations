=========
 CHANGES
=========

5.1.0 (2022-02-11)
==================

- Drop support for Python 3.4.

- Add support for Python 3.8, 3.9 and 3.10.


5.0.0 (2019-09-23)
==================

- Add support for transaction managers operating in explicit mode.
  Schema managers were previously required not to commit transactions
  in their ``evolve`` or ``install`` methods, but a loophole was open
  to allow them to commit "if there were no subsequent operations".
  That loophole is now closed, at least in explicit mode. See `issue 8
  <https://github.com/zopefoundation/zope.generations/issues/8>`_.


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

- Initial release extracted from ``zope.app.generations``.

- Generations key (stored in database root) has been changed from
  ``zope.app.generations`` to ``zope.generations``.  Migration is done when
  ``evolve`` is run the first time by coping the existing generations data
  over to the new key. So the old and the new key can be used in parallel.
