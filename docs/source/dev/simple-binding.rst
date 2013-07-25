.. _dev-simple-binding:

Simple UI Bindings
******************

Binding mechanism lets you bind your Python objects directly to UI elements and build CRUD interfaces in minutes.

Example
=======

Code::

    from ajenti.api import plugin
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on
    from ajenti.ui.binder import Binder


    class Settings (object):  # use new-style object at all times!
        def __init__(self):
            self.label_text = ''
            self.label_bold = False
            self.label_style = ''


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Bindings'
            self.icon = 'smile'
            self.category = 'Demo'

            self.append(self.ui.inflate('test_bindings:main'))

            self.settings = Settings()

            # Bind the settings object to the section UI element (self)
            self.binder = Binder(self.settings, self)
            self.binder.autodiscover().populate()

        @on('apply', 'click')
        def on_apply(self):
            self.binder.update()  # update objects from UI
            self.settings.label_style = 'bold' if self.settings.label_bold else ''
            self.binder.populate()  # update UI with objects

Here, the ``Settings`` object acts as a data model. :class:`ajenti.ui.binder.Binder` object connects data with UI. ``autodiscover`` method scans the UI for bindable elements, ``populate`` method updates UI with the data from bound objects, and ``update`` method applies UI changes to objects.

Layout::

    <body>
        <pad>
            <vc>
                <formline text="Text">
                    <textbox bind="label_text" />
                </formline>
                <formline text="Bold">
                    <checkbox bind="label_bold" />
                </formline>
                <formline>
                    <button icon="ok" id="apply" text="Apply" />
                </formline>
                <formline text="Result">
                    <label bind:text="label_text" bind:style="label_style" />
                </formline>
            </vc>
        </pad>
    </body>

We have added ``bind`` attributes to the elements which are to be auto-populated with values. If you want to bind multiple properties, use XML attributes like ``bind:text`` or ``bind:style``.

.. image:: /_static/dev/simple-binding.png

`Download this example </_static/dev/test_bindings.tar.gz>`_
