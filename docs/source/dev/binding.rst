.. _dev-binding:

UI Bindings
***********

Binding mechanism lets you bind your Python objects directly to UI elements and build CRUD interfaces in minutes.

Example
=======

Consider these data objects and code::

    from ajenti.api import *
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on
    from ajenti.ui.binder import Binder


    class Phone (object):
        def __init__(self, number):
            self.number = number


    class Person (object):
        def __init__(self, name, phones):
            self.name = name
            self.phones = phones


    class AddressBook (object):
        def __init__(self, persons):
            self.persons = persons


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Test'
            self.icon = 'question'
            self.category = 'Demo'

            self.append(self.ui.inflate('test:main'))

            alice = Person('Alice', [Phone('123')])
            bob = Person('Bob', [Phone('234'), Phone('345')])
            book = AddressBook([alice, bob])

            self.binder = Binder(book, self.find('addressbook'))
            self.binder.autodiscover().populate()

Now we only need to define appropriate templates in the layout file::

    <body xmlns:bind="bind">
        <pad id="addressbook">
            <bind:collection bind="persons" id="persons-collection">
                <dt bind="__items" width="1" />

                <bind:template>
                    <dtr>
                        <dtd>
                            <label bind="name" />
                        </dtd>
                        <dtd>
                            <bind:collection bind="phones" id="phones-collection">
                                <vc bind="__items" />
                                <bind:template>
                                    <label bind="number" />
                                </bind:template>
                            </bind:collection>
                        </dtd>
                    </dtr>
                </bind:template>
            </bind:collection>
        </pad>
    </body>

CRUD Example
============

Code::

    from ajenti.api import *
    from ajenti.plugins.main.api import SectionPlugin
    from ajenti.ui import on
    from ajenti.ui.binder import Binder


    class Phone (object):
        def __init__(self, number):
            self.number = number


    class Person (object):
        def __init__(self, name, phones):
            self.name = name
            self.phones = phones


    class AddressBook (object):
        def __init__(self, persons):
            self.persons = persons


    @plugin
    class Test (SectionPlugin):
        def init(self):
            self.title = 'Test'
            self.icon = 'question'
            self.category = 'Demo'

            self.append(self.ui.inflate('test:main'))

            alice = Person('Alice', [Phone('123')])
            bob = Person('Bob', [Phone('234'), Phone('345')])
            book = AddressBook([alice, bob])

            self.find('persons-collection').new_item = lambda c: Person('New person', [])
            self.find('phones-collection').new_item = lambda c: Phone('123')

            self.binder = Binder(book, self.find('addressbook'))
            self.binder.autodiscover().populate()

Layout::

    <body xmlns:bind="bind">
        <pad id="addressbook">
            <bind:collection bind="persons" id="persons-collection">
                <vc>
                    <dt bind="__items" width="1" />
                    <button bind="__add" icon="plus" text="Create" />
                </vc>

                <bind:template>
                    <dtr>
                        <dtd>
                            <textbox bind="name" />
                        </dtd>
                        <dtd>
                            <bind:collection bind="phones" id="phones-collection">
                                <vc>
                                    <vc bind="__items" />
                                    <button bind="__add" icon="plus" text="Create" />
                                </vc>
                                <bind:template>
                                    <hc>
                                        <textbox bind="number" />
                                        <button bind="__delete" icon="remove" style="mini" />
                                    </hc>
                                </bind:template>
                            </bind:collection>
                        </dtd>
                        <dtd width="1">
                            <button bind="__delete" icon="remove" style="mini" />
                        </dtd>
                    </dtr>
                </bind:template>
            </bind:collection>
        </pad>
    </body>

Note the **Add** and **Remove** buttons with special **bind** property values.

.. image:: /_static/dev/binding/example2.png
