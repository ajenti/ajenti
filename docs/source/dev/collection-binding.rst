.. _dev-collection-binding:

Collection Bindings
*******************

Ajenti supports following collection bindings:

  * Binding iterable to list of elements (:class:`ajenti.ui.binder.ListAutoBinding`)
  * Binding dict to key-annotated elements (:class:`ajenti.ui.binder.DictAutoBinding`)
  * Binding iterable with a child template (:class:`ajenti.ui.binder.CollectionAutoBinding`)

Example
=======

Code::
    
    import json

    from ajenti.api import plugin
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on
    from ajenti.ui.binder import Binder


    class Person (object):
        def __init__(self, name, **kwargs):
            self.name = name
            self.params = kwargs

        def __repr__(self):
            return json.dumps({'name': self.name, 'params': self.params})


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Collection Bindings'
            self.icon = 'smile'
            self.category = 'Demo'

            self.append(self.ui.inflate('test_bindings_collections:main'))

            andy = Person('andy', phone='123')
            bob = Person('bob', phone='321')

            self.obj_list = (andy, bob)
            self.obj_collection = [andy, bob]

            # This callback is used to autogenerate a new item with 'Add' button
            self.find('collection').new_item = lambda c: Person('new person', phone='000')

            self.binder = Binder(self, self)
            self.refresh()

        def refresh(self):
            self.binder.update()
            self.raw_data = repr(self.obj_collection)
            self.binder.reset().autodiscover().populate()

        @on('apply', 'click')
        def on_apply(self):
            self.refresh()

Layout::

    <body>
        <pad>
            <vc>
                <formline text="bind:list">
                    <bind:list bind="obj_list">
                        <box>
                            <label bind="name" />
                        </box>
                        <box>
                            <label bind="name" />
                        </box>
                    </bind:list>
                </formline>

                <formline text="bind:collection">
                    <bind:collection bind="obj_collection" id="collection">
                        <vc>
                            <dt bind="__items">
                                <dtr>
                                    <dth text="Name" />
                                    <dth text="Phone" />
                                    <dth />
                                </dtr>
                            </dt>
                            <button icon="plus" style="mini" bind="__add" />
                        </vc>

                        <bind:template>
                            <dtr>
                                <dtd> <textbox bind="name" /> </dtd>
                                
                                <dtd>
                                    <bind:dict bind="params">
                                        <textbox bind="phone" />
                                    </bind:dict>
                                </dtd>

                                <dtd> <button icon="remove" style="mini" bind="__delete" /> </dtd>
                            </dtr>
                        </bind:template>

                    </bind:collection>
                </formline>
                
                <formline text="Raw data">
                    <label bind="raw_data" />
                </formline>

                <formline>
                    <button icon="ok" id="apply" text="Apply" />
                </formline>
            </vc>
        </pad>
    </body>

Note the special ``bind`` attribute values used in ``bind:collection``:

  * ``__items`` denotes the container for items
  * ``__add`` denotes a button which will generate a new item (optional)
  * ``__remove`` denotes a button which will remove an item (optional)

.. image:: /_static/dev/collection-binding.png

`Download this example </_static/dev/test_bindings_collections.tar.gz>`_
