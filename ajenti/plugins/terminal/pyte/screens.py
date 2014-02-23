# -*- coding: utf-8 -*-
"""
    pyte.screens
    ~~~~~~~~~~~~

    This module provides classes for terminal screens, currently
    it contains three screens with different features:

    * :class:`~pyte.screens.Screen` -- base screen implementation,
      which handles all the core escape sequences, recognized by
      :class:`~pyte.streams.Stream`.
    * If you need a screen to keep track of the changed lines
      (which you probably do need) -- use
      :class:`~pyte.screens.DiffScreen`.
    * If you also want a screen to collect history and allow
      pagination -- :class:`pyte.screen.HistoryScreen` is here
      for ya ;)

    .. note:: It would be nice to split those features into mixin
              classes, rather than subclasses, but it's not obvious
              how to do -- feel free to submit a pull request.

    :copyright: (c) 2011-2013 Selectel, see AUTHORS for details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals, division

import copy
import math
import operator
import sys
from collections import deque, namedtuple
from itertools import islice, repeat

from . import modes as mo, graphics as g, charsets as cs


if sys.version_info[0] == 2:
    from future_builtins import map

    range = xrange


def take(n, iterable):
    """Returns first n items of the iterable as a list."""
    return list(islice(iterable, n))


#: A container for screen's scroll margins.
Margins = namedtuple("Margins", "top bottom")

#: A container for savepoint, created on :data:`~pyte.escape.DECSC`.
Savepoint = namedtuple("Savepoint", [
    "cursor",
    "g0_charset",
    "g1_charset",
    "charset",
    "origin",
    "wrap"
])

#: A container for a single character, field names are *hopefully*
#: self-explanatory.
_Char = namedtuple("_Char", [
    "data",
    "fg",
    "bg",
    "bold",
    "italics",
    "underscore",
    "strikethrough",
    "reverse",
])


class Char(_Char):
    """A wrapper around :class:`_Char`, providing some useful defaults
    for most of the attributes.
    """
    __slots__ = ()

    def __new__(cls, data, fg="default", bg="default", bold=False,
                italics=False, underscore=False, reverse=False,
                strikethrough=False):
        return _Char.__new__(cls, data, fg, bg, bold, italics, underscore,
                             reverse, strikethrough)


class Cursor(object):
    """Screen cursor.

    :param int x: horizontal cursor position.
    :param int y: vertical cursor position.
    :param pyte.screens.Char attrs: cursor attributes (see
        :meth:`~pyte.screens.Screen.selectel_graphic_rendition`
        for details).
    """
    def __init__(self, x, y, attrs=Char(" ")):
        self.x, self.y, self.attrs, self.hidden = x, y, attrs, False


class Screen(object):
    """
    A screen is an in-memory matrix of characters that represents the
    screen display of the terminal. It can be instantiated on it's own
    and given explicit commands, or it can be attached to a stream and
    will respond to events.

    .. attribute:: buffer

       A ``lines x columns`` :class:`~pyte.screens.Char` matrix.

    .. attribute:: cursor

       Reference to the :class:`~pyte.screens.Cursor` object, holding
       cursor position and attributes.

    .. attribute:: margins

       Top and bottom screen margins, defining the scrolling region;
       the actual values are top and bottom line.

    .. attribute:: charset

       Current charset number; can be either ``0`` or ``1`` for `G0`
       and `G1` respectively, note that `G0` is activated by default.

    .. note::

       According to ``ECMA-48`` standard, **lines and columnns are
       1-indexed**, so, for instance ``ESC [ 10;10 f`` really means
       -- move cursor to position (9, 9) in the display matrix.

    .. versionchanged:: 0.4.7
    .. warning::

       :data:`~pyte.modes.LNM` is reset by default, to match VT220
       specification.

    .. versionchanged:: 0.4.8
    .. warning::

       If `DECAWM` mode is set than a cursor will be wrapped to the
       **beginning* of the next line, which is the behaviour described
       in ``man console_codes``.

    .. seealso::

       `Standard ECMA-48, Section 6.1.1 \
       <http://www.ecma-international.org/publications
       /standards/Ecma-048.htm>`_
         For a description of the presentational component, implemented
         by ``Screen``.
    """
    #: A plain empty character with default foreground and background
    #: colors.
    default_char = Char(data=" ", fg="default", bg="default")

    #: An inifinite sequence of default characters, used for populating
    #: new lines and columns.
    default_line = repeat(default_char)

    def __init__(self, columns, lines):
        self.savepoints = []
        self.lines, self.columns = lines, columns
        self.buffer = []
        self.reset()

    def __repr__(self):
        return ("{0}({1}, {2})".format(self.__class__.__name__,
                                       self.columns, self.lines))

    def __before__(self, command):
        """Hook, called **before** a command is dispatched to the
        :class:`Screen` instance.

        :param str command: command name, for example ``"LINEFEED"``.
        """

    def __after__(self, command):
        """Hook, called **after** a command is dispatched to the
        :class:`Screen` instance.

        :param str command: command name, for example ``"LINEFEED"``.
        """

    @property
    def size(self):
        """Returns screen size -- ``(lines, columns)``"""
        return self.lines, self.columns

    @property
    def display(self):
        """Returns a :func:`list` of screen lines as unicode strings."""
        return ["".join(map(operator.attrgetter("data"), line))
                for line in self.buffer]

    def reset(self):
        """Resets the terminal to its initial state.

        * Scroll margins are reset to screen boundaries.
        * Cursor is moved to home location -- ``(0, 0)`` and its
          attributes are set to defaults (see :attr:`default_char`).
        * Screen is cleared -- each character is reset to
          :attr:`default_char`.
        * Tabstops are reset to "every eight columns".

        .. note::

           Neither VT220 nor VT102 manuals mentioned that terminal modes
           and tabstops should be reset as well, thanks to
           :manpage:`xterm` -- we now know that.
        """
        self.buffer[:] = (take(self.columns, self.default_line)
                          for _ in range(self.lines))
        self.mode = set([mo.DECAWM, mo.DECTCEM])
        self.margins = Margins(0, self.lines - 1)

        # According to VT220 manual and ``linux/drivers/tty/vt.c``
        # the default G0 charset is latin-1, but for reasons unknown
        # latin-1 breaks ascii-graphics; so G0 defaults to cp437.
        self.charset = 0
        self.g0_charset = cs.IBMPC_MAP
        self.g1_charset = cs.VT100_MAP

        # From ``man terminfo`` -- "... hardware tabs are initially
        # set every `n` spaces when the terminal is powered up. Since
        # we aim to support VT102 / VT220 and linux -- we use n = 8.
        self.tabstops = set(range(7, self.columns, 8))

        self.cursor = Cursor(0, 0)
        self.cursor_position()

    def resize(self, lines=None, columns=None):
        """Resize the screen to the given dimensions.

        If the requested screen size has more lines than the existing
        screen, lines will be added at the bottom. If the requested
        size has less lines than the existing screen lines will be
        clipped at the top of the screen. Similarly, if the existing
        screen has less columns than the requested screen, columns will
        be added at the right, and if it has more -- columns will be
        clipped at the right.

        .. note:: According to `xterm`, we should also reset origin
                  mode and screen margins, see ``xterm/screen.c:1761``.

        :param int lines: number of lines in the new screen.
        :param int columns: number of columns in the new screen.
        """
        lines = lines or self.lines
        columns = columns or self.columns

        # First resize the lines:
        diff = self.lines - lines

        # a) if the current display size is less than the requested
        #    size, add lines to the bottom.
        if diff < 0:
            self.buffer.extend(take(self.columns, self.default_line)
                               for _ in range(diff, 0))
        # b) if the current display size is greater than requested
        #    size, take lines off the top.
        elif diff > 0:
            self.buffer[:diff] = ()

        # Then resize the columns:
        diff = self.columns - columns

        # a) if the current display size is less than the requested
        #    size, expand each line to the new size.
        if diff < 0:
            for y in range(lines):
                self.buffer[y].extend(take(abs(diff), self.default_line))
        # b) if the current display size is greater than requested
        #    size, trim each line from the right to the new size.
        elif diff > 0:
            for line in self.buffer:
                del line[columns:]

        self.lines, self.columns = lines, columns
        self.margins = Margins(0, self.lines - 1)
        self.reset_mode(mo.DECOM)

    def set_margins(self, top=None, bottom=None):
        """Selects top and bottom margins for the scrolling region.

        Margins determine which screen lines move during scrolling
        (see :meth:`index` and :meth:`reverse_index`). Characters added
        outside the scrolling region do not cause the screen to scroll.

        :param int top: the smallest line number that is scrolled.
        :param int bottom: the biggest line number that is scrolled.
        """
        if top is None or bottom is None:
            return

        # Arguments are 1-based, while :attr:`margins` are zero based --
        # so we have to decrement them by one. We also make sure that
        # both of them is bounded by [0, lines - 1].
        top = max(0, min(top - 1, self.lines - 1))
        bottom = max(0, min(bottom - 1, self.lines - 1))

        # Even though VT102 and VT220 require DECSTBM to ignore regions
        # of width less than 2, some programs (like aptitude for example)
        # rely on it. Practicality beats purity.
        if bottom - top >= 1:
            self.margins = Margins(top, bottom)

            # The cursor moves to the home position when the top and
            # bottom margins of the scrolling region (DECSTBM) changes.
            self.cursor_position()

    def set_charset(self, code, mode):
        """Set active ``G0`` or ``G1`` charset.

        :param str code: character set code, should be a character
                         from ``"B0UK"`` -- otherwise ignored.
        :param str mode: if ``"("`` ``G0`` charset is set, if
                         ``")"`` -- we operate on ``G1``.

        .. warning:: User-defined charsets are currently not supported.
        """
        if code in cs.MAPS:
            setattr(self, {"(": "g0_charset", ")": "g1_charset"}[mode],
                    cs.MAPS[code])

    def set_mode(self, *modes, **kwargs):
        """Sets (enables) a given list of modes.

        :param list modes: modes to set, where each mode is a constant
                           from :mod:`pyte.modes`.
        """
        # Private mode codes are shifted, to be distingiushed from non
        # private ones.
        if kwargs.get("private"):
            modes = [mode << 5 for mode in modes]

        self.mode.update(modes)

        # When DECOLM mode is set, the screen is erased and the cursor
        # moves to the home position.
        if mo.DECCOLM in modes:
            self.resize(columns=132)
            self.erase_in_display(2)
            self.cursor_position()

        # According to `vttest`, DECOM should also home the cursor, see
        # vttest/main.c:303.
        if mo.DECOM in modes:
            self.cursor_position()

        # Mark all displayed characters as reverse.
        if mo.DECSCNM in modes:
            self.buffer[:] = ([char._replace(reverse=True) for char in line]
                       for line in self.buffer)
            self.select_graphic_rendition(g._SGR["+reverse"])

        # Make the cursor visible.
        if mo.DECTCEM in modes:
            self.cursor.hidden = False

    def reset_mode(self, *modes, **kwargs):
        """Resets (disables) a given list of modes.

        :param list modes: modes to reset -- hopefully, each mode is a
                           constant from :mod:`pyte.modes`.
        """
        # Private mode codes are shifted, to be distingiushed from non
        # private ones.
        if kwargs.get("private"):
            modes = [mode << 5 for mode in modes]

        self.mode.difference_update(modes)

        # Lines below follow the logic in :meth:`set_mode`.
        if mo.DECCOLM in modes:
            self.resize(columns=80)
            self.erase_in_display(2)
            self.cursor_position()

        if mo.DECOM in modes:
            self.cursor_position()

        if mo.DECSCNM in modes:
            self.buffer[:] = ([char._replace(reverse=False) for char in line]
                       for line in self.buffer)
            self.select_graphic_rendition(g._SGR["-reverse"])

        # Hide the cursor.
        if mo.DECTCEM in modes:
            self.cursor.hidden = True

    def shift_in(self):
        """Activates ``G0`` character set."""
        self.charset = 0

    def shift_out(self):
        """Activates ``G1`` character set."""
        self.charset = 1

    def draw(self, char):
        """Display a character at the current cursor position and advance
        the cursor if :data:`~pyte.modes.DECAWM` is set.

        :param str char: a character to display.
        """
        # Translating a given character.
        char = char.translate([self.g0_charset,
                               self.g1_charset][self.charset])

        # If this was the last column in a line and auto wrap mode is
        # enabled, move the cursor to the beginning of the next line,
        # otherwise replace characters already displayed with newly
        # entered.
        if self.cursor.x == self.columns:
            if mo.DECAWM in self.mode:
                self.carriage_return()
                self.linefeed()
            else:
                self.cursor.x -= 1

        # If Insert mode is set, new characters move old characters to
        # the right, otherwise terminal is in Replace mode and new
        # characters replace old characters at cursor position.
        if mo.IRM in self.mode:
            self.insert_characters(1)

        self.buffer[self.cursor.y][self.cursor.x] = self.cursor.attrs \
            ._replace(data=char)

        # .. note:: We can't use :meth:`cursor_forward()`, because that
        #           way, we'll never know when to linefeed.
        self.cursor.x += 1

    def carriage_return(self):
        """Move the cursor to the beginning of the current line."""
        self.cursor.x = 0

    def index(self):
        """Move the cursor down one line in the same column. If the
        cursor is at the last line, create a new line at the bottom.
        """
        top, bottom = self.margins

        if self.cursor.y == bottom:
            self.buffer.pop(top)
            self.buffer.insert(bottom, take(self.columns, self.default_line))
        else:
            self.cursor_down()

    def reverse_index(self):
        """Move the cursor up one line in the same column. If the cursor
        is at the first line, create a new line at the top.
        """
        top, bottom = self.margins

        if self.cursor.y == top:
            self.buffer.pop(bottom)
            self.buffer.insert(top, take(self.columns, self.default_line))
        else:
            self.cursor_up()

    def linefeed(self):
        """Performs an index and, if :data:`~pyte.modes.LNM` is set, a
        carriage return.
        """
        self.index()

        if mo.LNM in self.mode:
            self.carriage_return()

        self.ensure_bounds()

    def tab(self):
        """Move to the next tab space, or the end of the screen if there
        aren't anymore left.
        """
        for stop in sorted(self.tabstops):
            if self.cursor.x < stop:
                column = stop
                break
        else:
            column = self.columns - 1

        self.cursor.x = column

    def backspace(self):
        """Move cursor to the left one or keep it in it's position if
        it's at the beginning of the line already.
        """
        self.cursor_back()

    def save_cursor(self):
        """Push the current cursor position onto the stack."""
        self.savepoints.append(Savepoint(copy.copy(self.cursor),
                                         self.g0_charset,
                                         self.g1_charset,
                                         self.charset,
                                         mo.DECOM in self.mode,
                                         mo.DECAWM in self.mode))

    def restore_cursor(self):
        """Set the current cursor position to whatever cursor is on top
        of the stack.
        """
        if self.savepoints:
            savepoint = self.savepoints.pop()

            self.g0_charset = savepoint.g0_charset
            self.g1_charset = savepoint.g1_charset
            self.charset = savepoint.charset

            if savepoint.origin:
                self.set_mode(mo.DECOM)
            if savepoint.wrap:
                self.set_mode(mo.DECAWM)

            self.cursor = savepoint.cursor
            self.ensure_bounds(use_margins=True)
        else:
            # If nothing was saved, the cursor moves to home position;
            # origin mode is reset. :todo: DECAWM?
            self.reset_mode(mo.DECOM)
            self.cursor_position()

    def insert_lines(self, count=None):
        """Inserts the indicated # of lines at line with cursor. Lines
        displayed **at** and below the cursor move down. Lines moved
        past the bottom margin are lost.

        :param count: number of lines to delete.
        """
        count = count or 1
        top, bottom = self.margins

        # If cursor is outside scrolling margins it -- do nothin'.
        if top <= self.cursor.y <= bottom:
            #                           v +1, because range() is exclusive.
            for line in range(self.cursor.y,
                              min(bottom + 1, self.cursor.y + count)):
                self.buffer.pop(bottom)
                self.buffer.insert(line, take(self.columns, self.default_line))

            self.carriage_return()

    def delete_lines(self, count=None):
        """Deletes the indicated # of lines, starting at line with
        cursor. As lines are deleted, lines displayed below cursor
        move up. Lines added to bottom of screen have spaces with same
        character attributes as last line moved up.

        :param int count: number of lines to delete.
        """
        count = count or 1
        top, bottom = self.margins

        # If cursor is outside scrolling margins it -- do nothin'.
        if top <= self.cursor.y <= bottom:
            #                v -- +1 to include the bottom margin.
            for _ in range(min(bottom - self.cursor.y + 1, count)):
                self.buffer.pop(self.cursor.y)
                self.buffer.insert(bottom, list(
                    repeat(self.cursor.attrs, self.columns)))

            self.carriage_return()

    def insert_characters(self, count=None):
        """Inserts the indicated # of blank characters at the cursor
        position. The cursor does not move and remains at the beginning
        of the inserted blank characters. Data on the line is shifted
        forward.

        :param int count: number of characters to insert.
        """
        count = count or 1

        for _ in range(min(self.columns - self.cursor.y, count)):
            self.buffer[self.cursor.y].insert(self.cursor.x, self.cursor.attrs)
            self.buffer[self.cursor.y].pop()

    def delete_characters(self, count=None):
        """Deletes the indicated # of characters, starting with the
        character at cursor position. When a character is deleted, all
        characters to the right of cursor move left. Character attributes
        move with the characters.

        :param int count: number of characters to delete.
        """
        count = count or 1

        for _ in range(min(self.columns - self.cursor.x, count)):
            self.buffer[self.cursor.y].pop(self.cursor.x)
            self.buffer[self.cursor.y].append(self.cursor.attrs)

    def erase_characters(self, count=None):
        """Erases the indicated # of characters, starting with the
        character at cursor position. Character attributes are set
        cursor attributes. The cursor remains in the same position.

        :param int count: number of characters to erase.

        .. warning::

           Even though *ALL* of the VTXXX manuals state that character
           attributes **should be reset to defaults**, ``libvte``,
           ``xterm`` and ``ROTE`` completely ignore this. Same applies
           too all ``erase_*()`` and ``delete_*()`` methods.
        """
        count = count or 1

        for column in range(self.cursor.x,
                            min(self.cursor.x + count, self.columns)):
            self.buffer[self.cursor.y][column] = self.cursor.attrs

    def erase_in_line(self, type_of=0, private=False):
        """Erases a line in a specific way.

        :param int type_of: defines the way the line should be erased in:

            * ``0`` -- Erases from cursor to end of line, including cursor
              position.
            * ``1`` -- Erases from beginning of line to cursor,
              including cursor position.
            * ``2`` -- Erases complete line.
        :param bool private: when ``True`` character attributes aren left
                             unchanged **not implemented**.
        """
        interval = (
            # a) erase from the cursor to the end of line, including
            # the cursor,
            range(self.cursor.x, self.columns),
            # b) erase from the beginning of the line to the cursor,
            # including it,
            range(0, self.cursor.x + 1),
            # c) erase the entire line.
            range(0, self.columns)
        )[type_of]

        for column in interval:
            self.buffer[self.cursor.y][column] = self.cursor.attrs

    def erase_in_display(self, type_of=0, private=False):
        """Erases display in a specific way.

        :param int type_of: defines the way the line should be erased in:

            * ``0`` -- Erases from cursor to end of screen, including
              cursor position.
            * ``1`` -- Erases from beginning of screen to cursor,
              including cursor position.
            * ``2`` -- Erases complete display. All lines are erased
              and changed to single-width. Cursor does not move.
        :param bool private: when ``True`` character attributes aren left
                             unchanged **not implemented**.
        """
        interval = (
            # a) erase from cursor to the end of the display, including
            # the cursor,
            range(self.cursor.y + 1, self.lines),
            # b) erase from the beginning of the display to the cursor,
            # including it,
            range(0, self.cursor.y),
            # c) erase the whole display.
            range(0, self.lines)
        )[type_of]

        for line in interval:
            self.buffer[line][:] = \
                (self.cursor.attrs for _ in range(self.columns))

        # In case of 0 or 1 we have to erase the line with the cursor.
        if type_of in [0, 1]:
            self.erase_in_line(type_of)

    def set_tab_stop(self):
        """Sest a horizontal tab stop at cursor position."""
        self.tabstops.add(self.cursor.x)

    def clear_tab_stop(self, type_of=None):
        """Clears a horizontal tab stop in a specific way, depending
        on the ``type_of`` value:

        * ``0`` or nothing -- Clears a horizontal tab stop at cursor
          position.
        * ``3`` -- Clears all horizontal tab stops.
        """
        if not type_of:
            # Clears a horizontal tab stop at cursor position, if it's
            # present, or silently fails if otherwise.
            self.tabstops.discard(self.cursor.x)
        elif type_of == 3:
            self.tabstops = set()  # Clears all horizontal tab stops.

    def ensure_bounds(self, use_margins=None):
        """Ensure that current cursor position is within screen bounds.

        :param bool use_margins: when ``True`` or when
                                 :data:`~pyte.modes.DECOM` is set,
                                 cursor is bounded by top and and bottom
                                 margins, instead of ``[0; lines - 1]``.
        """
        if use_margins or mo.DECOM in self.mode:
            top, bottom = self.margins
        else:
            top, bottom = 0, self.lines - 1

        self.cursor.x = min(max(0, self.cursor.x), self.columns - 1)
        self.cursor.y = min(max(top, self.cursor.y), bottom)

    def cursor_up(self, count=None):
        """Moves cursor up the indicated # of lines in same column.
        Cursor stops at top margin.

        :param int count: number of lines to skip.
        """
        self.cursor.y -= count or 1
        self.ensure_bounds(use_margins=True)

    def cursor_up1(self, count=None):
        """Moves cursor up the indicated # of lines to column 1. Cursor
        stops at bottom margin.

        :param int count: number of lines to skip.
        """
        self.cursor_up(count)
        self.carriage_return()

    def cursor_down(self, count=None):
        """Moves cursor down the indicated # of lines in same column.
        Cursor stops at bottom margin.

        :param int count: number of lines to skip.
        """
        self.cursor.y += count or 1
        self.ensure_bounds(use_margins=True)

    def cursor_down1(self, count=None):
        """Moves cursor down the indicated # of lines to column 1.
        Cursor stops at bottom margin.

        :param int count: number of lines to skip.
        """
        self.cursor_down(count)
        self.carriage_return()

    def cursor_back(self, count=None):
        """Moves cursor left the indicated # of columns. Cursor stops
        at left margin.

        :param int count: number of columns to skip.
        """
        self.cursor.x -= count or 1
        self.ensure_bounds()

    def cursor_forward(self, count=None):
        """Moves cursor right the indicated # of columns. Cursor stops
        at right margin.

        :param int count: number of columns to skip.
        """
        self.cursor.x += count or 1
        self.ensure_bounds()

    def cursor_position(self, line=None, column=None):
        """Set the cursor to a specific `line` and `column`.

        Cursor is allowed to move out of the scrolling region only when
        :data:`~pyte.modes.DECOM` is reset, otherwise -- the position
        doesn't change.

        :param int line: line number to move the cursor to.
        :param int column: column number to move the cursor to.
        """
        column = (column or 1) - 1
        line = (line or 1) - 1

        # If origin mode (DECOM) is set, line number are relative to
        # the top scrolling margin.
        if mo.DECOM in self.mode:
            line += self.margins.top

            # Cursor is not allowed to move out of the scrolling region.
            if not self.margins.top <= line <= self.margins.bottom:
                return

        self.cursor.x, self.cursor.y = column, line
        self.ensure_bounds()

    def cursor_to_column(self, column=None):
        """Moves cursor to a specific column in the current line.

        :param int column: column number to move the cursor to.
        """
        self.cursor.x = (column or 1) - 1
        self.ensure_bounds()

    def cursor_to_line(self, line=None):
        """Moves cursor to a specific line in the current column.

        :param int line: line number to move the cursor to.
        """
        self.cursor.y = (line or 1) - 1

        # If origin mode (DECOM) is set, line number are relative to
        # the top scrolling margin.
        if mo.DECOM in self.mode:
            self.cursor.y += self.margins.top

            # FIXME: should we also restrict the cursor to the scrolling
            # region?

        self.ensure_bounds()

    def bell(self, *args):
        """Bell stub -- the actual implementation should probably be
        provided by the end-user.
        """

    def alignment_display(self):
        """Fills screen with uppercase E's for screen focus and alignment."""
        for line in self.buffer:
            for column, char in enumerate(line):
                line[column] = char._replace(data="E")

    def select_graphic_rendition(self, *attrs):
        """Set display attributes.

        :param list attrs: a list of display attributes to set.
        """
        replace = {}

        for attr in attrs or [0]:
            if attr in g.FG:
                replace["fg"] = g.FG[attr]
            elif attr in g.BG:
                replace["bg"] = g.BG[attr]
            elif attr in g.TEXT:
                attr = g.TEXT[attr]
                replace[attr[1:]] = attr.startswith("+")
            elif not attr:
                replace = self.default_char._asdict()

        self.cursor.attrs = self.cursor.attrs._replace(**replace)


class DiffScreen(Screen):
    """A screen subclass, which maintains a set of dirty lines in its
    :attr:`dirty` attribute. The end user is responsible for emptying
    a set, when a diff is applied.

    .. attribute:: dirty

       A set of line numbers, which should be re-drawn.

       >>> screen = DiffScreen(80, 24)
       >>> screen.dirty.clear()
       >>> screen.draw(u"!")
       >>> screen.dirty
       set([0])
    """
    def __init__(self, *args):
        self.dirty = set()
        super(DiffScreen, self).__init__(*args)

    def set_mode(self, *modes, **kwargs):
        if mo.DECSCNM >> 5 in modes and kwargs.get("private"):
            self.dirty.update(range(self.lines))
        super(DiffScreen, self).set_mode(*modes, **kwargs)

    def reset_mode(self, *modes, **kwargs):
        if mo.DECSCNM >> 5 in modes and kwargs.get("private"):
            self.dirty.update(range(self.lines))
        super(DiffScreen, self).reset_mode(*modes, **kwargs)

    def reset(self):
        self.dirty.update(range(self.lines))
        super(DiffScreen, self).reset()

    def resize(self, *args, **kwargs):
        self.dirty.update(range(self.lines))
        super(DiffScreen, self).resize(*args, **kwargs)

    def draw(self, *args):
        self.dirty.add(self.cursor.y)
        super(DiffScreen, self).draw(*args)

    def index(self):
        if self.cursor.y == self.margins.bottom:
            self.dirty.update(range(self.lines))

        super(DiffScreen, self).index()

    def reverse_index(self):
        if self.cursor.y == self.margins.top:
            self.dirty.update(range(self.lines))

        super(DiffScreen, self).reverse_index()

    def insert_lines(self, *args):
        self.dirty.update(range(self.cursor.y, self.lines))
        super(DiffScreen, self).insert_lines(*args)

    def delete_lines(self, *args):
        self.dirty.update(range(self.cursor.y, self.lines))
        super(DiffScreen, self).delete_lines(*args)

    def insert_characters(self, *args):
        self.dirty.add(self.cursor.y)
        super(DiffScreen, self).insert_characters(*args)

    def delete_characters(self, *args):
        self.dirty.add(self.cursor.y)
        super(DiffScreen, self).delete_characters(*args)

    def erase_characters(self, *args):
        self.dirty.add(self.cursor.y)
        super(DiffScreen, self).erase_characters(*args)

    def erase_in_line(self, *args):
        self.dirty.add(self.cursor.y)
        super(DiffScreen, self).erase_in_line(*args)

    def erase_in_display(self, type_of=0):
        self.dirty.update((
            range(self.cursor.y + 1, self.lines),
            range(0, self.cursor.y),
            range(0, self.lines)
        )[type_of])
        super(DiffScreen, self).erase_in_display(type_of)

    def alignment_display(self):
        self.dirty.update(range(self.lines))
        super(DiffScreen, self).alignment_display()


History = namedtuple("History", "top bottom ratio size position")


class HistoryScreen(DiffScreen):
    """A screen subclass, which keeps track of screen history and allows
    pagination. This is not linux-specific, but still useful; see  page
    462 of VT520 User's Manual.

    :param int history: total number of history lines to keep; is split
                        between top and bottom queues.
    :param int ratio: defines how much lines to scroll on :meth:`next_page`
                      and :meth:`prev_page` calls.

    .. attribute:: history

       A pair of history queues for top and bottom margins accordingly;
       here's the overall screen structure::

            [ 1: .......]
            [ 2: .......]  <- top history
            [ 3: .......]
            ------------
            [ 4: .......]  s
            [ 5: .......]  c
            [ 6: .......]  r
            [ 7: .......]  e
            [ 8: .......]  e
            [ 9: .......]  n
            ------------
            [10: .......]
            [11: .......]  <- bottom history
            [12: .......]

    .. note::

       Don't forget to update :class:`~pyte.streams.Stream` class with
       appropriate escape sequences -- you can use any, since pagination
       protocol is not standardized, for example::

           Stream.escape["N"] = "next_page"
           Stream.escape["P"] = "prev_page"
    """

    def __init__(self, columns, lines, history=100, ratio=.5):
        self.history = History(deque(maxlen=history // 2),
                               deque(maxlen=history),
                               float(ratio),
                               history,
                               history)

        super(HistoryScreen, self).__init__(columns, lines)

    def __before__(self, command):
        """Ensures a screen is at the bottom of the history buffer."""
        if command not in ["prev_page", "next_page"]:
            while self.history.position < self.history.size:
                self.next_page()

        super(HistoryScreen, self).__before__(command)

    def __after__(self, command):
        """Ensures all lines on a screen have proper width (:attr:`columns`).

        Extra characters are truncated, missing characters are filled
        with whitespace.
        """
        if command in ["prev_page", "next_page"]:
            for idx, line in enumerate(self.buffer):
                if len(line) > self.columns:
                    self.buffer[idx] = line[:self.columns]
                elif len(line) < self.columns:
                    self.buffer[idx] = line + take(self.columns - len(line),
                                                   self.default_line)

        # If we're at the bottom of the history buffer and `DECTCEM`
        # mode is set -- show the cursor.
        self.cursor.hidden = not (
            abs(self.history.position - self.history.size) < self.lines and
            mo.DECTCEM in self.mode
        )

        super(HistoryScreen, self).__after__(command)

    def reset(self):
        """Overloaded to reset screen history state: history position
        is reset to bottom of both queues;  queues themselves are
        emptied.
        """
        super(HistoryScreen, self).reset()

        self.history.top.clear()
        self.history.bottom.clear()
        self.history = self.history._replace(position=self.history.size)

    def index(self):
        """Overloaded to update top history with the removed lines."""
        top, bottom = self.margins

        if self.cursor.y == bottom:
            self.history.top.append(self.buffer[top])

        super(HistoryScreen, self).index()

    def reverse_index(self):
        """Overloaded to update bottom history with the removed lines."""
        top, bottom = self.margins

        if self.cursor.y == top:
            self.history.bottom.append(self.buffer[bottom])

        super(HistoryScreen, self).reverse_index()

    def prev_page(self):
        """Moves the screen page up through the history buffer. Page
        size is defined by ``history.ratio``, so for instance
        ``ratio = .5`` means that half the screen is restored from
        history on page switch.
        """
        if self.history.position > self.lines and self.history.top:
            mid = min(len(self.history.top),
                      int(math.ceil(self.lines * self.history.ratio)))

            self.history.bottom.extendleft(reversed(self.buffer[-mid:]))
            self.history = self.history \
                ._replace(position=self.history.position - self.lines)

            self.buffer[:] = list(reversed([
                self.history.top.pop() for _ in range(mid)
            ])) + self.buffer[:-mid]

            self.dirty = set(range(self.lines))

    def next_page(self):
        """Moves the screen page down through the history buffer."""
        if self.history.position < self.history.size and self.history.bottom:
            mid = min(len(self.history.bottom),
                      int(math.ceil(self.lines * self.history.ratio)))

            self.history.top.extend(self.buffer[:mid])
            self.history = self.history \
                ._replace(position=self.history.position + self.lines)

            self.buffer[:] = self.buffer[mid:] + [
                self.history.bottom.popleft() for _ in range(mid)
            ]

            self.dirty = set(range(self.lines))
