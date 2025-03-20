'''!
SiPy Plugin: Plugin to Grab an Inspirational Quote from https://zenquotes.io/api/random

Date created: 20th March 2025

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
from sipy_plugins.base_plugin import BasePlugin
import requests

class QuotePlugin(BasePlugin):
    def __init__(self, name="Quote Plugin", version="1.0", author="Maurice Ling"):
        super().__init__(name, version, author)

    def execute(self, kwargs):
        response = requests.get('https://zenquotes.io/api/random')
            
        if response.status_code == 200:
            quote_data = response.json()[0]
            content = quote_data.get('q', 'No content found')
            author = quote_data.get('a', 'Unknown')
            return f"""{content} \n -- {author}"""
        else:
            return f"""Failed to fetch quote. Status code: {response.status_code}"""

    def purpose(self):
        return """
This plugin grabs a random inspirational quote from https://zenquotes.io/api/random
        """

    def usage(self):
        return self.purpose() + """
Usage: pg quote
        """