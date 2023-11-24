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
import fitter
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
    
    Reference: 
        - Jarque CM, Bera, AK. 1980. Efficient tests for normality, homoscedasticity and serial independence of regression residuals. Econometric Letters 6(3), 255-259.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.jarque_bera(values)
    return (result[0], result[1])

def kurtosisNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Kurtosis Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Kurtosis-test

    Reference: 
        - Anscombe FJ, Glynn WJ. 1983. Distribution of the kurtosis statistic b2 for normal samples. Biometrika 70, 227-234.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.kurtosistest(values)
    return (result[0], result[1])

def shapiroWilkNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Shapiro Wilk Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Shapiro-Wilk-test-for-normality

    Reference: 
        - Shapiro SS, Wilk MB. 1965. An analysis of variance test for normality (complete samples). Biometrika 52, 591-611.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.shapiro(values)
    return (result[0], result[1])

def skewNormalityTest(values=(1,2,3,4,5)):
    """!
    Normality test - Skew Test; where the null hypothesis = the values are normally distributed.

    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/Skew-test

    Reference: 
        - D’Agostino RB, A. J. Belanger AJ, D’Agostino Jr. RB. 1990. A suggestion for using powerful and informative tests of normality. American Statistician 44, 316-321.

    @param values tuple: A tuple of numeric values to calculate. Default = (1,2,3,4,5)
    @return: (Z-score, p-value).
    """
    result = stats.skewtest(values)
    return (result[0], result[1])

def regressionLinear(X, y, add_intercept=True):
    result = pingouin.linear_regression(X, y, add_intercept=add_intercept)
    return result

def regressionLogistic(X, y):
    result = pingouin.logistic_regression(X, y)
    return result

def wilcoxon(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Wilcoxon Signed-Rank Test

    Web reference: https://pingouin-stats.org/build/html/generated/pingouin.wilcoxon.html

    References:
        - Wilcoxon, F. (1945). Individual comparisons by ranking methods. Biometrics bulletin, 1(6), 80-83.
    """
    result = pingouin.wilcoxon(x, y, alternative = "two-sided")
    return result

def mannWhitneyU(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Mann-Whitney U Test

    Web reference: https://pingouin-stats.org/build/html/generated/pingouin.mwu.html

    References:
        - Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. The annals of mathematical statistics, 50-60.
    """
    result = pingouin.mwu(x, y, alternative = "two-sided")
    return result

def compute_effsize_none(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
     no effect size
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='none')
    return result    

def compute_effsize_cohen(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Unbiased Cohen d
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='cohen')
    return result    


def compute_effsize_hedges(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Hedges g
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='hedges')
    return result    

def compute_effsize_r(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Pearson correlation coefficient
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='r')
    return result    
  

def compute_effsize_pointbiserialr(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Point-biserial correlation
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='pointbiserialr')
    return result    

def compute_effsize_etasquare(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Eta-square
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='eta-square')
    return result    

def compute_effsize_oddsratio(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Odds ratio
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='odds-ratio')
    return result    

def compute_effsize_AUC(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Area under the curve 
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='AUC')
    return result    

def compute_effsize_CLES(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Common Language Effect Size 
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.compute_effsize.html
    
    References: 
        - Lakens, D., 2013. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Front. Psychol. 4, 863. https://doi.org/10.3389/fpsyg.2013.00863
        - Cumming, Geoff. Understanding the new statistics: Effect sizes, confidence intervals, and meta-analysis. Routledge, 2013.
    """ 
    result = pingouin.compute_effsize(x, y, paired=False, eftype='CLES')
    return result    

def correlatePearson(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Pearson product-moment correlation
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='pearson')
    return result    

def correlateSpearman(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Spearman rank-order correlation
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='spearman')
    return result    

def correlateKendall(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Kendall’s correlation (for ordinal data)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='kendall')
    return result    

def correlateBicor(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Biweight midcorrelation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='bicor')
    return result    

def correlatePercbend (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Percentage bend correlation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='percbend')
    return result    

def correlateShepherd (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Shepherd's pi correlation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='shepherd')
    return result    

def correlateSkipped (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Skipped correlation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.corr(x, y, alternative='two-sided', method='skipped')
    return result    

def correlateDistance (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Distance correlation between two arrays 
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.distance_corr.html
    
    References: 
        - Székely, G. J., Rizzo, M. L., & Bakirov, N. K. (2007). Measuring and testing dependence by correlation of distances. The annals of statistics, 35(6), 2769-2794.
        - https://gist.github.com/satra/aa3d19a12b74e9ab7941
        - https://gist.github.com/wladston/c931b1495184fbb99bec
        - https://en.wikipedia.org/wiki/Distance_correlation

    """ 
    result = pingouin.corr(x, y, alternative='greater', n_boot=1000, seed=None)
    return result    

def correlate2cv (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Skipped correlation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.circ_corrcc(x, y, correction_uniform=False)
    return result    

def correlate1cv (x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    Skipped correlation (robust)
    
    Web References: https://pingouin-stats.org/build/html/generated/pingouin.corr.html
    
    References: 
        - Wilcox, R.R., 1994. The percentage bend correlation coefficient. Psychometrika 59, 601–616. https://doi.org/10.1007/BF02294395
        - Schwarzkopf, D.S., De Haas, B., Rees, G., 2012. Better ways to improve standards in brain-behavior correlation analysis. Front. Hum. Neurosci. 6, 200. https://doi.org/10.3389/fnhum.2012.00200
        - Rousselet, G.A., Pernet, C.R., 2012. Improving standards in brain-behavior correlation analyses. Front. Hum. Neurosci. 6, 119. https://doi.org/10.3389/fnhum.2012.00119
        - Pernet, C.R., Wilcox, R., Rousselet, G.A., 2012. Robust correlation analyses: false positive and power validation using a new open source matlab toolbox. Front. Psychol. 3, 606. https://doi.org/10.3389/fpsyg.2012.00606
    """ 
    result = pingouin.circ_corrcl(x, y)
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
    
    References: 
        - Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
        - Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
        - Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """ 
    result = pingouin.ttest(x, y, paired = False, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result

def tTest2SampleUnequal(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    T-test - 2-Sample, Independent-Samples, Unequal-Variance; where the null hypothesis: Mean of Population A = Mean of Population B
    
    Web References: https://github.com/mauriceling/mauriceling.github.io/wiki/t-test---2-samples-%28independent-samples%29-assuming-unequal-variance
    
    References: 
        - Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
        - Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
        - Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """
    result = pingouin.ttest(x, y, paired = False, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result

def tTest2SamplePaired(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    T-test - 2-Sample, Paired-Samples; where the null hypothesis: Mean of difference between Population A & Population B is 0
    
    Web References: https://github.com/mauriceling/mauriceling.github.io/wiki/t-test---paired-%28dependent-samples%29
    
    References: 
        - Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch’s t-test instead of Student’s t-test. International Review of Social Psychology, 30(1).
        - Zimmerman, D. W. (2004). A note on preliminary tests of equality of variances. British Journal of Mathematical and Statistical Psychology, 57(1), 173-181.
        - Rouder, J.N., Speckman, P.L., Sun, D., Morey, R.D., Iverson, G., 2009. Bayesian t tests for accepting and rejecting the null hypothesis. Psychon. Bull. Rev. 16, 225–237. https://doi.org/10.3758/PBR.16.2.225
    """
    result = pingouin.ttest(x, y, paired = True, alternative = "two-sided" , correction = "auto" , r = 0.707, confidence = 0.95)
    return result


def TOST(x=(1,2,3,4,5), y=(1,2,3,4,5)):
    """
    two One-Sided Test (TOST) for equivalence

    Web References: https://pingouin-stats.org/build/html/generated/pingouin.tost.html
    
    References: 
       - Schuirmann, D.L. 1981. On hypothesis testing to determine if the mean of a normal distribution is contained in a known interval. Biometrics 37 617.
    """
    result = pingouin.tost(x, y, bound=1, paired = False, correction =False)
    return result

def anova1way(values = (1,2,3,4,5)):
    """!
    ANOVA - 1-way, where the null hypothesis: all population means are equal
    
    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/ANOVA---One-way
    
    Note: One-way ANOVA assumes variances of all samples to be equal. If variances cannot be assumed to be equal, Alexander Govern test can be used.
    """
    result = stats.f_oneway(*values)
    return result

def anovaRM_wide(data):
    result = pingouin.rm_anova(data)
    return result
    
def anovakruskal(values = (1,2,3,4,5)):
    """!
    ANOVA - 1-way, where the null hypothesis: all population means are equal
    
    Web reference: https://github.com/mauriceling/mauriceling.github.io/wiki/ANOVA---One-way
    
    Note: One-way ANOVA assumes variances of all samples to be equal. If variances cannot be assumed to be equal, Alexander Govern test can be used.
    """
    result = pingouin.kruskal(data=None, dv=None, between=None, detailed=False)
    return result

def BartlettTest(values = (1,2,3,4,5)):
    """!
    Barlett's Test - Equal Variance, where the Null hypothesis: Variances of all samples are equal
    
    Web references: https://github.com/mauriceling/mauriceling.github.io/wiki/Bartlett%27s-test
    
    Reference: 
        - Bartlett MS. 1937. Properties of Sufficiency and Statistical Tests. Proceedings of the Royal Society of London. Series A, Mathematical and Physical Sciences 160(901), 268-282.
    """
    result = stats.bartlett(*values)
    return result

def FlignerTest(values = (1,2,3,4,5)):
    """!
    Fligner-Killeen Test - Equal Variance, where the null hypothesis: Variance of all samples are equal
    
    Web references: https://github.com/mauriceling/mauriceling.github.io/wiki/Fligner-Killeen-test
    
    Reference: 
        - Fligner MA, Killeen TJ. 1976. Distribution-free two-sample tests for scale. Journal of the American Statistical Association 71(353), 210-213.
    
    Note: Fligner-Killeen's test caters to non-normal samples.
    """
    result = stats.fligner(*values)
    return result   

def LeveneTest(values = (1,2,3,4,5)):
    """!
    Levene's Test - Equal Variance, where the null hypothesis: Variance of all samples are equal
    
    Web references: https://github.com/mauriceling/mauriceling.github.io/wiki/Levene%27s-test
    
    Reference: 
        - Levene H. 1960. Robust tests for equality of variances. In Olkin I, Hotelling H, et al. (eds.). Contributions to Probability and Statistics: Essays in Honor of Harold Hotelling. Stanford University Press. pp. 278–292.
        - Brown MB, Forsythe AB. 1974. Robust tests for the equality of variances. Journal of the American Statistical Association 69, 364–367.
    
    Note: Levene's test caters to non-normal samples.
          If the parameter center is changed to median or trimmed (for trimmed mean), Levene's test becomes Brown-Forsythe test.
    """
    result = stats.levene(*values, center = "mean")
    return result

def DistributionFit(values=(1,2,3,4,5), distributions="all"):
    """!
    Use fitter (https://github.com/cokelaer/fitter) to fit values to various distributions.
    """
    if distributions="all":
        f = fitter.Fitter(values)
    else:
        f = fitter.Fitter(values, distributions=distributions)
    f.fit()
    return f