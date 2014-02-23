# -*- coding: utf-8 -*-
"""
    pyte.control
    ~~~~~~~~~~~~

    This module defines simple control sequences, recognized by
    :class:`~pyte.streams.Stream`, the set of codes here is for
    ``TERM=linux`` which is a superset of VT102.

    :copyright: (c) 2011-2013 by Selectel, see AUTHORS for details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import unicode_literals


#: *Space*: Not suprisingly -- ``" "``.
SP = " "

#: *Null*: Does nothing.
NUL = "\u0000"

#: *Bell*: Beeps.
BEL = "\u0007"

#: *Backspace*: Backspace one column, but not past the begining of the
#: line.
BS = "\u0008"

#: *Horizontal tab*: Move cursor to the next tab stop, or to the end
#: of the line if there is no earlier tab stop.
HT = "\u0009"

#: *Linefeed*: Give a line feed, and, if :data:`pyte.modes.LNM` (new
#: line mode) is set also a carriage return.
LF = "\n"
#: *Vertical tab*: Same as :data:`LF`.
VT = "\u000b"
#: *Form feed*: Same as :data:`LF`.
FF = "\u000c"

#: *Carriage return*: Move cursor to left margin on current line.
CR = "\r"

#: *Shift out*: Activate G1 character set.
SO = "\u000e"

#: *Shift in*: Activate G0 character set.
SI = "\u000f"

#: *Cancel*: Interrupt escape sequence. If received during an escape or
#: control sequence, cancels the sequence and displays substitution
#: character.
CAN = "\u0018"
#: *Substitute*: Same as :data:`CAN`.
SUB = "\u001a"

#: *Escape*: Starts an escape sequence.
ESC = "\u001b"

#: *Delete*: Is ingored.
DEL = "\u007f"

#: *Control sequence introducer*: An equavalent for ``ESC [``.
CSI = "\u009b"
