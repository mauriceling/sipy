from sipy_pm import PluginManager

def main():
    manager = PluginManager()
    plugin_directory = "sipy_plugins"  # Directory where plugins are stored

    manager.load_plugin(plugin_directory, "sample_plugin")
    manager.execute_plugin("sample_plugin", 1, 2, 3, operation="print", name="Alice", age=30)
    manager.unload_plugin("sample_plugin")  # Unload the plugin

if __name__ == "__main__":
    main()

