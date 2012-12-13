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
                if type(self.get()) in prop.bindtypes or type(self.get()) == type(None):
                    self.property = prop.name
                    break
            else:
                raise Exception('Cannot bind %s.%s' % (object, field))
        else:
            self.property = property

    def populate(self):
        self.old_value = self.get()
        self.ui.properties[self.property].value = self.ui.bindtransform(self.get())

    def update(self):
        new_value = self.ui.properties[self.property].value
        if new_value != self.old_value:
            self.set(new_value)


class CollectionAutoBinding (Binding):
    def __init__(self, object, field, ui):
        Binding.__init__(self, object, field, ui)
        self.template = ui.find_type('bind:template')
        self.template_parent = self.template.parent
        self.template.visible = False
        self.items_ui = self.ui.nearest(lambda x: x.bind == '__items')[0] or self.ui
        self.old_items = copy.copy(self.items_ui.children)

    def unpopulate(self):
        self.template_parent.append(self.template)
        self.items_ui.empty()
        self.items_ui.children = copy.copy(self.old_items)
        return self

    def _element_in_child_binder(self, root, e):
        return any(x.typeid.startswith('bind:') for x in root.path_to(e))

    def populate(self):
        self.template_parent.remove(self.template)

        if self.field:
            self.collection = getattr(self.object, self.field)
        else:
            self.collection = self.object
        self.values = self.ui.values(self.collection)

        self.unpopulate()

        self.binders = {}
        for value in self.values:
            template = self.template.clone()
            template.visible = True
            self.items_ui.append(template)
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
        for value in self.values:
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
            #print object, k, dir(object)
            v = getattr(object, k)
            children = (ui or self.ui).nearest(lambda x: x.bind == k)
            for child in children:
                if child == ui:
                    raise Exception('Circular UI reference for %s!' % k)
                if type(v) in [str, unicode, int, float, bool, property, type(None)] or v is None:
                    self.add(PropertyBinding(object, k, child))
                elif not hasattr(v, '__iter__'):
                    self.autodiscover(v, child)
                else:
                    if not child.typeid.startswith('bind:collection'):
                        raise Exception('Collection %s (%s) only binds to <bind:collection />' % (k, type(v)))
                    self.add(child.binding()(object, k, child))
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
@p('add_item', default=lambda i, c: c.append(i), type=eval, public=False)
@p('new_item', default=lambda c: None, type=eval, public=False)
@p('delete_item', default=lambda i, c: c.remove(i), type=eval, public=False)
@p('post_bind', default=lambda o, c, u: None, type=eval, public=False)
@p('post_item_bind', default=lambda o, c, i, u: None, type=eval, public=False)
@p('post_item_update', default=lambda o, c, i, u: None, type=eval, public=False)
@p('binding', default=lambda: CollectionAutoBinding, type=eval, public=False)
@p('values', default=lambda c: c, type=eval, public=False)
@plugin
class CollectionElement (UIElement):
    typeid = 'bind:collection'
