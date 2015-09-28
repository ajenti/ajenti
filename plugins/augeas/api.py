import augeas
from jadi import interface


class AugeasError(Exception):
    def __init__(self, aug):
        self.message = None
        self.data = {}
        aug.dump('/')
        for ep in aug.match('/augeas//error'):
            self.message = aug.get(ep + '/message')
            for p in aug.match(ep + '/*'):
                self.data[p.split('/')[-1]] = aug.get(p)

    def __str__(self):
        return self.message


class Augeas(augeas.Augeas):
    """
    A smarter and faster wrapper around :class:`augeas.Augeas`.augeas

    For faster startup, no modules and lenses are preloaded::

        aug = Augeas(modules=[{
            'name': 'Interfaces',  # module name
            'lens': 'Interfaces.lns',  # lens name
            'incl': [  # included files list
                self.path,
                self.path + '.d/*',
            ]
        }])

    Don't forget to call :func:`.load()` afterwards.
    """

    def __init__(self, modules=[], loadpath=None):
        augeas.Augeas.__init__(self, loadpath=loadpath, flags=augeas.Augeas.NO_MODL_AUTOLOAD | augeas.Augeas.NO_LOAD)
        for module in modules:
            path = '/augeas/load/%s' % module['name']
            self.set(path + '/lens', module['lens'])
            for index, incl in enumerate(module['incl']):
                self.set(path + '/incl[%i]' % (index + 1), incl)

    def __enc(self, v):
        if v:
            return v.encode('utf8')

    def match(self, path):
        return augeas.Augeas.match(self, self.__enc(path))

    def get(self, path):
        return augeas.Augeas.get(self, self.__enc(path))

    def set(self, path, value):
        augeas.Augeas.set(self, self.__enc(path), self.__enc(value))

    def setd(self, path, value, default=None):
        """
        Sets `path` to `value`, or removes `path` if `value == default`
        """
        if value is not None:
            self.set(path, value)
        if value == default:
            self.remove(path)

    def raise_error(self):
        """
        Extracts error information from Augeas tree and raises :exc:`AugeasError`
        """
        raise AugeasError(self)

    def save(self):
        try:
            augeas.Augeas.save(self)
        except IOError:
            self.raise_error()

    def dump(self, path):
        """
        Dumps contents under `path` to stdout.
        """
        for sp in self.match(path + '/*'):
            print(sp, '=', self.get(sp))


@interface
class AugeasEndpoint(object):
    """
    Implement this to provide Augeas trees to the frontend.
    """

    id = None

    def __init__(self, context):
        self.context = context

    def get_augeas(self):
        """
        Should return a ready-to-use :class:`Augeas`
        """
        raise NotImplementedError

    def get_root_path(self):
        """
        Should return an Augeas path of the root node to be provided to the frontend.
        """
        raise NotImplementedError
