# -*- coding: utf-8 -*-
"""
    pyte.streams
    ~~~~~~~~~~~~

    This module provides three stream implementations with different
    features; for starters, here's a quick example of how streams are
    typically used:

    >>> import pyte
    >>>
    >>> class Dummy(object):
    ...     def __init__(self):
    ...         self.y = 0
    ...
    ...     def cursor_up(self, count=None):
    ...         self.y += count or 1
    ...
    >>> dummy = Dummy()
    >>> stream = pyte.Stream()
    >>> stream.attach(dummy)
    >>> stream.feed(u"\u001B[5A")  # Move the cursor up 5 rows.
    >>> dummy.y
    5

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import codecs
import sys

from . import control as ctrl, escape as esc


class Stream(object):
    """A stream is a state machine that parses a stream of characters
    and dispatches events based on what it sees.

    .. note::

       Stream only accepts unicode strings as input, but if, for some
       reason, you need to feed it with byte strings, consider using
       :class:`~pyte.streams.ByteStream` instead.

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow in :attr:`basic`,
            :attr:`escape`, :attr:`csi` and :attr:`sharp`.
    """

    #: Control sequences, which don't require any arguments.
    basic = {
        ctrl.BEL: "bell",
        ctrl.BS: "backspace",
        ctrl.HT: "tab",
        ctrl.LF: "linefeed",
        ctrl.VT: "linefeed",
        ctrl.FF: "linefeed",
        ctrl.CR: "carriage_return",
        ctrl.SO: "shift_out",
        ctrl.SI: "shift_in",
    }

    #: non-CSI escape sequences.
    escape = {
        esc.RIS: "reset",
        esc.IND: "index",
        esc.NEL: "linefeed",
        esc.RI: "reverse_index",
        esc.HTS: "set_tab_stop",
        esc.DECSC: "save_cursor",
        esc.DECRC: "restore_cursor",
    }

    #: "sharp" escape sequences -- ``ESC # <N>``.
    sharp = {
        esc.DECALN: "alignment_display",
    }

    #: CSI escape sequences -- ``CSI P1;P2;...;Pn <fn>``.
    csi = {
        esc.ICH: "insert_characters",
        esc.CUU: "cursor_up",
        esc.CUD: "cursor_down",
        esc.CUF: "cursor_forward",
        esc.CUB: "cursor_back",
        esc.CNL: "cursor_down1",
        esc.CPL: "cursor_up1",
        esc.CHA: "cursor_to_column",
        esc.CUP: "cursor_position",
        esc.ED: "erase_in_display",
        esc.EL: "erase_in_line",
        esc.IL: "insert_lines",
        esc.DL: "delete_lines",
        esc.DCH: "delete_characters",
        esc.ECH: "erase_characters",
        esc.HPR: "cursor_forward",
        esc.VPA: "cursor_to_line",
        esc.VPR: "cursor_down",
        esc.HVP: "cursor_position",
        esc.TBC: "clear_tab_stop",
        esc.SM: "set_mode",
        esc.RM: "reset_mode",
        esc.SGR: "select_graphic_rendition",
        esc.DECSTBM: "set_margins",
        esc.HPA: "cursor_to_column",
    }

    def __init__(self):
        self.handlers = {
            "stream": self._stream,
            "escape": self._escape,
            "arguments": self._arguments,
            "sharp": self._sharp,
            "charset": self._charset
        }

        self.listeners = []
        self.reset()

    def reset(self):
        """Reset state to ``"stream"`` and empty parameter attributes."""
        self.state = "stream"
        self.flags = {}
        self.params = []
        self.current = ""

    def consume(self, char):
        """Consume a single unicode character and advance the state as
        necessary.

        :param unicode char: a unicode character to consume.
        """
        if not isinstance(char, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        try:
            self.handlers.get(self.state)(char)
        except TypeError:
            pass
        except KeyError:
            if __debug__:
                self.flags["state"] = self.state
                self.flags["unhandled"] = char
                self.dispatch("debug", *self.params)
                self.reset()
            else:
                raise

    def feed(self, chars):
        """Consume a unicode string and advance the state as necessary.

        :param unicode chars: a unicode string to feed from.
        """
        if not isinstance(chars, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        for char in chars: self.consume(char)

    def attach(self, screen, only=()):
        """Adds a given screen to the listeners queue.

        :param pyte.screens.Screen screen: a screen to attach to.
        :param list only: a list of events you want to dispatch to a
                          given screen (empty by default, which means
                          -- dispatch all events).
        """
        self.listeners.append((screen, set(only)))

    def detach(self, screen):
        """Removes a given screen from the listeners queue and failes
        silently if it's not attached.

        :param pyte.screens.Screen screen: a screen to detach.
        """
        for idx, (listener, _) in enumerate(self.listeners):
            if screen is listener:
                self.listeners.pop(idx)

    def dispatch(self, event, *args, **kwargs):
        """Dispatch an event.

        Event handlers are looked up implicitly in the listeners'
        ``__dict__``, so, if a listener only wants to handle ``DRAW``
        events it should define a ``draw()`` method or pass
        ``only=["draw"]`` argument to :meth:`attach`.

        .. warning::

           If any of the attached listeners throws an exception, the
           subsequent callbacks are be aborted.

        :param unicode event: event to dispatch.
        :param list args: arguments to pass to event handlers.
        """
        for listener, only in self.listeners:
            if only and event not in only:
                continue

            try:
                handler = getattr(listener, event)
            except AttributeError:
                continue

            if hasattr(listener, "__before__"):
                listener.__before__(event)

            handler(*args, **self.flags)

            if hasattr(listener, "__after__"):
                listener.__after__(event)
        else:
            if kwargs.get("reset", True): self.reset()

    # State transformers.
    # ...................

    def _stream(self, char):
        """Process a character when in the default ``"stream"`` state."""
        if char in self.basic:
            self.dispatch(self.basic[char])
        elif char == ctrl.ESC:
            self.state = "escape"
        elif char == ctrl.CSI:
            self.state = "arguments"
        elif char not in [ctrl.NUL, ctrl.DEL]:
            self.dispatch("draw", char)

    def _escape(self, char):
        """Handle characters seen when in an escape sequence.

        Most non-VT52 commands start with a left-bracket after the
        escape and then a stream of parameters and a command; with
        a single notable exception -- :data:`escape.DECOM` sequence,
        which starts with a sharp.
        """
        if char == "#":
            self.state = "sharp"
        elif char == "[":
            self.state = "arguments"
        elif char in "()":
            self.state = "charset"
            self.flags["mode"] = char
        else:
            self.dispatch(self.escape[char])

    def _sharp(self, char):
        """Parse arguments of a `"#"` seqence."""
        self.dispatch(self.sharp[char])

    def _charset(self, char):
        """Parse ``G0`` or ``G1`` charset code."""
        self.dispatch("set-charset", char)

    def _arguments(self, char):
        """Parse arguments of an escape sequence.

        All parameters are unsigned, positive decimal integers, with
        the most significant digit sent first. Any parameter greater
        than 9999 is set to 9999. If you do not specify a value, a 0
        value is assumed.

        .. seealso::

           `VT102 User Guide <http://vt100.net/docs/vt102-ug/>`_
               For details on the formatting of escape arguments.

           `VT220 Programmer Reference <http://http://vt100.net/docs/vt220-rm/>`_
               For details on the characters valid for use as arguments.
        """
        if char == "?":
            self.flags["private"] = True
        elif char in [ctrl.BEL, ctrl.BS, ctrl.HT, ctrl.LF, ctrl.VT,
                      ctrl.FF, ctrl.CR]:
            # Not sure why, but those seem to be allowed between CSI
            # sequence arguments.
            self.dispatch(self.basic[char], reset=False)
        elif char == ctrl.SP:
            pass
        elif char in [ctrl.CAN, ctrl.SUB]:
            # If CAN or SUB is received during a sequence, the current
            # sequence is aborted; terminal displays the substitute
            # character, followed by characters in the sequence received
            # after CAN or SUB.
            self.dispatch("draw", char)
            self.state = "stream"
        elif char.isdigit():
            self.current += char
        else:
            self.params.append(min(int(self.current or 0), 9999))

            if char == ";":
                self.current = ""
            else:
                self.dispatch(self.csi[char], *self.params)


class ByteStream(Stream):
    """A stream, which takes bytes strings (instead of unicode) as input
    and tries to decode them using a given list of possible encodings.
    It uses :class:`codecs.IncrementalDecoder` internally, so broken
    bytes is not an issue.

    By default, the following decoding strategy is used:

    * First, try strict ``"utf-8"``, proceed if recieved and
      :exc:`UnicodeDecodeError` ...
    * Try strict ``"cp437"``, failed? move on ...
    * Use ``"utf-8"`` with invalid bytes replaced -- this one will
      allways succeed.

    >>> stream = ByteStream()
    >>> stream.feed(b"foo".decode("utf-8"))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyte/streams.py", line 323, in feed
        "%s requires input in bytes" % self.__class__.__name__)
    TypeError: ByteStream requires input in bytes
    >>> stream.feed(b"foo")

    :param list encodings: a list of ``(encoding, errors)`` pairs,
                           where the first element is encoding name,
                           ex: ``"utf-8"`` and second defines how
                           decoding errors should be handeld; see
                           :meth:`str.decode` for possible values.
    """

    def __init__(self, encodings=None):
        encodings = encodings or [
            ("utf-8", "strict"),
            ("cp437", "strict"),
            ("utf-8", "replace")
        ]

        self.buffer = b"", 0
        self.decoders = [codecs.getincrementaldecoder(encoding)(errors)
                         for encoding, errors in encodings]

        super(ByteStream, self).__init__()

    def feed(self, chars):
        if not isinstance(chars, bytes):
            raise TypeError(
                "%s requires input in bytes" % self.__class__.__name__)

        for decoder in self.decoders:
            decoder.setstate(self.buffer)

            try:
                chars = decoder.decode(chars)
            except UnicodeDecodeError:
                continue

            self.buffer = decoder.getstate()
            return super(ByteStream, self).feed(chars)
        else:
            raise


class DebugStream(ByteStream):
    """Stream, which dumps a subset of the dispatched events to a given
    file-like object (:data:`sys.stdout` by default).

    >>> stream = DebugStream()
    >>> stream.feed("\x1b[1;24r\x1b[4l\x1b[24;1H\x1b[0;10m")
    SET_MARGINS 1; 24
    RESET_MODE 4
    CURSOR_POSITION 24; 1
    SELECT_GRAPHIC_RENDITION 0; 10

    :param file to: a file-like object to write debug information to.
    :param list only: a list of events you want to debug (empty by
                      default, which means -- debug all events).
    """

    def __init__(self, to=sys.stdout, only=(), *args, **kwargs):
        super(DebugStream, self).__init__(*args, **kwargs)

        class Bugger(object):
            def fixup(self, arg):
                if isinstance(arg, str):
                    return arg.encode("utf-8")
                elif not isinstance(arg, unicode):
                    return str(arg)
                else:
                    return arg

            def __getattr__(self, event):
                def inner(*args, **flags):
                    to.write(event.upper() + " ")
                    to.write("; ".join(map(self.fixup, args)))
                    to.write(" ")
                    to.write(", ".join("{0}: {1}".format(name, self.fixup(arg))
                                       for name, arg in flags.iteritems()))
                    to.write("\n")
                return inner

        self.attach(Bugger(), only=only)
