from jadi import interface

@interface
class Widget():
    """
    Base interface for dashboard widgets.
    """
    id = None

    name = None
    """Display name"""


    def __init__(self, context):
        self.context = context

    def get_value(self, config):
        """
        Override this to return the widget value for the given config dict.
        """
        raise NotImplementedError
