from ajenti.com import *

class IMeter (Interface):
    pass


class BaseMeter (Plugin):
    """
    Meters are determinable values (int, float, bool) representing system status
    (sysload, memory usage, service status, etc.) which are used and exported
    over HTTP by ``health`` builtin plugin.

    - ``name`` - `str`, meter name
    - ``text`` - `str`, text shown on the specific meter widget
    - ``category`` - `str`, meter category name
    - ``type`` - `str`, one of 'binary', 'linear', 'decimal'
    - ``transform`` - `str`, value->text transform applied to meter. One of
      'float', 'fsize', 'percent', 'fsize_percent', 'yesno', 'onoff', 'running'
    """
    implements(IMeter)
    abstract = True
    multi_instance = True

    name = 'Unknown'
    text = ''
    category = ''
    type = None
    transform = None

    def prepare(self, variant=None):
        self = self.__class__(self.app)
        self.variant = variant
        self.init()
        return self

    def init(self):
        """
        Implementation may perform preparations based on ``self.variant`` here.
        """

    def get_variants(self):
        """
        Implementation should return list of meter 'variants' here.
        """
        return ['None']

    def format_value(self):
        return None


class BinaryMeter (BaseMeter):
    """
    Base class for binary value meters
    """
    abstract = True
    type = 'binary'

    def get_value(self):
        """
        Implementation should return binary meter value
        """

    def format_value(self):
        BaseMeter.format_value(self)
        return { 'value': self.get_value() }


class DecimalMeter (BaseMeter):
    """
    Base class for decimal/float value meters
    """
    abstract = True
    type = 'decimal'

    def get_value(self):
        """
        Implementation should return decimal meter value
        """

    def format_value(self):
        BaseMeter.format_value(self)
        return { 'value': self.get_value() }


class LinearMeter (BaseMeter):
    """
    Base class for decimal/float value meters with min/max range
    """
    abstract = True
    type = 'linear'

    def get_value(self):
        """
        Implementation should return decimal meter value
        """
        return 0

    def get_max(self):
        """
        Implementation should return decimal meter range maximum
        """
        return 0

    def get_min(self):
        """
        Implementation should return decimal meter range minimum
        """
        return 0

    def format_value(self):
        BaseMeter.format_value(self)
        return {
            'value': self.get_value(),
            'max': self.get_max(),
            'min': self.get_min(),
        }
