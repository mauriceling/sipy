"""!
Data Wrangler for SiPy

Date created: 9th September 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only.

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
import pandas

try: 
    import fire
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'fire',
                           '--trusted-host', 'pypi.org', 
                           '--trusted-host', 'files.pythonhosted.org'])
    import fire

if __name__ == '__main__':
    exposed_functions = {}
    fire.Fire(exposed_functions)
