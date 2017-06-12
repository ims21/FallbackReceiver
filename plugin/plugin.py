#
#  FallbackReceiver
#
#  $Id$
#
#  Coded by ims (c) 2017
#  Support: openpli.org
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

# for localized messages
from . import _

from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
	import ui
	session.open(ui.FallbackReceivers)

def startSetup(menuid):
	if menuid == "expert":
		return [(_("Set Fallback Receiver"), main, "fallbackreceiver", 0)]
	return []

def Plugins(**kwargs):
	return [PluginDescriptor(where = PluginDescriptor.WHERE_MENU, fnc = startSetup)]
