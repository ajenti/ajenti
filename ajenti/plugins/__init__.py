import imp
import os
import logging
import traceback


class PluginLoadError (Exception):
	pass

class PluginCrashed (PluginLoadError):
	def __init__(self, e):
		self.e = e

	def __str__(self):
		return 'crashed: %s' % self.e


class Dependency:
    class Unsatisfied (PluginLoadError):
    	def __init__(self):
    		self.dependency = None

    	def reason(self):
    		pass

        def __str__(self):
        	return '%s (%s)' % (self.dependency.__class__, self.reason())

    def satisfied(self):
        return False

    def build_exception(self):
    	exception = self.Unsatisfied()
        exception.dependency = self
        return exception
            
    def check(self):
        if not self.satisfied():
            exception = self.build_exception()
            raise exception


class PluginDependency (Dependency):
    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
        	return '%s' % self.dependency.plugin_name

    def __init__(self, plugin_name):
    	self.plugin_name = plugin_name

    def satisfied(self):
        pass


class PluginManager:
    """
    Handles plugin loading and unloading
    """

    __classes = {}
    __plugins = {}


    def register_interface(self, iface):
        pass

    def register_implementation(self, impl):
        pass

    def load_all(self):
        path = os.path.split(__file__)[0]
        for item in os.listdir(path):
            if not '.' in item:
                self.load(item)

    def resolve_path(self, name):
        path = os.path.join(os.path.split(__file__)[0], name)
        if os.path.exists(path):
            return path
        return None

    def load_recursive(self, name):
        path = self.resolve_path(name)
        while True:
            try:
                self.load(name, path)
            except PluginDependency.Unsatisfied, e:
                try:
                    self.load_recursive(e.plugin_name)
                except:
                    raise e

    def load(self, name):
        """
        Loads given plugin
        """
        logging.debug('Loading plugin %s' % name)
        try:
            mod = imp.load_source('ajenti.plugins.%s' % name, os.path.join(self.resolve_path(name), '__init__.py'))
            logging.debug('  == %s ' % mod.info.title)
        except Exception, e:
            logging.warn(' *** Plugin not loadable: %s' % e)
            traceback.print_exc()
            raise PluginCrashed(e)

        info = mod.info
        info.module = mod
        info.active = False
        self.__plugins[name] = info

        try:
            for dependency in info.dependencies:
                dependency.check()
            info.active = True
        except PluginDependency:
            raise
        except PluginLoadError, e:
            logging.warn(' *** Plugin crashed: %s' % e)
            info.crash = e


manager = PluginManager()

__all__ = ['manager', 'PluginLoadError', 'PluginCrashed', 'PluginDependency']

