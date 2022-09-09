'''!
libsipy (Base): Base Collection of Functions for SiPy

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
from scipy import stats

def arithmeticMean(values=(1,2,3,4,5)):
    """!
    Calculating arithmetic mean of the values.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Arithmetic mean.
    """
    result = stats.describe(values)
    return result.mean

def kurtosisNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Kurtosis Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Kurtosis-test

    Reference: Anscombe FJ, Glynn WJ. 1983. Distribution of the kurtosis statistic b2 for normal samples. Biometrika 70, 227-234.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.kurtosistest(values)
    return (result[0], result[1])
