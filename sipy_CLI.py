"""!
SiPy: Statistics in Python (CLI/CUI Version)

Date created: 5th October 2022

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
"""
import os
import sys

from sipy import SiPy_Shell

if __name__ == "__main__":
    shell = SiPy_Shell()
    if len(sys.argv) == 1:
        shell.cmdLoop()
        sys.exit()
    elif (len(sys.argv) == 3) and (sys.argv[1].lower() == "script_execute"):
        scriptfile = os.path.abspath(sys.argv[2])
        shell.runScript(scriptfile, "script_execute")
        sys.exit()
    elif (len(sys.argv) == 3) and (sys.argv[1].lower() == "script_merge"):
        scriptfile = os.path.abspath(sys.argv[2])
        shell.runScript(scriptfile, "script_merge")
        sys.exit()