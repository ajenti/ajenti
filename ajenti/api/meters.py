from ajenti.com import *

class IMeter (Interface):
    pass


class BaseMeter (Plugin):
    implements(IMeter)
    abstract = True
    multi_instance = True

    name = 'Unknown'
    text = ''
    category = ''
    rangeable = True
    type = None
    transform = None

    def prepare(self, variant=None):
        self = self.__class__(self.app)
        self.variant = variant
        self.init()
        return self

    def init(self):
        pass

    def get_variants(self):
        return ['None']

    def format_value(self):
        return None


class BinaryMeter (BaseMeter):
    abstract = True
    type = 'binary'

    def get_value(self):
        return 0

    def format_value(self):
        BaseMeter.format_value(self)
        return { 'value': self.get_value() }


class DecimalMeter (BaseMeter):
    abstract = True
    type = 'decimal'

    def get_value(self):
        return 0

    def format_value(self):
        BaseMeter.format_value(self)
        return { 'value': self.get_value() }


class LinearMeter (BaseMeter):
    abstract = True
    type = 'linear'

    def get_value(self):
        return 0

    def get_max(self):
        return 0

    def get_min(self):
        return 0

    def format_value(self):
        BaseMeter.format_value(self)
        return {
            'value': self.get_value(),
            'max': self.get_max(),
            'min': self.get_min(),
        }
