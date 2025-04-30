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
"""Utility functions for evolving database generations.
"""


def findObjectsMatching(root, condition):
    """Find all objects in the root that match the condition.

    The condition is a callable Python object that takes an object as an
    argument and must return `True` or `False`.

    All sub-objects of the root will also be searched recursively. All mapping
    objects providing ``values()`` are supported.

    Example:

    >>> class A(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> class B(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> class C(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> tree = A('a1')
    >>> tree['b1'] = B('b1')
    >>> tree['c1'] = C('c1')
    >>> tree['b1']['a2'] = A('a2')
    >>> tree['b1']['b2'] = B('b2')
    >>> tree['b1']['b2']['c2'] = C('c2')
    >>> tree['b1']['b2']['a3'] = A('a3')

    Find all instances of class A:

    >>> matches = findObjectsMatching(tree, lambda x: isinstance(x, A))
    >>> names = [x.name for x in matches]
    >>> names.sort()
    >>> names
    ['a1', 'a2', 'a3']

    Find all objects having a '2' in the name:

    >>> matches = findObjectsMatching(tree, lambda x: '2' in x.name)
    >>> names = [x.name for x in matches]
    >>> names.sort()
    >>> names
    ['a2', 'b2', 'c2']


    If there is no ``values`` on the root, we stop:

    >>> root = [1, 2, 3]
    >>> found = list(findObjectsMatching(root, lambda x: True))
    >>> found == [root]
    True
    """

    if condition(root):
        yield root

    if hasattr(root, 'values'):
        for subobj in root.values():
            yield from findObjectsMatching(subobj, condition)


def findObjectsProviding(root, interface):
    """Find all objects in the root that provide the specified interface.

    All sub-objects of the root will also be searched recursively.

    Example:

    >>> from zope.interface import Interface, implementer
    >>> class IA(Interface):
    ...     pass
    >>> class IB(Interface):
    ...     pass
    >>> class IC(IA):
    ...     pass
    >>> @implementer(IA)
    ... class A(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> @implementer(IB)
    ... class B(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> @implementer(IC)
    ... class C(dict):
    ...     def __init__(self, name):
    ...         self.name = name
    >>> tree = A('a1')
    >>> tree['b1'] = B('b1')
    >>> tree['c1'] = C('c1')
    >>> tree['b1']['a2'] = A('a2')
    >>> tree['b1']['b2'] = B('b2')
    >>> tree['b1']['b2']['c2'] = C('c2')
    >>> tree['b1']['b2']['a3'] = A('a3')

    Find all objects that provide IB:

    >>> matches = findObjectsProviding(tree, IB)
    >>> names = [x.name for x in matches]
    >>> names.sort()
    >>> names
    ['b1', 'b2']

    Find all objects that provide IA:

    >>> matches = findObjectsProviding(tree, IA)
    >>> names = [x.name for x in matches]
    >>> names.sort()
    >>> names
    ['a1', 'a2', 'a3', 'c1', 'c2']
    """

    yield from findObjectsMatching(root, interface.providedBy)


try:
    import zope.app.publication.zopepublication
except ModuleNotFoundError:
    # 'Application' is what ZopePublication uses, up through at least
    # 4.3.1

    #: The name of the root folder.
    #: If ``zope.app.publication.zopepublication`` is available,
    #: this is imported from there.
    ROOT_NAME = 'Application'
else:  # pragma: no cover
    #: The name of the root folder.
    #: If ``zope.app.publication.zopepublication`` is available,
    #: this is imported from there.
    ROOT_NAME = zope.app.publication.zopepublication.ZopePublication.root_name


def getRootFolder(context):
    """Get the root folder of the ZODB.

    We need some set up. Create a database:

    >>> from ZODB.MappingStorage import DB
    >>> from zope.generations.generations import Context
    >>> import transaction
    >>> db = DB()
    >>> context = Context()
    >>> tx = transaction.begin()
    >>> context.connection = db.open()
    >>> root = context.connection.root()

    Add a root folder:

    >>> from zope.site.folder import rootFolder
    >>> root[ROOT_NAME] = rootFolder()
    >>> tx.commit()
    >>> tx = transaction.begin()

    Now we can get the root folder using the function:

    >>> getRootFolder(context) # doctest: +ELLIPSIS
    <zope.site.folder.Folder object at ...>

    We'd better clean up:

    >>> tx.abort()
    >>> context.connection.close()
    >>> db.close()

    """
    return context.connection.root().get(ROOT_NAME, None)
