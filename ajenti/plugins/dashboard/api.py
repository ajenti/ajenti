from ajenti.com import Interface


class IDashboardWidget(Interface):
    title = ''
    
    def get_ui(self):
        pass
