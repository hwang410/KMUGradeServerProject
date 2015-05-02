

# Put in const.py...
class Const:
    class ConstError(TypeError): pass
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "You can't change the value"
        
        self.__dict__[name] = value
    
import sys
sys.modules[__name__] = Const()