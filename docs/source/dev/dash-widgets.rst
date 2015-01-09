Dashboard Widgets
*****************

Dashboard plugin API exposes two widget types: :class:`ajenti.plugins.dashboard.api.DashboardWidget` and :class:`ajenti.plugins.dashboard.api.ConfigurableWidget`.

Simple widget
=============

Example::

    from ajenti.api import plugin
    from ajenti.plugins.dashboard.api import DashboardWidget

    @plugin
    class HelloWidget (DashboardWidget):
        name = 'Hello Widget'
        icon = 'comment'

        def init(self):
            self.append(self.ui.inflate('hello_widget:widget'))
            self.find('text').text = 'Hello'

Layout::

    <hc>
        <box width="20">
            <icon id="icon" icon="comment" />
        </box>
        
        <box width="90">
            <label id="name" style="bold" text="Widget" />
        </box>

        <label id="text" />
    </hc>


Configurable widget
===================

Configurable widgets have a ``dict`` config, configuration dialog and a configuration button.

Example (real dashboard Text widget)::

    from ajenti.api import plugin
    from ajenti.plugins.dashboard.api import ConfigurableWidget


    @plugin
    class TextWidget (ConfigurableWidget):
        name = _('Text')
        icon = 'font'

        def on_prepare(self):
            # probably not configured yet!
            self.append(self.ui.inflate('dashboard:text'))

        def on_start(self):
            # configured by now
            self.find('text').text = self.config['text']

        def create_config(self):
            return {'text': ''}

        def on_config_start(self):
            # configuration begins now, a chance to fill the configuration dialog
            pass

        def on_config_save(self):
            self.config['text'] = self.dialog.find('text').value

Layout::

    <hc>
        <label id="text" text="---" />

        <dialog id="config-dialog" visible="False">
            <pad>
                <formline text="{Text}">
                    <textbox id="text" />
                </formline>
            </pad>
        </dialog>
    </hc>

