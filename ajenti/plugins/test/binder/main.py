from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


class Person (object):
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return '{%s: %s}' % (self.name, self.phone)


@plugin
class SimpleDemo (SectionPlugin):
    def init(self):
        self.title = 'Binder'
        self.icon = 'question'
        self.category = 'Demo'

        self.append(self.ui.inflate('test:binder-main'))

        self.data = [
            Person('Alice', '123'),
            Person('Bob', '234'),
        ]

        self.dict = {
            'a': 1,
            'b': 2,
        }

        self.find('data').text = repr(self.data)

        self.binder = Binder(self, self.find('bindroot'))

    @on('populate', 'click')
    def on_populate(self):
        self.binder.populate()

    @on('unpopulate', 'click')
    def on_unpopulate(self):
        self.binder.unpopulate()

    @on('update', 'click')
    def on_update(self):
        self.binder.update()
        self.find('data').text = repr(self.data)