from ajenti.com import *
from ajenti.utils import *


class IComponent (Interface):
    """
    Base interface for background components.

    See :class:`Component`.
    """
    def run(self):
        pass


class Component (Plugin, BackgroundWorker):
    """
    Base class for a custom Component. Components are thread-safe objects (optionally
    containing a background thread) that are persisted for all the run time.

    - ``name`` - `str`, unique component ID
    """
    implements(IComponent)

    name = 'unknown'
    proxy = None
    abstract = True

    def __init__(self):
        BackgroundWorker.__init__(self)

    @classmethod
    def get(cls):
        """
        Convinience method, will return the component.
        Same as ``ComponentManager.get().find(name)``.
        """
        return ComponentManager.get().find(cls.name)

    def start(self):
        """
        Starts the component. For internal use only.
        """
        self.on_starting()
        BackgroundWorker.start(self)

    def stop(self):
        """
        Stops the component. For internal use only.
        """
        self.on_stopping()
        self.kill()
        self.on_stopped()

    def run(self):
        """
        Derived classes should put here the body of background thread (if any).
        """

    def on_starting(self):
        """
        Called when component is started. Use this instead of ``__init__``.
        """

    def on_stopping(self):
        """
        Called when component is about to be stopped. Thread is still running.
        """

    def on_stopped(self):
        """
        Called when component's thread has been stopped.
        """

    def unload(self):
        self.stop()


class ComponentManager (Plugin):
    """
    A general manager for all :class:`Component` classes.
    """
    instance = None

    @staticmethod
    def create(app):
        """
        Initializes the ComponentManager
        """
        ComponentManager.instance = ComponentManager(app)

    @staticmethod
    def get():
        """
        :returns: the ComponentManager instance
        """
        return ComponentManager.instance

    def __init__(self):
        self.components = []
        self.rescan()

    def stop(self):
        """
        Shutdowns all the components
        """
        for c in self.components:
            c.stop()

    def find(self, name):
        """
        Finds a :class:`Component` by ID.
        """
        for c in self.components:
            if c.name == name:
                return c.proxy

    def rescan(self):
        """
        Finds and starts any newly-found Components
        """
        for c in self.app.grab_plugins(IComponent):
            if not c in self.components:
                self.log.debug('Registered component: ' + c.name)
                c.proxy = ClassProxy(c)
                c.start()
                self.components.append(c)
