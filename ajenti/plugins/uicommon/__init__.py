# coding=utf-8
# ---------------------------------------------------------------------------
#   UI common plugin for Ajenti, to provide general UI elements.
#
#   Copyright (C) 2015 Marc Bertens <m.bertens@pe2mbs.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see http://www.gnu.org/licenses/agpl-3.0.html.
# ---------------------------------------------------------------------------
#
__author__      = "Marc Bertens"
__copyright__   = "Copyright 2015, GNU Affero General Public License"
__credits__     = ["Marc Bertens"]
__license__     = "AGPL"
__version__     = "1.0.0"
__maintainer__  = "Marc Bertens"
__email__       = "m.bertens@pe2mbs.nl"
__status__      = "Production"

from ajenti.api import *
from ajenti.plugins import *

info = PluginInfo(
    title           = 'common UI',
    description     = 'common UI elements',
    icon            = '',
    dependencies    = [
        PluginDependency( 'main' ),
    ],
)

def init():
    import main
# end def
