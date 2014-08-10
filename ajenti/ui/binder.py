import copy
import warnings

from ajenti.api import *
from ajenti.ui.element import p, UIElement
from ajenti.util import *


def is_bound_context(el):
    """
    :type el: UIElement
    :rtype: bool
    """
    return ('{binder}context' in el.properties) and el.properties['{binder}context'] is not None


def is_bound(el):
    """
    :type el: UIElement
    :rtype: bool
    """
    if el.typeid.startswith('bind:'):
        return True
    for prop in el.properties.keys():
        if prop == 'bind' or prop.startswith('{bind}') or is_bound_context(el):
            if el.properties[prop]:
                return True
    return False


@public
class Binding (object):
    """
    A base class for bindings. Binding is a link between a Python object attribute and Ajenti UI element's property.

    :param object: a Python object
    :param attribute: attribute name
    :param ui: Ajenti :class:`ajenti.ui.UIElement`
    """

    def __init__(self, object, attribute, ui):
        """
        :type object: object
        :type attribute: str
        :type ui: UIElement
        """
        self.object = object
        self.attribute = attribute
        self.ui = ui
        self.dict_mode = False
        if attribute and attribute.startswith('[') and attribute.endswith(']'):
            self.dict_mode = True
            self.attribute = self.attribute[1:-1]

    @classmethod
    def applicable(cls, object, attribute):
        try:
            cls.extract(object, attribute)
            return True
        except:
            return False

    @classmethod
    def extract(cls, object, attribute, ignore_errors=True):
        if attribute.startswith('[') and attribute.endswith(']'):
            if ignore_errors:
                return object.get(attribute[1:-1], None)
            else:
                return object.get[attribute[1:-1]]
        else:
            return getattr(object, attribute)

    def get(self):
        """
        :returns: value of the bound attribute
        """
        if self.dict_mode:
            return self.object.get(self.attribute, None)
        else:
            return getattr(self.object, self.attribute)

    def set(self, value):
        """
        Sets value of the bound attribute
        """
        try:
            if self.dict_mode:
                self.object[self.attribute] = value
            else:
                setattr(self.object, self.attribute, value)
        except Exception:
            raise Exception('Binder set failed: %s.%s = %s' % (self.object, self.attribute, repr(value)))

    def populate(self):
        """
        Should update the UI with attribute's value
        """

    def unpopulate(self):
        """
        Should revert UI to normal state
        """

    def update(self):
        """
        Should update the attribute with data from the UI
        """


@public
class PropertyBinding (Binding):
    """
    A simple binding between UI element's property and Python object's attribute

    :param property: UI property name. If ``None``, property is deduced from ``bindtypes``
    """

    def __init__(self, obj, attribute, ui, property=None):
        """
        :type attribute: str
        :type ui: UIElement
        :type property: str, None
        """
        Binding.__init__(self, obj, attribute, ui)
        if property is None:
            # find a property with matching bindtypes
            v = self.__get_transformed()
            for prop in ui.property_definitions.values():
                if prop.bindtypes:
                    # nb: we can't guess the type for None
                    if type(v) in prop.bindtypes or (v is None) or (object in prop.bindtypes):
                        self.property = prop.name
                        break
            else:
                raise Exception('Cannot bind %s.%s (%s, = %s) to %s' % (repr(obj), attribute, repr(type(v)), repr(v), ui))
        else:
            self.property = property
        self.oneway = ui.bindtransform is not None

    def __repr__(self):
        return u'[%s.%s <-> %s.%s]' % (self.object, self.attribute, self.ui, self.property)

    def __get_transformed(self):
        return self.ui.bindtransform(self.get()) if self.ui.bindtransform else self.get()

    def populate(self):
        self.old_value = self.get()
        setattr(self.ui, self.property, self.__get_transformed())

    def update(self):
        if self.oneway:
            return
        new_value = getattr(self.ui, self.property)
        # avoid unnecessary sets
        if new_value != self.old_value:
            self.set(new_value)


class DictValueBinding (PropertyBinding):
    def get(self):
        return self.object.get(self.attribute, None)

    def set(self, value):
        self.object[self.attribute] = value

    def update(self):
        if self.oneway:
            return
        self.set(getattr(self.ui, self.property))


@public
class ListAutoBinding (Binding):
    """
    Binds values of a collection to UI element's children consecutively, using :class:`Binder`
    """

    def __init__(self, object, attribute, ui):
        Binding.__init__(self, object, attribute, ui)
        self.binders = {}
        self.values = []

    def unpopulate(self):
        for binder in self.binders.values():
            binder.unpopulate()

    def populate(self):
        if self.attribute:
            self.collection = Binding.extract(self.object, self.attribute)
        else:
            self.collection = self.object
        self.values = self.ui.values(self.collection)

        self.unpopulate()

        self.binders = {}
        index = 0

        if len(self.values) > len(self.ui.children):
            raise Exception('Number of bind:list children is less than collection size')

        for value in self.values:
            template = self.ui.children[index]
            index += 1
            binder = Binder(value, template)
            binder.populate()
            self.binders[value] = binder
            self.ui.post_item_bind(self.object, self.collection, value, template)

        self.ui.post_bind(self.object, self.collection, self.ui)
        return self

    def update(self):
        for value in self.values:
            self.binders[value].update()
            self.ui.post_item_update(self.object, self.collection, value, self.binders[value].ui)


@public
class DictAutoBinding (Binding):
    """
    Binds values from a dict to UI element's children mapping 'bind' attribute to dict key, using :class:`Binder`
    """

    def __init__(self, object, attribute, ui):
        Binding.__init__(self, object, attribute, ui)
        self.binders = {}

    def unpopulate(self):
        for binder in self.binders.values():
            binder.unpopulate()

    def populate(self):
        if self.attribute:
            self.collection = Binding.extract(self.object, self.attribute)
        else:
            self.collection = self.object
        self.values = self.ui.values(self.collection)

        self.unpopulate()

        self.binders = {}
        bindables = self.ui.nearest(
            lambda x: is_bound(x),
            exclude=lambda x: (
                x != self.ui and is_bound_context(x.parent) and x.parent != self.ui
            )
        )

        for bindable in bindables:
            if bindable == self.ui:
                continue

            for prop in bindable.properties:
                if not bindable.properties[prop]:
                    continue
                if prop.startswith('{bind}'):
                    binder = DictValueBinding(self.values, bindable.properties[prop], bindable, prop.split('}')[1])
                elif prop == 'bind':
                    binder = DictValueBinding(self.values, bindable.bind, bindable)
                else:
                    continue
                key = bindable.properties[prop]
                binder.populate()
                self.binders[key] = binder

        self.ui.post_bind(self.object, self.collection, self.ui)
        return self

    def update(self):
        for key in self.binders:
            self.binders[key].update()
            self.ui.post_item_update(self.object, self.collection, key, self.binders[key].ui)


def _element_in_child_binder(root, e):
    """
    detect if the element is trapped inside a nested bind: tag
    relative to e

    :type root: UIElement
    :type e: UIElement
    :rtype: bool
    """
    return any(x.typeid.startswith('bind:') for x in root.path_to(e))


def _element_in_child_template(root, e):
    """
    detect if the element is trapped inside a nested bind: tag
    relative to e

    :type root: UIElement
    :type e: UIElement
    :rtype: bool
    """
    return any(x.typeid.startswith('bind:template') for x in root.path_to(e))


@public
class CollectionAutoBinding (Binding):
    """
    Binds values of a collection to UI element's children using a template.
    The expected UI layout::

        <xml xmlns:bind="bind">
            <bind:collection id="<binding to this>">
                <container-element bind="__items">
                    <1-- instantiated templates will appear here -->
                </container-element>

                <bind:template>
                    <!-- a template for one collection item
                         it will be bound to item using ajenti.ui.binder.Binder -->
                    <label bind="some_property" />

                    <button id="__delete" /> <!-- a delete button may appear in the template -->
                </bind:template>

                <button id="__add" /> <!-- an add button may appear inside collection tag -->
            </bind:collection>
        </xml>
    """

    def __init__(self, object, attribute, ui):
        Binding.__init__(self, object, attribute, ui)
        self.template = ui.find_type('bind:template')
        if self.template:
            if self.template.children:
                self.template = self.template.children[0]
            self.template_parent = self.template.parent
            self.template.visible = False
        self.items_ui_element = self.ui.nearest(lambda x: x.bind == '__items')[0] or self.ui
        self.old_items = copy.copy(self.items_ui_element.children)

        self.item_ui = []
        self.binders = []
        self.values = []

        self.last_template_hash = None

    def unpopulate(self):
        if self.template:
            self.template_parent.append(self.template)
        self.items_ui_element.empty()
        # restore original container content
        self.items_ui_element.children = copy.copy(self.old_items)
        return self

    def get_template(self, item, ui):
        # override for custom item template creation
        return self.template.clone()

    def populate(self):
        if self.template:
            self.template_parent.remove(self.template)

        if self.attribute:
            self.collection = self.get()
        else:
            self.collection = self.object

        self.values = self.ui.values(self.collection)
        if self.ui.sorting:
            self.values = sorted(self.values, key=self.ui.sorting)

        self.unpopulate()

        # Do it before DOM becomes huge
        self.items_ui_element.on('add', self.on_add)

        try:
            add_button = self.ui.nearest(lambda x: x.bind == '__add')[0]
            if not _element_in_child_binder(self.ui, add_button):
                add_button.on('click', self.on_add)
        except IndexError:
            pass

        if self.ui.pagesize:
            try:
                self.paging = None
                paging = self.ui.nearest(lambda x: x.bind == '__paging')[0]
                if not _element_in_child_binder(self.ui, paging):
                    self.paging = paging
                    paging.on('switch', self.set_page)
                    paging.length = int((len(self.values) - 1) / self.ui.pagesize) + 1
            except IndexError:
                pass

        self.item_ui = {}
        self.binders = {}
        for index, value in enumerate(self.values):
            # apply the filter property
            if not self.ui.filter(value):
                continue

            template = self.get_template(value, self.ui)
            template.visible = True
            self.items_ui_element.append(template)
            self.item_ui[index] = template

            binder = Binder(value, template)
            binder.populate()
            self.binders[index] = binder

            try:
                del_button = template.nearest(lambda x: x.bind == '__delete')[0]
                if not _element_in_child_binder(template, del_button):
                    del_button.on('click', self.on_delete, value)
            except IndexError:
                pass

            self.ui.post_item_bind(self.object, self.collection, value, template)

        self.set_page(0)
        self.ui.post_bind(self.object, self.collection, self.ui)
        return self

    def set_page(self, page=0):
        if self.ui.pagesize:
            for index, value in enumerate(self.values):
                self.item_ui[index].visible = int(index / self.ui.pagesize) == page
            if self.paging:
                self.paging.active = page

    def on_add(self):
        self.update()
        self.ui.add_item(self.ui.new_item(self.collection), self.collection)
        self.populate()

    def on_delete(self, item):
        self.update()
        self.ui.delete_item(item, self.collection)
        self.populate()

    def update(self):
        if hasattr(self.items_ui_element, 'sortable') and self.items_ui_element.order:
            sortable_indexes = []
            for i, e in enumerate(self.items_ui_element.children):
                if e.visible:
                    sortable_indexes.append(i)

            try:
                absolute_order = [sortable_indexes[i - 1] for i in self.items_ui_element.order]
                indexes_valid = True
            except IndexError:
                indexes_valid = False

            if indexes_valid:
                new_indexes = []
                absolute_order_idx = 0
                for i in range(len(self.values)):
                    if i in sortable_indexes:
                        new_indexes.append(absolute_order[absolute_order_idx])
                        absolute_order_idx += 1
                    else:
                        new_indexes.append(i)
                
                shuffle = lambda a: dict([(old, a[i]) for old, i in enumerate(new_indexes) if i < len(self.collection)])
                self.binders = shuffle(self.binders)
                self.item_ui = shuffle(self.item_ui)

                new_values = [self.values[i] for i in new_indexes if i < len(self.collection)]
                while len(self.collection) > 0:
                    self.collection.pop(0)
                for e in new_values:
                    self.collection.append(e)

                self.items_ui_element.order = []

        for index, value in enumerate(self.values):
            if self.ui.filter(value):
                self.binders[index].update()
                self.ui.post_item_update(self.object, self.collection, value, self.binders[index].ui)


@public
class Binder (object):
    """
    An automatic object-to-ui-hierarchy binder. Uses ``bind`` UI property to find what and where to bind.
    If ``object`` is not None, the Binder is also initialized (see ``setup(object)``) with this data object.

    :param object: Python object
    :param ui: UI hierarchy root
    """

    def __init__(self, object=None, ui=None):
        self.bindings = []
        self.ui = ui
        if object is not None:
            self.setup(object)

    def __warn_new_binder(self, s):
        import traceback; traceback.print_stack();
        warnings.warn(s, DeprecationWarning)
        print('Binding syntax has been changed: see http://docs.ajenti.org/en/latest/dev/binding.html')

    def setup(self, object=None):
        """
        Initializes the Binder with a data object.
        :type object: object
        """
        self.unpopulate()
        if object is not None:
            self.object = object
        self.__autodiscover()
        return self

    def reset(self, object=None, ui=None):
        """
        Cancels the binding and replaces Python object / UI root.

        :type object: object
        :type ui: UIElement, None
        """
        self.__warn_new_binder('Binder.reset(object, ui)')
        self.unpopulate()
        if object is not None:
            self.object = object
        if ui:
            self.ui = ui
        return self

    def autodiscover(self, object=None, ui=None):
        self.__warn_new_binder('Binder.autodiscover(object, ui)')
        self.__autodiscover(object, ui)
        return self

    def __autodiscover(self, object=None, ui=None):
        """
        Recursively scans UI tree for ``bind`` properties, and creates bindings.
        """

        # Initial call
        if object is None and ui is None:
            self.bindings = []

        if ui is None:
            ui = self.ui
        if object is None:
            object = self.object

        bindables = ui.nearest(
            lambda x: is_bound(x),
            exclude=lambda x: (
                x.parent != ui and x != ui and (
                    '{bind}context' in x.parent.properties  # skip nested contexts
                    or x.parent.typeid.startswith('bind:')  # and templates and nested collections
                )
            )
        )

        for bindable in bindables:
            # Custom/collection binding
            if bindable.typeid.startswith('bind:'):
                k = bindable.bind
                if k and Binding.applicable(object, k):
                    self.add(bindable.binding(object, k, bindable))
                continue

            for prop in bindable.properties:
                if not prop.startswith('{bind') and prop != 'bind':
                    continue

                k = bindable.properties[prop]

                # Nested binder context
                if prop == '{binder}context':
                    if bindable is not ui and k:
                        if Binding.applicable(object, k):
                            self.__autodiscover(Binding.extract(object, k), bindable)

                # Property binding
                if prop.startswith('{bind}') or prop == 'bind':
                    propname = None if prop == 'bind' else prop.split('}')[1]
                    if k and Binding.applicable(object, k):
                        self.add(PropertyBinding(object, k, bindable, propname))

        return self

    def add(self, binding):
        self.bindings.append(binding)

    def populate(self):
        """
        Populates the bindings.
        """
        for binding in self.bindings:
            binding.populate()
        return self

    def unpopulate(self):
        """
        Unpopulates the bindings.
        """
        for binding in self.bindings:
            binding.unpopulate()
        return self

    def update(self):
        """
        Updates the bindings.
        """
        for binding in self.bindings:
            binding.update()
        return self


# Helper elements
@p('post_bind', default=lambda o, c, u: None, type=eval, public=False,
    doc='Called after binding is complete, ``lambda object, collection, ui: None``')
@p('post_item_bind', default=lambda o, c, i, u: None, type=eval, public=False,
    doc='Called after an item is bound, ``lambda object, collection, item, item-ui: None``')
@p('post_item_update', default=lambda o, c, i, u: None, type=eval, public=False,
    doc='Called after an item is updated, ``lambda object, collection, item, item-ui: None``')
@p('binding', default=ListAutoBinding, type=eval, public=False,
    doc='Collection binding class to use')
@p('filter', default=lambda i: True, type=eval, public=False,
    doc='Called to filter collection''s values, ``lambda value: bool``')
@p('values', default=lambda c: c, type=eval, public=False,
    doc='Called to extract values from the collection, ``lambda collection: []``')
@public
class BasicCollectionElement (UIElement):
    pass


@public
@plugin
class ListElement (BasicCollectionElement):
    typeid = 'bind:list'


@public
@p('add_item', default=lambda i, c: c.append(i), type=eval, public=False,
    doc='Called to append value to the collection, ``lambda item, collection: None``')
@p('new_item', default=lambda c: None, type=eval, public=False,
    doc='Called to create an empty new item, ``lambda collection: object()``')
@p('delete_item', default=lambda i, c: c.remove(i), type=eval, public=False,
    doc='Called to remove value from the collection, ``lambda item, collection: None``')
@p('sorting', default=None, type=eval, public=False,
    doc='If defined, used as key function to sort items')
@p('pagesize', default=0, type=int, public=False)
@p('binding', default=CollectionAutoBinding, type=eval, public=False)
@plugin
class CollectionElement (BasicCollectionElement):
    typeid = 'bind:collection'


@p('binding', default=DictAutoBinding, type=eval, public=False)
@plugin
class DictElement (BasicCollectionElement):
    typeid = 'bind:dict'
