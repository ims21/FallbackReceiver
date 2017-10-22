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
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eTimer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigSubList, ConfigIP, ConfigInteger, ConfigText, getConfigListEntry
import skin

config.plugins.fallback = ConfigSubsection()
config.plugins.fallback.entriescount = ConfigInteger(0)
config.plugins.fallback.receivers = ConfigSubList()


def initFallbackReceiverConfig():
	config.plugins.fallback.receivers.append(ConfigSubsection())
	i = len(config.plugins.fallback.receivers) -1
	config.plugins.fallback.receivers[i].name = ConfigText(default = _("Remote receiver"), visible_width = 30, fixed_size = False)
	config.plugins.fallback.receivers[i].ip = ConfigIP(default = [192,168,1,100])
	return config.plugins.fallback.receivers[i]

def initConfig():
	count = config.plugins.fallback.entriescount.value
	if count != 0:
		i = 0
		while i < count:
			initFallbackReceiverConfig()
			i += 1

initConfig()

class FallbackReceivers(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="560,420" title="Set Fallback Receiver" >
			<ePixmap name="red" position="0,0" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget  name="key_red" position="0,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1"/>
			<widget  name="key_green" position="140,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="green" font="Regular;20" transparent="1"/>
			<widget  name="key_yellow" position="280,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="yellow" font="Regular;20" transparent="1"/>
			<widget  name="key_blue" position="420,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="blue" font="Regular;20" transparent="1"/>
			<widget name="fallback" position="5,50" size="550,25" font="Regular;22" halign="left"/>
			<widget name="name" position="5,80" size="275,25" font="Regular;22" halign="left"/>
			<widget name="ip" position="280,80" size="275,25" font="Regular;22" halign="left"/>
			<widget name="entrylist" position="5,110" size="550,300" scrollbarMode="showOnDemand"/>
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.setTitle(_("Set Fallback Receiver"))

		self["fallback"] = Label(_("Current:  %s") % config.usage.remote_fallback.value )
		self["name"] = Label(_("Name"))
		self["ip"] = Label(_("IP"))

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Set"))
		self["key_yellow"] = Button(_("Edit"))
		self["key_blue"] = Button(_("Add"))

		self["entrylist"] = FallbackReceiversList([])
		self["entrylist"].onSelectionChanged.append(self.changedEntry)

		self["actions"] = ActionMap(["OkCancelActions","ColorActions"],
			{
			"ok":		self.setAsFallback,
			"cancel":	self.keyClose,
			"green":	self.setAsFallback,
			"red":		self.keyClose,
			"yellow":	self.keyEdit,
			"blue": 	self.keyAdd,
			 }, -1)

		self.msgNM=None
		self.onLayoutFinish.append(self.updateList)

	def updateList(self):
		self["entrylist"].buildList()

	def changedEntry(self):
		self.MessageBoxNM()

	def keyClose(self):
		self.close()

	def keyAdd(self):
		self.session.openWithCallback(self.updateList, FallbackReceiverConfigScreen, None)

	def keyEdit(self):
		try:
			sel = self["entrylist"].l.getCurrentSelection()[0]
		except:
			sel = None
		self.session.openWithCallback(self.updateList, FallbackReceiverConfigScreen, sel)

	def setAsFallback(self):
		try:
			sel = self["entrylist"].l.getCurrentSelection()[0]
		except:
			sel = None
		if sel is None:
			return
		ip = "%d.%d.%d.%d" % tuple(sel.ip.value)
		if not ip:
			return
		new_fallback = "http://%s:8001" % ip
		if new_fallback == config.usage.remote_fallback.value:
			self.MessageBoxNM(True, _("This box is used as remote fallback receiver"), 3)
			return
		def fallbackConfirm(result):
			if not result:
				return
			config.usage.remote_fallback.value = new_fallback
			config.usage.remote_fallback.save()
			self["fallback"].setText(_("Current:  %s") % config.usage.remote_fallback.value )
		self.session.openWithCallback(fallbackConfirm, MessageBox, _("Set %s as fallback remote receiver?") % sel.name.value)

	def MessageBoxNM(self, display=False, text="", delay=0):
		if self.msgNM:
			self.session.deleteDialog(self.msgNM)
			self.msgNM = None
		else:
			if display and self.session is not None:
				self.msgNM = self.session.instantiateDialog(NonModalMessageBoxDialog, text=text, delay=delay)
				self.msgNM.show()


class FallbackReceiversList(MenuList):
	def __init__(self, list, enableWrapAround = True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		font = skin.fonts.get("FallbackReceiverList0", ("Regular", 22, 25))
		self.l.setFont(0, gFont(font[0], font[1]))
		self.ItemHeight = int(font[2])
		font = skin.fonts.get("FallbackReceiverList1", ("Regular", 22))
		self.l.setFont(1, gFont(font[0], font[1]))
	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		instance.setItemHeight(self.ItemHeight)

	def buildList(self):
		self.list=[]
		index = 0
		position = 0
		current = config.usage.remote_fallback.value.replace("http://","").replace(":8001","")
		for c in config.plugins.fallback.receivers:
			res = [c]
			x, y, w, h = skin.parameters.get("FallbackReceiverListName",(5, 0, 250, 20))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.name.value)))
			ip = "%d.%d.%d.%d" % tuple(c.ip.value)
			if ip == current:
				position = index
			x, y, w, h = skin.parameters.get("FallbackReceiverListIP",(260, 0, 250, 20))
			res.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(ip)))
			self.list.append(res)
			index += 1
		self.l.setList(self.list)
		self.moveToIndex(position)

class FallbackReceiverConfigScreen(ConfigListScreen, Screen):
	skin = """
		<screen name="FallbackReceiverConfigScreen" position="center,center" size="560,110" title="Edit Remote Receiver">
			<ePixmap name="red" position="0,0" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget  name="key_red" position="0,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1"/>
			<widget  name="key_green" position="140,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="green" font="Regular;20" transparent="1"/>
			<widget  name="key_yellow" position="280,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="yellow" font="Regular;20" transparent="1"/>
			<widget  name="key_blue" position="420,0" size="140,40" zPosition="1" valign="center" halign="center" backgroundColor="blue" font="Regular;20" transparent="1"/>
			<widget name="config" position="5,50" size="550,100" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, entry):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("Edit Remote Receiver"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"blue": self.keyDelete,
		}, -2)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Delete"))

		if entry is None:
			self.newmode = True
			self.current = initFallbackReceiverConfig()
		else:
			self.newmode = False
			self.current = entry

		ConfigListScreen.__init__(self, [], session)
		self.onLayoutFinish.append(self.initConfig)

	def initConfig(self):
		list = [
			getConfigListEntry(_("Name"), self.current.name),
			getConfigListEntry(_("IP"), self.current.ip),
		]
		self["config"].list = list
		self["config"].l.setList(list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.initConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.initConfig()

	def keyDelete(self):
		if self.newmode:
			self.keyCancel()
		else:
			self.session.openWithCallback(self.deleteConfirm, MessageBox, _("Really delete %s?") % self.current.name.value )

	def deleteConfirm(self, result):
		if not result:
			return
		config.plugins.fallback.entriescount.value = config.plugins.fallback.entriescount.value - 1
		config.plugins.fallback.entriescount.save()
		config.plugins.fallback.receivers.remove(self.current)
		config.plugins.fallback.receivers.save()
		config.plugins.fallback.save()
		self.close()

	def keySave(self):
		if self.newmode:
			config.plugins.fallback.entriescount.value = config.plugins.fallback.entriescount.value + 1
			config.plugins.fallback.entriescount.save()
		ConfigListScreen.keySave(self)
		config.plugins.fallback.save()
		self.close()

	def keyCancel(self):
		if self.newmode:
			config.plugins.fallback.receivers.remove(self.current)
		ConfigListScreen.cancelConfirm(self, True)

class NonModalMessageBoxDialog(Screen):
	skin="""
		<screen name="NonModalMessageBoxDialog" position="center,center" size="470,120" backgroundColor="#00404040" zPosition="2" flags="wfNoBorder">
			<widget name="message" position="center,center" size="460,110" font="Regular;20" valign="center" halign="center"/>
		</screen>
	"""
	def __init__(self, session, text="", delay=0):
		Screen.__init__(self, session)
		self.text = text
		self.delay = delay
		self["message"]=Label()

		self.timer = eTimer()
		self.timer.callback.append(self.timerLoop)

		self.onLayoutFinish.append(self.timerStart)

	def timerStart(self):
		self["message"].setText(self.text)
		self.timer.start(1000, True)

	def timerLoop(self):
		self.delay -= 1
		if self.delay > 0:
			self.timer.start(1000, True)
		else:
			self.session.deleteDialog(self)