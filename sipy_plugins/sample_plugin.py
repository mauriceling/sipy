from sipy_plugins.base_plugin import BasePlugin

class SamplePlugin(BasePlugin):
    def execute(self, *args, **kwargs):
        print("Executing SamplePlugin")
        print(f"Arguments: {args}")
        print(f"Keyword Arguments: {kwargs}")
