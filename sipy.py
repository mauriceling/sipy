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
import warnings
warnings.filterwarnings("ignore")

import libsipy

try: 
    import fire
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'fire',
                           '--trusted-host', 'pypi.org', 
                           '--trusted-host', 'files.pythonhosted.org'])
    import fire

def arithmeticMean(values=(1,2,3,4,5), module=False):
    """!
    Calculating arithmetic mean of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Arithmetic-mean

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: Arithmetic mean.
    """
    result = libsipy.base.arithmeticMean(values)
    if module:
       return result
    else:
        print("Arimethic mean = %f" % result)

def kurtosisNormalityTest(values=(1,2,3,4,5), module=False):
    """!
    Normality test - Kurtosis Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Kurtosis-test

    Reference: Anscombe FJ, Glynn WJ. 1983. Distribution of the kurtosis statistic b2 for normal samples. Biometrika 70, 227-234.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: (Z-score, p-value).
    """
    result = libsipy.base.kurtosisNormalityTest(values)
    if module:
       return result
    else:
        print("Z-score = %f" % result[0])
        print("p-value = %f" % result[1])

def availableModules(module=False):
    """!
    List all the available modules (in libsipy).

    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: List of available modules in libsipy.
    """
    ignores = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__']
    result = [m for m in dir(libsipy) if m not in ignores]
    if module: 
        return result
    else:
        print("List of Available Modules:")
        for m in result: print(m)

def template(module=False):
    """!

    @param module Boolean: Flag to whether this function will be used as a module. If True, this function will return values to the calling function. Default = False
    @return: List of available modules in libsipy.
    """
    
    if module: 
        return result
    else:
        print("xxx")
        for m in result: print(m)

if __name__ == '__main__':
    exposed_functions = {"kurtosistest": kurtosisNormalityTest,
                         "mean": arithmeticMean,
                         "modules": availableModules}
    fire.Fire(exposed_functions)
