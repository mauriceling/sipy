'''!
Plugin Manager for SiPy

Date created: 15th November 2023

License: GNU General Public License version 3 for academic or 
not-for-profit use only

SiPy package is free software: you can redistribute it and/or 
modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import importlib
import inspect
import os

from sipy_plugins.base_plugin import BasePlugin

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugin(self, plugin_dir, plugin_name):
        if plugin_name in self.plugins:
            print(f"Plugin '{plugin_name}' is already loaded.")
            return
        try:
            plugin_module = importlib.import_module(f'{plugin_dir}.{plugin_name}')
            plugin_class = self.find_plugin_class(plugin_module)
            if plugin_class:
                self.plugins[plugin_name] = plugin_class()
                print(f"Plugin '{plugin_name}' loaded.")
            else:
                print(f"No valid plugin class found in '{plugin_name}'.")
        except (ImportError, Exception) as e:
            print(f"Error loading plugin '{plugin_name}': {e}")

    def find_plugin_class(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                return obj
        return None

    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            print(f"Plugin '{plugin_name}' unloaded.")
        else:
            print(f"Plugin '{plugin_name}' not found.")

    def execute_plugin(self, plugin_name, kwargs):
        plugin = self.plugins.get(plugin_name)
        if plugin:
            plugin.initialize()
            plugin.pre_execute()
            retR = self.execute_safely(plugin_name, plugin, kwargs)
            plugin.post_execute()
            plugin.finalize()
        else:
            print(f"Plugin '{plugin_name}' failed to load or does not exist.")
        return retR

    def execute_safely(self, plugin_name, plugin, kwargs):
        try:
            return plugin.execute(kwargs)
        except Exception as e:
            print(f"Error executing plugin '{plugin_name}': {e}")

    def load_plugins_from_directory(self, plugin_dir):
        if not os.path.isdir(plugin_dir):
            print(f"Error: '{plugin_dir}' is not a valid directory.")
            return
        plugin_files = [file[:-3] for file in os.listdir(plugin_dir) if file.endswith('.py') and file != '__init__.py']
        for plugin_name in plugin_files:
            self.load_plugin(plugin_dir, plugin_name)

    def get_purpose(self, plugin_name):
        plugin = self.plugins.get(plugin_name)
        return plugin.purpose()

    def get_usage(self, plugin_name):
        plugin = self.plugins.get(plugin_name)
        return plugin.usage()
