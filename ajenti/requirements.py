from ajenti.utils import shell_status

class BaseRequirement(Exception):
    pass
    
class BackendRequirement(BaseRequirement):
    def __init__(self, app, interface):
        self.app = app
        self.interface = interface
                      
    def test(self):
        self.app.get_backend(self.interface).test()
                  
    def __str__(self):
        return 'Backend required: ' + str(self.interface)

                          
class SoftwareRequirement(BaseRequirement):
    def __init__(self, app, name, binary):
        self.app = app
        self.name = name
        self.bin = binary
        
    def test(self):
        if shell_status('which ' + self.bin) != 0:
            raise self
            
    def __str__(self):
        return 'Binary required: ' + self.bin
            