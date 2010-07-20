#
# encoding: utf-8
#
# $Id: PrioList.py 12 2006-10-06 21:37:28Z avenger $
# 
# Copyright (C) 2006-2010 Dmitry Zamaruev (dmitry.zamaruev@gmail.com)
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

from UserList import UserList

class PrioList(UserList):
    def __init__(self, max_priority=100):
        super(PrioList, self).__init__()
        self.prio = []
        self._max = max_priority
        self._def = max_priority/2

    def __delitem__(self, i): 
        del self.data[i]
        del self.prio[i]

    # Prohibit following operations 
    __setslice__ = None
    __delslice__ = None
    __add__ = None
    __radd__ = None
    __iadd__ = None
    __mul__ = None
    __imul__ = None

    def _prio_index(self, prio):
        i = None
        for p, el in enumerate(self.prio):
             if prio < el:
                i = p
                break
        if i is None:
            i = len(self.prio)
        return i

    def _append_prio(self, item, prio):
        i = self._prio_index(prio)
        super(PrioList, self).insert(i, item)
        self.prio.insert(i, prio)

    # Access methods 
    def append(self, item):
        if isinstance(item, tuple): 
            self._append_prio(item[0], item[1])
        else:
            self._append_prio(item, self._def)

    # Prohibit following methods
    insert = None
    pop = None
    remove = None
    index = None
    reverse = None
    sort = None
    extend = None
    
