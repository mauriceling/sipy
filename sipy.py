'''!
SiPy: Statistics in Python

Date created: 9th September 2022

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
import os
import subprocess
import sys

import libsipy

try: 
    import fire
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'fire',
                           '--trusted-host', 'pypi.org', 
                           '--trusted-host', 'files.pythonhosted.org'])
    import fire

def arithmeticMean(datalist, module=False):
    """!
    Calculating arithmetic mean of the datalist.

    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: Arithmetic mean.
    """
    results = libsipy.base.arithmeticMean(datalist)
    if module:
       return results
    else:
        print("Arimethic mean = %f" % results)

def availableModules(module=False):
    """!
    List all the available modules (in libsipy).

    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: List of available modules in libsipy.
    """
    ignores = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__']
    results = [m for m in dir(libsipy) if m not in ignores]
    if module: 
        return results
    else:
        print("List of Available Modules:")
        for m in results: print(m)

def template(module=False):
    """!

    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: List of available modules in libsipy.
    """
    
    if module: 
        return results
    else:
        print("xxx")
        for m in results: print(m)

if __name__ == '__main__':
    exposed_functions = {"mean": arithmeticMean,
                         "modules": availableModules}
    fire.Fire(exposed_functions)
