.. _dev-notifications:

Notifications
*************

Example
=======

Code::

    from ajenti.api import plugin
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Notifications'
            self.icon = 'smile'
            self.category = 'Demo'

            self.append(self.ui.inflate('test_notifications:main'))
            self.find('style').labels = self.find('style').values = ['info', 'warning', 'error']

        @on('show', 'click')
        def on_show(self):
            self.context.notify(self.find('style').value, self.find('text').value)

Layout::

    <body>
        <pad>
            <vc>
                <formline text="Text">
                    <textbox id="text" />
                </formline>
                <formline text="Style">
                    <dropdown id="style" />
                </formline>
                <formline>
                    <button icon="ok" id="show" text="Show" />
                </formline>
            </vc>
        </pad>
    </body>

`Download this example </_static/dev/test_notifications.tar.gz>`_
