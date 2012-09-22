import os
import re

from ajenti.api import *

from ajenti.ui import *
from ajenti.ui.standard import *
from ajenti.plugins.main.api import SectionPlugin


@plugin
class Dash (SectionPlugin): 
	def init(self):
		self.title = 'Dashboard'

		self.append(self.ui.inflate('dashboard:dash'))
		self.label = self.find('label')
		self.button = self.find('button')
		self.submit = self.find('submit')
		self.flabel = self.find('flabel')

		self.counter = 0
		self.button.on('click', self.on_button)
		self.submit.on('click', self.on_submit)

	def on_button(self):
		self.counter += 1
		self.label.text = str(self.counter)
		self.label.publish()

	def on_submit(self):
		self.flabel.text = self.find('text').value
		self.publish()