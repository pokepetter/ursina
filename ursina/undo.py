#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 David Townshend
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 675 Mass Ave, Cambridge, MA 02139, USA.

__version__ = '0.5.1'
__author__ = 'David Townshend'

# __all__ = ['undoable', 'group', 'Stack', 'stack', 'setstack']

import contextlib

from collections import deque

class _Action:
    ''' This represents an action which can be done and undone.

    It is the result of a call on an undoable function and has
    three methods: ``do()``, ``undo()`` and ``text()``.  The first value
    returned by the internal call in ``do()`` is the value which will
    subsequently be returned by ``text``.  Any remaining values are
    returned by ``do()``.
    '''
    def __init__(self, generator, args, kwargs):
        self._generator = generator
        self.args = args
        self.kwargs = kwargs
        self._text = ''

    def do(self):
        'Do or redo the action'
        self._runner = self._generator(*self.args, **self.kwargs)
        rets = next(self._runner)
        if isinstance(rets, tuple):
            self._text = rets[0]
            return rets[1:]
        elif rets is None:
            self._text = ''
            return None
        else:
            self._text = rets
            return None

    def undo(self):
        'Undo the action'
        try:
            next(self._runner)
        except StopIteration:
            pass
        # Delete it so that its not accidentally called again
        del self._runner

    def text(self):
        'Return the descriptive text of the action'
        return self._text


def undoable(generator):
    ''' Decorator which creates a new undoable action type.

    This decorator should be used on a generator of the following format::

        @undoable
        def operation(*args):
            do_operation_code
            yield 'descriptive text'
            undo_operator_code
    '''
    def inner(*args, **kwargs):
        action = _Action(generator, args, kwargs)
        ret = action.do()
        stack().append(action)
        if isinstance(ret, tuple):
            if len(ret) == 1:
                return ret[0]
            elif len(ret) == 0:
                return None
        return ret
    return inner


class _Group:
    ''' A undoable group context manager. '''

    def __init__(self, desc):
        self._desc = desc
        self._stack = []

    def __enter__(self):
        stack().setreceiver(self._stack)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            stack().resetreceiver()
            stack().append(self)
        return False

    def undo(self):
        for undoable in reversed(self._stack):
            undoable.undo()

    def do(self):
        for undoable in self._stack:
            undoable.do()

    def text(self):
        return self._desc.format(count=len(self._stack))


def group(desc):
    ''' Return a context manager for grouping undoable actions.

    All actions which occur within the group will be undone by a single call
    of `stack.undo`, e.g.

    >>> @undoable
    ... def operation(n):
    ...     yield
    ...     print(n)
    >>> with group('text'):
    ...     for n in range(3):
    ...         operation(n)
    >>> operation(3)
    >>> stack().undo()
    3
    >>> stack().undo()
    2
    1
    0
    '''
    return _Group(desc)


class Stack:
    ''' The main undo stack.

    The two key features are the :func:`redo` and :func:`undo` methods. If an
    exception occurs during doing or undoing a undoable, the undoable
    aborts and the stack is cleared to avoid any further data corruption.

    The stack provides two properties for tracking actions: *docallback*
    and *undocallback*. Each of these allow a callback function to be set
    which is called when an action is done or undone repectively. By default,
    they do nothing.

    >>> def done():
    ...     print('Can now undo: {}'.format(stack().undotext()))
    >>> def undone():
    ...     print('Can now redo: {}'.format(stack().redotext()))
    >>> stack().docallback = done
    >>> stack().undocallback = undone
    >>> @undoable
    ... def action():
    ...     yield 'An action'
    >>> action()
    Can now undo: Undo An action
    >>> stack().undo()
    Can now redo: Redo An action
    >>> stack().redo()
    Can now undo: Undo An action

    Setting them back to ``lambda: None`` will stop any further actions.

    >>> stack().docallback = stack().undocallback = lambda: None
    >>> action()
    >>> stack().undo()

    It is possible to mark a point in the undo history when the document
    handled is saved. This allows the undo system to report whether a
    document has changed. The point is marked using :func:`savepoint` and
    :func:`haschanged` returns whether or not the state has changed (either
    by doing or undoing an action). Only one savepoint can be tracked,
    marking a new one removes the old one.

    >>> stack().savepoint()
    >>> stack().haschanged()
    False
    >>> action()
    >>> stack().haschanged()
    True
    '''

    def __init__(self):
        self._undos = deque()
        self._redos = deque()
        self._receiver = self._undos
        self._savepoint = None
        self.undocallback = lambda: None
        self.docallback = lambda: None

    def canundo(self):
        ''' Return *True* if undos are available '''
        return len(self._undos) > 0

    def canredo(self):
        ''' Return *True* if redos are available '''
        return len(self._redos) > 0

    def redo(self):
        ''' Redo the last undone action.

        This is only possible if no other actions have occurred since the
        last undo call.
        '''
        if self.canredo():
            undoable = self._redos.pop()
            with self._pausereceiver():
                try:
                    undoable.do()
                except:
                    self.clear()
                    raise
                else:
                    self._undos.append(undoable)
            self.docallback()

    def undo(self):
        ''' Undo the last action. '''
        if self.canundo():
            undoable = self._undos.pop()
            with self._pausereceiver():
                try:
                    undoable.undo()
                except:
                    self.clear()
                    raise
                else:
                    self._redos.append(undoable)
            self.undocallback()

    def clear(self):
        ''' Clear the undo list. '''
        self._undos.clear()
        self._redos.clear()
        self._savepoint = None
        self._receiver = self._undos

    def undocount(self):
        ''' Return the number of undos available. '''
        return len(self._undos)

    def redocount(self):
        ''' Return the number of redos available. '''
        return len(self._undos)

    def undotext(self):
        ''' Return a description of the next available undo. '''
        if self.canundo():
            return ('Undo ' + self._undos[-1].text()).strip()

    def redotext(self):
        ''' Return a description of the next available redo. '''
        if self.canredo():
            return ('Redo ' + self._redos[-1].text()).strip()

    @contextlib.contextmanager
    def _pausereceiver(self):
        ''' Return a contect manager which temporarily pauses the receiver. '''
        self.setreceiver([])
        yield
        self.resetreceiver()

    def setreceiver(self, receiver=None):
        ''' Set an object to receiver commands pushed onto the stack.

        By default it is the internal stack, but it can be set (usually
        internally) to any object with an *append()* method.
        '''
        assert hasattr(receiver, 'append')
        self._receiver = receiver

    def resetreceiver(self):
        ''' Reset the receiver to the internal stack.'''
        self._receiver = self._undos

    def append(self, action):
        ''' Add a undoable to the stack, using ``receiver.append()``. '''
        if self._receiver is not None:
            self._receiver.append(action)
        if self._receiver is self._undos:
            self._redos.clear()
            self.docallback()

    def savepoint(self):
        ''' Set the savepoint. '''
        self._savepoint = self.undocount()

    def haschanged(self):
        ''' Return *True* if the state has changed since the savepoint.

        This will always return *True* if the savepoint has not been set.
        '''
        return self._savepoint is None or self._savepoint != self.undocount()


_stack = None

def stack():
    ''' Return the currently used stack.

    If no stack has been set, a new one is created and set.
    '''
    global _stack
    if _stack is None:
        _stack = Stack()
    return _stack

def setstack(stack):
    ''' Set the undo stack to a specific `Stack` object.'''
    global _stack
    _stack = stack
