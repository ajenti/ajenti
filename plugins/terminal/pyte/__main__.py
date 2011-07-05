# -*- coding: utf-8 -*-
"""
    pyte
    ~~~~

    Command-line tool for "disassembling" escape and CSI sequences::

        $ echo -e "\e[Jfoo" | python -m pyte
        ERASE_IN_DISPLAY 0
        DRAW f
        DRAW o
        DRAW o
        LINEFEED

        $ python -m pyte foo
        DRAW f
        DRAW o
        DRAW o

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

if __name__ == "__main__":
    import sys
    import pyte

    if len(sys.argv) is 1:
        pyte.dis(sys.stdin.read())
    else:
        pyte.dis("".join(sys.argv[1:]))
