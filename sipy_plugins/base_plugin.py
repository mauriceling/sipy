'''!
SiPy Plugin: Base Plugin

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

class BasePlugin:
    """
    Base class for creating plugins.
    """
    def __init__(self, name="Generic Plugin", version="1.0", author="Anonymous"):
        """
        Initialize BasePlugin.

        Args:
            name (str): Name of the plugin.
            version (str): Version number of the plugin.
            author (str): Author of the plugin.
        """
        self.name = name
        self.version = version
        self.author = author
        self.is_initialized = False

    def initialize(self):
        """
        Initialize the plugin.
        """
        if not self.is_initialized:
            self.setup()
            self.is_initialized = True

    def setup(self):
        """
        Perform setup tasks for the plugin.
        """
        pass

    def pre_execute(self):
        """
        Tasks to be done before executing the plugin.
        """
        pass

    def execute(self, kwargs):
        """
        Execute the plugin logic.

        Args:
            kwargs: Arbitrary keyword arguments.
        """
        return "Plugin execute method not implemented"

    def post_execute(self):
        """
        Tasks to be done after executing the plugin.
        """
        pass

    def finalize(self):
        """
        Finalize the plugin.
        """
        if self.is_initialized:
            self.cleanup()
            self.is_initialized = False

    def cleanup(self):
        """
        Perform cleanup tasks for the plugin.
        """
        pass

    def purpose(self):
        return """
        """
        
    def usage(self):
        return """
        """
