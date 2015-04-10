import augeas

from aj.api import interface


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
    def __init__(self, modules=[]):
        augeas.Augeas.__init__(self, flags=augeas.Augeas.NO_MODL_AUTOLOAD | augeas.Augeas.NO_LOAD)
        for module in modules:
            path = '/augeas/load/%s' % module['name']
            self.set(path + '/lens', module['lens'])
            for index, incl in enumerate(module['incl']):
                self.set(path + '/incl[%i]' % (index + 1), incl)

    def enc(self, v):
        if v:
            return v.encode('utf8')

    def match(self, path):
        return augeas.Augeas.match(self, self.enc(path))

    def set(self, path, value):
        augeas.Augeas.set(self, self.enc(path), self.enc(value))

    def setd(self, path, value, default=None):
        self.set(path, value)
        if value == default:
            self.remove(path)

    def raise_error(self):
        raise AugeasError(self)

    def save(self):
        try:
            augeas.Augeas.save(self)
        except IOError:
            self.raise_error()

    def dump(self, path):
        for sp in self.match(path + '/*'):
            print sp, '=', self.get(sp)


@interface
class AugeasEndpoint(object):
    id = None

    def __init__(self, context):
        self.context = context

    def get_augeas(self):
        raise NotImplementedError

    def get_root_path(self):
        raise NotImplementedError
