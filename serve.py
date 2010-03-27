#!/usr/bin/env python
import sys
import logging

from ajenti.standalone import server

if __name__ == '__main__':
    log_level = logging.INFO
    if '-v' in sys.argv:
        log_level = logging.DEBUG
    server(log_level)

