import logging


class LazyModule():
    def __init__(self, module, obj=None):
        self._module = module
        self._object = obj
        self._loaded = False

    def __load(self):
        logging.debug(f'Lazy-loading module {self._module}')
        target = __import__(self._module, fromlist=[str(self._module)])
        if self._object:
            target = getattr(target, self._object)

        for k in dir(target):
            try:
                self.__dict__[k] = getattr(target, k)
            except AttributeError:
                pass

        self._loaded = True

    def __getattr__(self, attr):
        if not self._loaded:
            self.__load()
        return self.__dict__[attr]
