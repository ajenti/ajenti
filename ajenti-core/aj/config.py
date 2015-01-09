class BaseConfig (object):
    def __init__(self):
        self.data = None

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()
