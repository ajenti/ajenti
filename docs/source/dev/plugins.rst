.. _dev-plugins:

Plugins
*******

To get started, create an empty directory ``<source>/ajenti/plugins/test``.

Place a file called ``__init__.py`` there::

    from ajenti.api import *
    from ajenti.plugins import *


    info = PluginInfo(
        title='Test',
        icon=None,
        dependencies=[
            PluginDependency('main'),
        ],
    )


    def init():
        import main

In the same directory, create module ``main.py``. The comments explain the concept behind plugins architecture::

    from ajenti.api import *


    @interface
    class IFoo (object):
        """
        This is an interface, specifying the methods required.
        """
        def bar(self):
            pass


    @plugin
    class FooImplOne (BasePlugin, IFoo):
        """
        A sample implementation, note the inheritance from both BasePlugin (optional but gives extra options such as context management) and the interface.
        """

        def init(self):
            """
            init() methods are automatically called for plugins, maintaining inheritance hierarchy
            """
            print 'FooImpleOne #%s initialized' % id(self)

        def bar(self):
            print 'FooImplOne'


    @plugin
    class FooImplTwo (BasePlugin, IFoo):
        def bar(self):
            print 'FooImplTwo'



    print 'IFoo is implemented by', IFoo.get_class()
    foo = IFoo.get()  # get/create any instance of any IFoo implementation
    # or, more verbose, IFoo.get_class().new()
    print 'foo is', foo
    foo.bar()

    # The instances are by default singleton:
    print foo == IFoo.get()  # True

    # But you can create separate ones:
    foo2 = IFoo.get_class().new()
    print foo == foo2  # False, different instances


    for another_foo in IFoo.get_all():  # iterate over all possible IFoo implementations
        print '\n%s says:' % another_foo
        another_foo.bar()


    print IFoo.get_instances()  # lists all three active IFoo instances

Output::

    IFoo is implemented by <class 'ajenti.plugins.test.main.FooImplOne'>
    FooImpleOne #24838864 initialized
    foo is <ajenti.plugins.test.main.FooImplOne object at 0x17b02d0>
    FooImplOne
    True
    FooImpleOne #24838928 initialized
    False

    <ajenti.plugins.test.main.FooImplOne object at 0x17b02d0> says:
    FooImplOne

    <ajenti.plugins.test.main.FooImplTwo object at 0x17b0390> says:
    FooImplTwo
    [<ajenti.plugins.test.main.FooImplOne object at 0x17b02d0>, <ajenti.plugins.test.main.FooImplOne object at 0x17b0310>, <ajenti.plugins.test.main.FooImplTwo object at 0x17b0390>]


Learn about more interface and plugin methods here: :class:`ajenti.api.plugin`

Continue to :ref:`User Interface <dev-ui>`