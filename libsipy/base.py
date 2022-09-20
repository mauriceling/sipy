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
import pingouin
from scipy import stats

def arithmeticMean(values=(1,2,3,4,5)):
    """!
    Calculating arithmetic mean of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Arithmetic-mean

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Arithmetic mean.
    """
    result = stats.describe(values)
    return result.mean
def geometricMean(values=(1,2,3,4,5)):
    """!
    Calculating geometric mean of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Geometric-mean

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Geometric mean.
    """
    result = stats.gmean(values)
    return result

def harmonicMean(values=(1,2,3,4,5)):
    """!
    Calculating harmonic mean of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Harmonic-mean

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Harmonic mean.
    """
    result = stats.hmean(values)
    return result

def kurtosis(values=(1,2,3,4,5)):
    """!
    Calculating kurtosis of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Kurtosis

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Kurtosis.
    """
    result = stats.describe(values)
    return result.kurtosis

def skew(values=(1,2,3,4,5)):
    """!
    Calculating skew of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Skew

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Skew.
    """
    result = stats.describe(values)
    return result.skewness

def standardDeviation(values=(1,2,3,4,5)):
    """!
    Calculating standard deviation of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Sample-standard-deviation

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Standard deviation.
    """
    result = stats.tstd(values)
    return result

def standardError(values=(1,2,3,4,5)):
    """!
    Calculating standard deviation of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Sample-standard-error

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Standard error.
    """
    result = stats.tsem(values)
    return result

def variance(values=(1,2,3,4,5)):
    """!
    Calculating variance of the values.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Sample-variance

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: Variance.
    """
    result = stats.describe(values)
    return result.variance

def jarqueBeraNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Jarque Bera Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Jarque-Bera-test
    
    Reference: Jarque CM, Bera, AK. 1980. Efficient tests for normality, homoscedasticity and serial independence of regression residuals. Econometric Letters 6(3), 255-259.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.jarque_bera(values)
    return (result[0], result[1])

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

def shapiroWilkNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Shapiro Wilk Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Shapiro-Wilk-test-for-normality

    Reference: Shapiro SS, Wilk MB. 1965. An analysis of variance test for normality (complete samples). Biometrika 52, 591-611.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.shapiro(values)
    return (result[0], result[1])

def skewNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Skew Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Skew-test

    Reference: D’Agostino RB, A. J. Belanger AJ, D’Agostino Jr. RB. 1990. A suggestion for using powerful and informative tests of normality. American Statistician 44, 316-321.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.skewtest(values)
    return (result[0], result[1])

def regressionLinear(X, y, add_intercept=True):
    """!
    Performs simple / multiple linear regression as y = b1X1 + ... + bnXn + c
    """
    result = pingouin.linear_regression(X, y, add_intercept=add_intercept)
    return result

def regressionLogistic(X, y):
    """!
    Performs logistic regression
    """
    result = pingouin.logistic_regression(X, y)
    return result

def tTest1Sample(values=(1,2,3,4,5), mu=0):
    """!
    T-Test - 1-Sample
    """
    mu = float(mu)
    result = pingouin.ttest(values, mu)
    return result

def tTest2SampleEqual(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    T-test - 2-Sample, Independent-Samples, Equal-Variance; where the null hypothesis: Mean of Population A = Mean of Population B
    
    Web References: https://github.com/mauriceling/mauriceling.github.io/wiki/t-test---2-samples-%28independent-samples%29-assuming-equal-variance
    
    References: https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm
                Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
                Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
                Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """ 
    result = pingouin.ttest(x, y, paired = False, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result

def tTest2SampleUnequal(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    T-test - 2-Sample, Independent-Samples, Unequal-Variance; where the null hypothesis: Mean of Population A = Mean of Population B
    
    Web References: https://github.com/mauriceling/mauriceling.github.io/wiki/t-test---2-samples-%28independent-samples%29-assuming-unequal-variance
    
    References: https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm
                Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
                Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
                Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """
    result = pingouin.ttest(x, y, paired = False, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result

def tTest2SamplePaired(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    T-test - 2-Sample, Paired-Samples; where the null hypothesis: Mean of difference between Population A & Population B is 0
    
    Web References: https://github.com/mauriceling/mauriceling.github.io/wiki/t-test---paired-%28dependent-samples%29
    
    References: https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm
                Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
                Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
                Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """
    result = pingouin.ttest(x, y, paired = True, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result

def anova1way(values = (1,2,3,4,5)):
    """!
    ANOVA - 1-way, where the null hypothesis: all population means are equal
    
    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/ANOVA---One-way
    
    Note: One-way ANOVA assumes variances of all samples to be equal. If variances cannot be assumed to be equal, Alexander Govern test can be used.
    """
    result = stats.f_oneway(*values)
    return result