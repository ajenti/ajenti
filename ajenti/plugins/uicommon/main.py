# coding=utf-8
# ---------------------------------------------------------------------------
#   common UI plugin for Ajenti, to provide general UI elements
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
from ajenti.api                 import *
from ajenti.ui                  import UIElement, p

@p('plugin',default='',type=str)
@p('title',default='',type=str)
@p('version',default='',type=str)
@p('pluginversion',default='0.1 Pre-alpha',type=str)
@p('author',default='',type=str)
@p('copyright',default='Copyright 2015, GNU Affero General Public License',type=str)
@p('email',default='',type=str)
@plugin
class PluginHeader( UIElement ):
    typeid = 'uicommon:header'
# end class
