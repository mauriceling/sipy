'''!
SiPy Plugin: Plugin for Pingouin (https://pingouin-stats.org) Functions

Date created: 19th March 2025

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
import pingouin as pg

class PingouinPlugin(BasePlugin):
    def __init__(self, name="Pingouin Plugin", version="1.0", author="Maurice Ling"):
        super().__init__(name, version, author)

    def execute(self, kwargs):
        if "test" not in kwargs: 
            return "test type must be given"
        else:
            test = kwargs["test"]
        if test.lower() == 'anova': return self.power_anova(kwargs)
        elif test.lower() == 'rm_anova': return self.power_rm_anova(kwargs)
        elif test.lower() in ['chi2', 'chisq', 'chi-sq']: return self.power_chi2(kwargs)
        elif test.lower() in ['corr', 'correlation', 'pearson', 'r']: return self.power_corr(kwargs)
        elif test.lower() == 'ttest': return self.power_ttest(kwargs)
        elif test.lower() == 'ttest2n': return self.power_ttest2n(kwargs)
        else: return "Invalid test type: " + test

    def power_anova(self, kwargs):
        kwargs["eta-sq"] = float(kwargs["eta-sq"]) if "eta-sq" in kwargs else None
        kwargs["k"] = int(kwargs["k"]) if "k" in kwargs else None
        kwargs["n"] = int(kwargs["n"]) if "n" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        result = pg.power_anova(eta_squared=kwargs["eta-sq"], k=kwargs["k"], n=kwargs["n"], power=kwargs["power"], alpha=kwargs["alpha"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def power_rm_anova(self, kwargs):
        kwargs["eta-sq"] = float(kwargs["eta-sq"]) if "eta-sq" in kwargs else None
        kwargs["m"] = int(kwargs["m"]) if "m" in kwargs else None
        kwargs["n"] = int(kwargs["n"]) if "n" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        kwargs["corr"] = float(kwargs["corr"]) if "corr" in kwargs else 0.5
        kwargs["epsilon"] = float(kwargs["epsilon"]) if "epsilon" in kwargs else 1.0
        result = pg.power_rm_anova(eta_squared=kwargs["eta-sq"], m=kwargs["m"], n=kwargs["n"], power=kwargs["power"], alpha=kwargs["alpha"], corr=kwargs["corr"], epsilon=kwargs["epsilon"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def power_chi2(self, kwargs):
        kwargs["df"] = int(kwargs["df"]) if "df" in kwargs else 1
        kwargs["w"] = float(kwargs["w"]) if "w" in kwargs else None
        kwargs["n"] = int(kwargs["n"]) if "n" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        result = pg.power_chi2(dof=kwargs["df"], w=kwargs["w"], n=kwargs["n"], power=kwargs["power"], alpha=kwargs["alpha"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def power_corr(self, kwargs):
        kwargs["r"] = float(kwargs["r"]) if "r" in kwargs else None
        kwargs["n"] = int(kwargs["n"]) if "n" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        kwargs["alternative"] = str(kwargs["alternative"]) if "alternative" in kwargs else "two-sided"
        result = pg.power_corr(r=kwargs["r"], n=kwargs["n"], power=kwargs["power"], alpha=kwargs["alpha"], alternative=kwargs["alternative"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def power_ttest(self, kwargs):
        kwargs["d"] = float(kwargs["d"]) if "d" in kwargs else None
        kwargs["n"] = int(kwargs["n"]) if "n" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        kwargs["contrast"] = str(kwargs["contrast"]) if "contrast" in kwargs else "two-samples"
        kwargs["alternative"] = str(kwargs["alternative"]) if "alternative" in kwargs else "two-sided"
        result = pg.power_ttest(d=kwargs["d"], n=kwargs["n"], power=kwargs["power"], alpha=kwargs["alpha"], contrast=kwargs["contrast"], alternative=kwargs["alternative"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def power_ttest2n(self, kwargs):
        kwargs["nx"] = int(kwargs["nx"]) if "nx" in kwargs else 2
        kwargs["ny"] = int(kwargs["ny"]) if "ny" in kwargs else 2
        kwargs["d"] = float(kwargs["d"]) if "d" in kwargs else None
        kwargs["power"] = float(kwargs["power"]) if "power" in kwargs else None
        kwargs["alpha"] = float(kwargs["alpha"]) if "alpha" in kwargs else None
        kwargs["alternative"] = str(kwargs["alternative"]) if "alternative" in kwargs else "two-sided"
        result = pg.power_ttest2n(nx=kwargs["nx"], ny=kwargs["ny"], d=kwargs["d"], power=kwargs["power"], alpha=kwargs["alpha"], alternative=kwargs["alternative"])
        return ["Data given = %s" % kwargs, 
                f"""Result for "None": {result}"""]

    def purpose(self):
        return """
This plugin holds several statistical functions from Pingouin (https://pingouin-stats.org).
[Reference: Vallat, R. (2018). Pingouin: statistics in Python. Journal of Open Source Software, 3(31), 1026, https://doi.org/10.21105/joss.01026]
Currently, it contains power calculation for (i) 1-way ANOVA, (ii) repeated measures ANOVA, (iii) Chi-Square test, (iv) Pearson's correlation, (v) t-test for 1-sample or equal sample sizes, and (vi) t-test for unequal sample sizes.
        """

    def usage(self):
        return self.purpose() + """

1. ANOVA (test=anova)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_anova.html]

    Usage:
        pg pingouin test=anova eta-sq=<ANOVA effect size> k=<Number of groups> n=<Sample size per group> alpha=<significance> power=<power>
    where one of eta-sq, k, n, power, or alpha must be missing, which will be calculated.

    For example:
        pg pingouin test=anova eta-sq=0.1 k=3 n=20 alpha=0.05
    will show the following output (for power): 
        Data given = {'test': 'anova', 'eta-sq': 0.1, 'k': 3, 'n': 20, 'alpha': 0.05, 'power': None}
        Result for "None": 0.6081589938567256

Repeated measures ANOVA (test=rm_anova)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_rm_anova.html]

    Usage:
        pg pingouin test=rm_anova eta-sq=<ANOVA effect size> m=<number of repeated measurements> n=<number of measurements per repeat> alpha=<significance> power=<power> corr=<average correlation between repeats> epsilon=<Epsilon adjustement factor for sphericity>
    where one of eta-sq, m, n, power, or alpha must be missing, which will be calculated.
    If not given, corr is default to 0.1 and epsilon is default to 1.

    For example:
        pg pingouin test=rm_anova eta-sq=0.1 m=3 n=20 alpha=0.05 corr=0.5 epsilon=1
    will show the following output (for power): 
        Data given = {'test': 'rm_anova', 'eta-sq': 0.1, 'm': 3, 'n': 20, 'alpha': 0.05, 'corr': 0.5, 'epsilon': 1.0, 'power': None}
        Result for "None": 0.8913027075779112

Chi-Square (test=chi2 | chisq | chi-sq)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_chi2.html]

    Usage:
        pg pingouin test=chi2 df=<degrees of freedom> w=<Cohen's w> n=<sample size> alpha=<significance> power=<power>
    where one of w, n, alpha, or power must be missing, which will be calculated.
    If not given, df is default to 1.

    For example:
        pg pingouin test=chi2 df=1 w=0.3 n=20 alpha=0.05
    will show the following output (for power):
        Data given = {'test': 'chi2', 'df': 1, 'w': 0.3, 'n': 20, 'alpha': 0.05, 'power': None}
        Result for "None": 0.2686618236636774

Pearson's correlation (test=corr | correlation | pearson | r)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_corr.html]

    Usage:
        pg pingouin test=corr r=<Pearson's correlation> n=<sample size> alpha=<significance> power=<power> alternative={two-sided|greater|less}
    where one of r, n, alpha, or power must be missing, which will be calculated.

    For example:
        pg pingouin test=corr r=0.3 power=0.8 alpha=0.05 alternative=two-sided
    will show the following output (for n):
        Data given = {'test': 'corr', 'r': 0.3, 'power': 0.8, 'alpha': 0.05, 'n': None, 'alternative': 'two-sided'}
        Result for "None": 84.07363774429605

1-sample t-test or 2-samples t-test of equal sample sizes (test=ttest)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_ttest.html]

    Usage: 
        pg pingouin test=ttest d=<Cohen's d> n=<sample size> alpha=<significance> power=<power> contrast=one-sample alternative={two-sided|greater|less}
    where one of d, n, alpha, or power must be missing, which will be calculated.

    For example:
        pg pingouin test=ttest d=0.5 n=20 alpha=0.05 contrast=one-sample alternative=two-sided
    will show the following output (for power):
        Data given = {'test': 'ttest', 'd': 0.5, 'n': 20, 'alpha': 0.05, 'contrast': 'one-sample', 'power': None, 'alternative': 'two-sided'}
        Result for "None": 0.564504418439038

2-samples t-test of unequal sample sizes (test=ttest2n)
[Reference: https://pingouin-stats.org/build/html/generated/pingouin.power_ttest2n.html]

    Usage:
        pg pingouin test=ttest d=<Cohen's d> nx=<sample size 1> nx=<sample size 2> alpha=<significance> power=<power> alternative={two-sided|greater|less}
    where one of d, alpha, or power must be missing, which will be calculated. 
    If not given, nx and ny are default to 2.

    For example:
        pg pingouin test=ttest2n d=0.5 n=20 alpha=0.05 alternatuve=two-sided
    will show the following output (for power):
        Data given = {'test': 'ttest2n', 'd': 0.5, 'n': '20', 'alpha': 0.05, 'nx': 2, 'ny': 2, 'power': None, 'alternative': 'two-sided'}
        Result for "None": 0.06150785655741487
        """