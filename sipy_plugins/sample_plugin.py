from sipy_plugins.base_plugin import BasePlugin

class SamplePlugin(BasePlugin):
    def __init__(self, name="Sample Plugin", version="1.0", 
                 author="Maurice Ling"):
        super().__init__(name, version, author)
        
    def execute(self, kwargs):
        print("Executing SamplePlugin")
        return(f"Keyword Arguments: {kwargs}")
        
    def purpose(self):
        return """
This is a sample plugin
        """

    def usage(self):
        return self.purpose() + """
Usage: pg sample
        """
