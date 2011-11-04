from ajenti.com import Interface, implements
from ajenti.api import *
from ajenti.apis import API
from ajenti import apis

import traceback


class ConfManager (Component):
    """
    A :class:`Component`, proxyfies access to system's config files.
    Use this when possible instead of ``open``. You'll have to create an
    :class:`IConfigurable` first, then use ``load``, ``save``, and ``commit``
    functions.
    """
    name = 'confmanager'

    configurables = {}
    hooks = []

    def load(self, id, path):
        """
        Reads a config file.

        :param  id:     :class:`IConfigurable` ID.
        :type   id:     str
        :param  path:   file location
        :type   path:   str
        :rtype:         str
        :returns:       file contents
        """
        cfg = self.get_configurable(id)
        for c in self.hooks:
            c.pre_load(cfg, path)

        data = open(path, 'r').read()

        for c in self.hooks:
            data = c.post_load(cfg, path, data)

        return data

    def save(self, id, path, data):
        """
        Writes a config file.

        :param  id:     :class:`IConfigurable` ID.
        :type   id:     str
        :param  path:   file location
        :type   path:   str
        :param  data:   file contents
        :type   data:   str
        """
        cfg = self.get_configurable(id)

        for c in self.hooks:
            data = c.pre_save(cfg, path, data)
            if data is None:
                return

        open(path, 'w').write(data)

        for c in self.hooks:
            c.post_save(cfg, path)

        return data

    def commit(self, id):
        """
        Notifies ConfManager that you have finished writing Configurable's files.
        For example, at this point Recovery plugin will make a backup.

        :param  id:     :class:`IConfigurable` ID.
        :type   id:     str
        """
        cfg = self.get_configurable(id)
        for c in self.hooks:
            c.finished(cfg)

    def get_configurable(self, id):
        """
        Finds a Configurable.

        :param  id:     :class:`IConfigurable` ID.
        :type   id:     str
        :rtype:         :class:`IConfigurable`
        """
        for c in self.configurables.values():
            if c.id == id:
                return c

    def rescan(self):
        """
        Registers any newly found Configurables
        """
        self.configurables = {}
        self.hooks = []
        try:
            for cfg in self.app.grab_plugins(IConfigurable):
                self.log.debug('Registered configurable: ' + cfg.id + ' ' + str(cfg))
                self.configurables[cfg.id] = cfg
        except Exception, e:
            self.app.log.error('Configurables loading failed: ' + str(e) + traceback.format_exc())
        for h in self.app.grab_plugins(IConfMgrHook):
            self.app.log.debug('Registered configuration hook: ' + str(h))
            self.hooks.append(h)

    def on_starting(self):
        self.rescan()

    def on_stopping(self):
        pass

    def on_stopped(self):
        pass


class IConfMgrHook (Interface):
    """
    Base interface for ConfManager hooks that react to events and process
    the config files.
    """
    def pre_load(self, cfg, path):
        """
        Called before reading a file.

        :param  cfg:    Configurable
        :type   cfg:    :class:`IConfigurable`
        :param  path:   file location
        :type   path:   str
        """

    def post_load(self, cfg, path, data):
        """
        Called after reading a file. Implementation has to process the file and
        return new content

        :param  cfg:    Configurable
        :type   cfg:    :class:`IConfigurable`
        :param  path:   file location
        :type   path:   str
        :param  data:   file contents
        :type   data:   str
        :rtype:         str
        :returns:       modified contents
        """

    def pre_save(self, cfg, path, data):
        """
        Called before saving a file. Implementation has to process the file and
        return new content.

        :param  cfg:    Configurable
        :type   cfg:    :class:`IConfigurable`
        :param  path:   file location
        :type   path:   str
        :param  data:   file contents
        :type   data:   str
        :rtype:         str
        :returns:       modified contents
        """

    def post_save(self, cfg, path):
        """
        Called after saving a file.

        :param  cfg:    Configurable
        :type   cfg:    :class:`IConfigurable`
        :param  path:   file location
        :type   path:   str
        """

    def finished(self, cfg):
        """
        Called when a ``commit`` is performed. Good time to make backups/save data/etc.

        :param  cfg:    Configurable
        :type   cfg:    :class:`IConfigurable`
        """


class ConfMgrHook (Plugin):
    """
    Handy base class in case you don't want to reimplement all hook methods.
    """
    implements(IConfMgrHook)
    abstract = True

    def pre_load(self, cfg, path):
        pass

    def post_load(self, cfg, path, data):
        return data

    def pre_save(self, cfg, path, data):
        return data

    def post_save(self, cfg, path):
        pass

    def finished(self, cfg):
        pass


class IConfigurable (Interface):
    """
    Interface for Configurables. Configurable is an entity (software or
    system aspect) which has a set of config files.

    - ``name`` - `str`, a human-readable name.
    - ``id`` - `str`, unique ID.
    """
    name = None
    id = None

    def list_files(self):
        """
        Implementation should return list of config file paths - file names or
        wildcards (globs) which will be expanded by :func:`glob.glob`.
        """
