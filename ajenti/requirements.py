from ajenti.utils import shell_status


class BaseRequirement(Exception):
    pass
    

                          
class PluginRequirement(BaseRequirement):
    def __init__(self, name):
        self.name = name
        
    def test(self, plugins):
        if not self.name in plugins:
            raise self
            
    def __str__(self):
        return 'Plugin required: ' + self.name
            
            
class SoftwareRequirement(BaseRequirement):
    def __init__(self, binary):
        self.bin = binary
        
    def test(self, plugins):
        if shell_status('which ' + self.bin) != 0:
            raise self
            
    def __str__(self):
        return 'Binary required: ' + self.bin
                        
