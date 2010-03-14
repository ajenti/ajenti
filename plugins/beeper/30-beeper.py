from plugin import PluginMaster, PluginInstance #Import base plugin classes from Ajenti's plugin.py
import commands
import session # Ajenti session controller
import ui # Ajenti WebUI
import log
import tools # Support for actions

# Plugins themselves consist of two parts: Master plugin and Instance plugin
# The Master plugin is launched when Ajenti server starts
# The Instance plugins are launched one per user session

class BeeperPluginMaster(PluginMaster):
	name = 'Beeper'

	def _on_load(self): # This event is fired when Ajenti loads the plugin
		PluginMaster._on_load(self)

	def make_instance(self): # Should return a new Instance plugin
		i = BeeperPluginInstance(self)
		self.instances.append(i)
		return i


class BeeperPluginInstance(PluginInstance):
	# Standard properties
	name = 'Beeper'

	# Our custom stuff
	_tblBeeps = None
	_btnAdd = None
	_txtCmd = None
	Beeps = None

	def _on_load(self, s): # The session controller instance is passed to this method
		PluginInstance._on_load(self, s)

		# Build a category switcher for Ajenti
		c = ui.Category()
		c.text = 'Beeper'
		c.description = 'Beep-beep-beep!'
		c.icon = 'plug/beeper;icon' # This means that image is stored in plugins/beeper/icon.png
		self.category_item = c # The category_item property will be later examined by Core plugin. If it isn't None, the new Category will be added to the UI

		self.build_panel()

		# Make use of /etc/ajenti/beeper.conf
		self.Beeps = BeepingProfiles()
		log.info('BeeperPlugin', 'Started instance') # Available methods are log.info, log.warn, log.err. The first parameter is 'sender' name, the second is string being logged

	def build_panel(self):
		# The Ajenti web UI has tree-like structure based on containers

		# Make a header
		l = ui.Label('Beeper demo plugin')
		l.size = 5

		# The top block
		c = ui.HContainer([ui.Image('plug/ajentibackup;bigicon.png'), ui.Spacer(10, 1), l])

		# Profiles table
		self._tblBeeps = ui.DataTable()
		self._tblBeeps.title = 'Beeping profiles'
		self._tblBeeps.widths = [300, 100] # The column widths
		r = ui.DataTableRow([ui.Label('Params'), ui.Label('Control')])
		r.is_header = True
		self._tblBeeps.rows.append(r)

		# The main area
		d = ui.VContainer()
		d.add_element(self._tblBeeps)
		d.add_element(ui.Spacer(1,10))

		self._txtCmd = ui.Input()
		self._btnAdd = ui.Button('Add new')
		self._btnAdd.handler = self._on_add_clicked

		d.AddElement(ui.Label('Beep parameters:'))
		d.AddElement(self._txtCmd)
		d.AddElement(self._btnAdd)

		# Assemble the stuff altogether
		self.Panel = ui.VContainer([c, d])
		return


	def Update(self): # The method is fired when user requests an updated UI view
		if self.Panel.Visible: # We can enhance Ajenti performance by not refreshing the stuff when it's not visible
			self.Beeps.Parse() # Reload profiles
			self._tblBeeps.Rows = [self._tblBeeps.Rows[0]] # Remove all rows but the header
			for k in self.Beeps.Profiles:
				l1 = ui.Link('Beep!')
				l2 = ui.Link('Delete')
				l1.Handler = self.HControlClicked
				l2.Handler = self.HControlClicked

				# We'll use custom field 'profile' to store profile this control link is for
				l1.Profile = k
				l2.Profile = k
				# And 'tag' property to remember what's the link for
				l1.Tag = 'beep'
				l2.Tag = 'delete'

				r = ui.DataTableRow([ui.Label(k), ui.HContainer([l1, l2])])
				self._tblBeeps.Rows.append(r)
			return


	def HAddClicked(self, t, e, d): # The parameters passed are: the control that caused event, the event name and optional event data
		self.Beeps.Profiles.append(self._txtCmd.Text)
		self._txtCmd.Text = ''
		self.Beeps.Save()


	def HControlClicked(self, t, e, d):
		if t.Tag == 'beep':
			tools.Actions['beeper/beep'].Run(t.Profile) # Call the beeper/beep action (see below)
		if t.Tag == 'delete':
			self.Beeps.Profiles.remove(t.Profile)
			self.Beeps.Save()
			return


# The Actions are common way for plugin interconnection. Here we define 'beep' action that can be later called by any other plugin
class BeepAction(tools.Action):
	Name = 'beep'
	Plugin = 'beeper'

	def Run(self, d): # Argument is an optional parameter passed to the Action
		try:
			tools.Actions['core/shell-run'].Run('beep ' + d)
			log.warn('Beeper', 'Beeping: ' + 'beep ' + d)
		except:
			pass


# Our class to handle the /etc/ajenti/beeper.conf file
# The file contains parameter sets for beep(1) command
class BeepingProfiles:
	Profiles = None

	def Parse(self):
		self.Profiles = []

		try:
			f = open('/etc/ajenti/beeper.conf', 'r')
			ss = f.read().splitlines()
			f.close()

			for s in ss:
				self.Profiles.append(s)
		except:
			pass

		return

	def Save(self):
		f = open('/etc/ajenti/beeper.conf', 'w')
		for x in self.Profiles:
			f.write(x + '\n')
		f.close()

		return
