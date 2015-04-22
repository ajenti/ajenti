from jadi import interface


@interface
class Widget(object):
    """
    Base interface for dashboard widgets.
    """
    id = None

    name = None
    """Display name"""

    template = None
    """Angular view template URL"""

    config_template = None
    """Configuration dialog template URL"""

    def __init__(self, context):
        self.context = context

    def get_value(self, config):
        """
        Override this to return the widget value for the given config dict.
        """
        raise NotImplementedError
