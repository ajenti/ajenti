.. _dev-getting-started:

Getting Started with Plugin Development
***************************************

Prerequisites
=============

The following are the absolutely minimal set of software required to build and run Ajenti:

  * git
  * coffee-script (use NPM)
  * lessc (use NPM)

If you don't have CoffeeScript or LESS compiler, you won't be able to make changes to Ajenti CSS/JS files. In this case, download sources from PyPI, which includes compiled CSS/JS resources.

Debian/Ubuntu extras:

  * apt-show-versions
  * python-dbus (ubuntu)


Setting up
==========

Download the source::

    git clone git://github.com/Eugeny/ajenti.git

(or download them from PyPI: https://pypi.python.org/pypi/ajenti)

Install the dependencies::
  
    [sudo] pip install -Ur requirements.txt

Launch Ajenti in debug mode::

    make run

Navigate to http://localhost:8000/.

Press Ctrl-\ at any time to launch an interactive Python shell and Ctrl-D to resume Ajenti.

CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console.

Ajenti source code includes various example plugins under **Demo** category; their source is available in ``ajenti/plugins/test`` directory.


Creating new plugin package
===========================

New plugins can be placed in both ``<source>/ajenti/plugins/`` (if you expect inclusion in the source tree) and ``/var/lib/ajenti/plugins``.

Each plugin package consists of few Python modules, which contain :class:`ajenti.api.plugin` classes (*plugins*).
Packages also may contain :ref:`static files, CoffeeScript and LESS code <dev-resources>`, and XML user interface layouts::


    * ajenti
      * plugins
        * test
          * content
            * css
              - 1.less
            * js
              - 2.coffee
            * static
              - 3.png
          * layout
            - 4.xml
          - __init__.py
          - main.py




Plugins
=======

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
    class IShape (object):
        """
        This is an interface, specifying the methods required.
        """
        def number_of_corners(self):
            pass


    @plugin
    class Square (BasePlugin, IShape):
        """
        A sample implementation, note the inheritance from both BasePlugin (optional but gives extra options such as context management) and the interface.
        """

        def init(self):
            """
            init() methods are automatically called for plugins, maintaining inheritance hierarchy
            """
            print 'Square #%s initialized' % id(self)

        def number_of_corners(self):
            return 4


    @plugin
    class Circle (BasePlugin, IShape):
        def number_of_corners(self):
            return 0



    print 'IShape is implemented by', IShape.get_class()
    foo = IShape.get()  # get/create any instance of any IShape implementation
    # or, more verbose, IShape.get_class().new()
    print 'foo corners:', foo.number_of_corners()

    # The instances are by default singleton:
    print foo == IShape.get()  # True

    # But you can create separate ones:
    foo2 = IShape.get_class().new()
    print foo == foo2  # False, different instances


    for another_foo in IShape.get_all():  # iterate over all possible IShape implementations
        print '\n%s says:' % another_foo, another_foo.number_of_corners()


    print IShape.get_instances()  # lists all three active IShape instances

Output::

    IShape is implemented by <class 'ajenti.plugins.test.main.Square'>
    Square #24838864 initialized
    foo corners: 4
    True
    Square #24838928 initialized
    False

    <ajenti.plugins.test.main.Square object at 0x17b02d0> says: 4
    <ajenti.plugins.test.main.Circle object at 0x17b0390> says: 0
    [<ajenti.plugins.test.main.Square object at 0x17b02d0>, <ajenti.plugins.test.main.Square object at 0x17b0310>, <ajenti.plugins.test.main.Circle object at 0x17b0390>]


Learn about more interface and plugin methods here: :class:`ajenti.api.plugin`

Continue to :ref:`User Interface <dev-ui>`