from ajenti.apis import API
from ajenti.com import Interface


class LoadCores(API):
    class ILoadCores(Interface):
        def get_loadcores(self):
            pass
			