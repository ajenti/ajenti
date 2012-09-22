import os
import re

from ajenti.api import *

from ajenti.ui import *
from ajenti.ui.standard import *
from ajenti.plugins.main.api import SectionPlugin


@plugin
class Dash (SectionPlugin): 
	def init(self):
		self.counter = 0

		self.title = 'Dashboard'
		self.l = Label(self.ui, text = '0')
		self.append(self.l)

		self.b = Button(self.ui, text='test')
		self.b.on('click', self.on_button)
		self.append(self.b)

		self.append(Button(self.ui, text="Normal", style='normal'))
		self.append(Button(self.ui, text="Orange", style='orange'))
		self.append(Button(self.ui, text="Green", style='green'))

	def on_button(self):
		self.counter += 1
		self.l.text = str(self.counter)
		self.l.publish()

