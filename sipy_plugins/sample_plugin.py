from sipy_plugins.base_plugin import BasePlugin

class SamplePlugin(BasePlugin):
    def execute(self, kwargs):
        print("Executing SamplePlugin")
        print(f"Keyword Arguments: {kwargs}")
