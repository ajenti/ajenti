import copy

from ajenti.api import *
from ajenti.ui.element import p, UIElement


class Binding (object):
    def __init__(self, object, field, ui):
        self.object = object
        self.field = field
        self.ui = ui

    def get(self):
        return getattr(self.object, self.field)

    def set(self, value):
        setattr(self.object, self.field, value)

    def populate(self):
        pass

    def unpopulate(self):
        pass

    def update(self):
        pass


class PropertyBinding (Binding):
    def __init__(self, object, field, ui, property=None):
        Binding.__init__(self, object, field, ui)
        if property is None:
            for prop in ui.properties.values():
                if prop.bindtypes:
                    if type(self.get()) in prop.bindtypes or type(self.get()) == type(None) or ui.bindtransform:
                        self.property = prop.name
                        break
            else:
                raise Exception('Cannot bind %s.%s' % (object, field))
        else:
            self.property = property

    def populate(self):
        self.old_value = self.get()
        v = self.ui.bindtransform(self.get()) if self.ui.bindtransform else self.get()
        self.ui.properties[self.property].value = v

    def update(self):
        new_value = self.ui.properties[self.property].value
        if new_value != self.old_value:
            self.set(new_value)


class ListAutoBinding (Binding):
    def __init__(self, object, field, ui):
        Binding.__init__(self, object, field, ui)
        self.binders = {}

    def unpopulate(self):
        for binder in self.binders.values():
            binder.unpopulate()

    def populate(self):
        if self.field:
            self.collection = getattr(self.object, self.field)
        else:
            self.collection = self.object
        self.values = self.ui.values(self.collection)

        self.unpopulate()

        self.binders = {}
        index = 0
        for value in self.values:
            template = self.ui.children[index]
            index += 1
            binder = Binder(value, template)
            binder.autodiscover()
            binder.populate()
            self.binders[value] = binder
            self.ui.post_item_bind(self.object, self.collection, value, template)

        self.ui.post_bind(self.object, self.collection, self.ui)
        return self

    def update(self):
        for value in self.values:
            self.binders[value].update()
            self.ui.post_item_update(self.object, self.collection, value, self.binders[value].ui)


class CollectionAutoBinding (Binding):
    def __init__(self, object, field, ui):
        Binding.__init__(self, object, field, ui)
        self.template = ui.find_type('bind:template')
        if self.template:
            self.template_parent = self.template.parent
            self.template.visible = False
        self.items_ui = self.ui.nearest(lambda x: x.bind == '__items')[0] or self.ui
        self.old_items = copy.copy(self.items_ui.children)

        self.item_ui = {}
        self.binders = {}

    def unpopulate(self):
        if self.template:
            self.template_parent.append(self.template)
        self.items_ui.empty()
        self.items_ui.children = copy.copy(self.old_items)
        return self

    def _element_in_child_binder(self, root, e):
        return any(x.typeid.startswith('bind:') for x in root.path_to(e))

    def get_template(self, item, ui):
        return self.template.clone()

    def populate(self):
        if self.template:
            self.template_parent.remove(self.template)

        if self.field:
            self.collection = getattr(self.object, self.field)
        else:
            self.collection = self.object
        self.values = self.ui.values(self.collection)

        self.unpopulate()

        old_item_ui = self.item_ui
        old_binders = self.binders

        self.item_ui = {}
        self.binders = {}
        for value in self.values:
            if not self.ui.filter(value):
                continue

            if value in old_item_ui:
                template = old_item_ui[value]
            else:
                template = self.get_template(value, self.ui)
                template.visible = True
            self.items_ui.append(template)
            self.item_ui[value] = template
            if value in old_binders:
                binder = old_binders[value]
            else:
                binder = Binder(value, template)
                binder.autodiscover()
            binder.populate()
            self.binders[value] = binder

            try:
                del_button = template.nearest(lambda x: x.bind == '__delete')[0]
                if not self._element_in_child_binder(template, del_button):
                    del_button.on('click', self.on_delete, value)
            except IndexError:
                pass

            self.ui.post_item_bind(self.object, self.collection, value, template)

        try:
            add_button = self.ui.nearest(lambda x: x.bind == '__add')[0]
            if not self._element_in_child_binder(self.ui, add_button):
                add_button.on('click', self.on_add)
        except IndexError:
            pass

        self.ui.post_bind(self.object, self.collection, self.ui)
        return self

    def on_add(self):
        self.update()
        self.ui.add_item(self.ui.new_item(self.collection), self.collection)
        self.populate()

    def on_delete(self, item):
        self.update()
        self.ui.delete_item(item, self.collection)
        self.populate()

    def update(self):
        if hasattr(self.items_ui, 'sortable'):
            new_values = []
            for i in self.items_ui.order:
                if i - 1 < len(self.collection):
                    new_values.append(self.collection[i - 1])
            while len(self.collection) > 0:
                self.collection.pop(0)
            for e in new_values:
                self.collection.append(e)
        for value in self.values:
            if self.ui.filter(value):
                self.binders[value].update()
                self.ui.post_item_update(self.object, self.collection, value, self.binders[value].ui)


class Binder (object):
    def __init__(self, object=None, ui=None):
        self.bindings = []
        self.reset(object, ui)

    def reset(self, object=None, ui=None):
        self.unpopulate()
        if object:
            self.object = object
        if ui:
            self.ui = ui
        return self

    def autodiscover(self, object=None, ui=None):
        object = object or self.object
        for k in dir(object):
            v = getattr(object, k)
            children = (ui or self.ui).nearest(lambda x: x.bind == k)
            for child in children:
                if child == ui:
                    raise Exception('Circular UI reference for %s!' % k)
                if type(v) in [str, unicode, int, float, bool, property, type(None)] or v is None or child.bindtransform:
                    self.add(PropertyBinding(object, k, child))
                elif not hasattr(v, '__iter__'):
                    self.autodiscover(v, child)
                else:
                    if not hasattr(child, 'binding'):
                        raise Exception('Collection %s (%s) only binds to <bind:collection />' % (k, type(v)))
                    self.add(child.binding(object, k, child))
        return self

    def add(self, binding):
        self.bindings.append(binding)

    def populate(self):
        for binding in self.bindings:
            binding.populate()
        return self

    def unpopulate(self):
        for binding in self.bindings:
            binding.unpopulate()
        return self

    def update(self):
        for binding in self.bindings:
            binding.update()
        return self


# Helper elements
@p('post_bind', default=lambda o, c, u: None, type=eval, public=False)
@p('post_item_bind', default=lambda o, c, i, u: None, type=eval, public=False)
@p('post_item_update', default=lambda o, c, i, u: None, type=eval, public=False)
@p('binding', default=ListAutoBinding, type=eval, public=False)
@p('values', default=lambda c: c, type=eval, public=False)
@plugin
class ListElement (UIElement):
    typeid = 'bind:list'


@p('add_item', default=lambda i, c: c.append(i), type=eval, public=False)
@p('new_item', default=lambda c: None, type=eval, public=False)
@p('delete_item', default=lambda i, c: c.remove(i), type=eval, public=False)
@p('post_bind', default=lambda o, c, u: None, type=eval, public=False)
@p('post_item_bind', default=lambda o, c, i, u: None, type=eval, public=False)
@p('post_item_update', default=lambda o, c, i, u: None, type=eval, public=False)
@p('binding', default=CollectionAutoBinding, type=eval, public=False)
@p('values', default=lambda c: c, type=eval, public=False)
@p('filter', default=lambda i: True, type=eval, public=False)
@plugin
class CollectionElement (UIElement):
    typeid = 'bind:collection'
