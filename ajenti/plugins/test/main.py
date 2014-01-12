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

        self.binder = Binder(None, self.find('addressbook'))
        self.binder.setup(book).populate()
