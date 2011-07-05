# -*- coding: utf-8 -*-
"""
    pyte
    ~~~~

    `pyte` implements a mix of VT100, VT220 and VT520 specification,
    and aims to support most of the `TERM=linux` functionality.

    Two classes: :class:`~pyte.streams.Stream`, which parses the
    command stream and dispatches events for commands, and
    :class:`~pyte.screens.Screen` which, when used with a stream
    maintains a buffer of strings representing the screen of a
    terminal.

    .. warning:: From ``xterm/main.c`` «If you think you know what all
                 of this code is doing, you are probably very mistaken.
                 There be serious and nasty dragons here» -- nothing
                 has changed.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

__all__ = ("Screen", "DiffScreen", "HistoryScreen",
           "Stream", "ByteStream", "DebugStream",
           "ctrl", "esc", "mo", "g", "cs")

from . import (
    control as ctrl,
    charsets as cs,
    escape as esc,
    graphics as g,
    modes as mo
)
from .screens import Screen, DiffScreen, HistoryScreen
from .streams import Stream, ByteStream, DebugStream


if __debug__:
    def dis(chars):
        """A :func:`dis.dis` for terminals.

        >>> dis(u"\u0007")
        BELL
        >>> dis(u"\x9b20m")
        SELECT-GRAPHIC-RENDITION 20
        """
        if isinstance(chars, unicode):
            chars = chars.encode("utf-8")

        return DebugStream().feed(chars)
