'''!
libsipy (R-Wrap): Collection of R-Based Functions for SiPy

Date created: 16th March 2025

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

import pandas as pd
import subprocess
import os
import time as pytime
import uuid

def ensure_r_package(package_name):
    return f"""
    if (!requireNamespace("{package_name}", quietly = TRUE)) {{
        install.packages("{package_name}", repos="https://cloud.r-project.org")
    }}
    """
       
def anova(df, response, factors, method="anova", covariate=None, posthoc_tests=None, plots=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    epoch = str(int(pytime.time()))
    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"anova_script_{unique_id}.R"
    df.to_csv(csv_path, index=False)

    factors_formula = " + ".join(factors)
    interaction_formula = " * ".join(factors)
    response_formula = f"{response} ~ {interaction_formula}" if len(factors) > 1 else f"{response} ~ {factors_formula}"

    if (posthoc_tests is None) or posthoc_tests == "all":
        posthoc_tests = ["dunn", "games-howell", "lsd", "mixed-posthoc", "pairwise", "perm", "scheffe", "tukey", "wilcoxon"]

    posthoc_code = ""
    if posthoc_tests and factors:
        posthoc_code += f"""
        if (length(unique(data${factors[0]})) > 2) {{
        """
        if "dunn" in posthoc_tests and method == "kruskal":
            posthoc_code += f"""
            {ensure_r_package('dunn.test')}
            library(dunn.test)
            print("Dunn's posthoc test:")
            dunn.test::dunn.test(data${response}, data${factors[0]}, method = "bonferroni")
            """
        if "games-howell" in posthoc_tests and method == "welch":
            posthoc_code += f"""
            {ensure_r_package('PMCMRplus')}
            library(PMCMRplus)
            print("Games-Howell posthoc test:")
            print(gamesHowellTest({response} ~ {factors[0]}, data=data))
            """
        if "lsd" in posthoc_tests and method in ["anova", "ancova"]:
            posthoc_code += f"""
            if (!requireNamespace("agricolae", quietly = TRUE)) install.packages("agricolae", repos="https://cloud.r-project.org")
            library(agricolae)
            print("LSD posthoc test:")
            lsd_model <- aov({response} ~ {factors[0]}, data=data)
            print(LSD.test(lsd_model, "{factors[0]}", p.adj="none"))
            """
        if "mixed-posthoc" in posthoc_tests and method == "mixed":
            posthoc_code += f"""
            {ensure_r_package('emmeans')}
            {ensure_r_package('multcomp')}
            library(emmeans)
            library(multcomp)

            print("Estimated Marginal Means and Pairwise Comparisons (Bonferroni-adjusted):")
            emms <- emmeans(model, pairwise ~ {factors[0]}, adjust = "bonferroni")
            print(emms)
            """
        if "pairwise" in posthoc_tests:
            posthoc_code += f"""
            print("Pairwise t-test posthoc (Bonferroni):")
            print(pairwise.t.test(data${response}, data${factors[0]}, p.adjust.method = "bonferroni"))
            """
        if "perm" in posthoc_tests and method == "permutation":
            posthoc_code += f"""
            {ensure_r_package('RVAideMemoire')}
            library(RVAideMemoire)
            print("Pairwise Permutation t-tests posthoc (Bonferroni):")
            print(pairwise.perm.t.test(data${response}, data${factors[0]}))
            """
        if "scheffe" in posthoc_tests and method in ["anova", "ancova"]:
            posthoc_code += f"""
            {ensure_r_package('agricolae')}
            library(agricolae)
            print("Scheffe posthoc test:")
            scheffe_model <- aov({response} ~ {factors[0]}, data=data)
            print(scheffe.test(scheffe_model, "{factors[0]}"))
            """
        if "tukey" in posthoc_tests and method in ["anova", "ancova"]:
            posthoc_code += f"""
            print("Tukey HSD posthoc:")
            tukey_model <- aov({response} ~ {factors[0]}, data=data)
            print(TukeyHSD(tukey_model))
            """
        if "wilcoxon" in posthoc_tests:
            posthoc_code += f"""
            print("Pairwise Wilcoxon Tests (Bonferroni):")
            print(pairwise.wilcox.test(data${response}, data${factors[0]}, p.adjust.method='bonferroni'))
            """
        posthoc_code += "}"

    models = {
        "ancova": f"""
            model <- aov({response} ~ {interaction_formula} + {covariate}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "anova": f"""
            model <- aov({response_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "friedman": f"""
            {ensure_r_package('tidyr')}
            {ensure_r_package('dplyr')}
            library(tidyr)
            library(dplyr)

            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})

            wide_data <- data %>%
                select(subject, {factors[0]}, {response}) %>%
                pivot_wider(names_from = {factors[0]}, values_from = {response})

            wide_data <- na.omit(wide_data)
            if (nrow(wide_data) == 0) {{
                stop("No complete blocks found for Friedman test.")
            }}

            response_matrix <- as.matrix(wide_data[, -1])
            print(friedman.test(response_matrix))
        """,
        "kruskal": f"""
            print(kruskal.test({response_formula}, data=data))
            {posthoc_code}
        """,
        "manova": f"""
            model <- manova(cbind({', '.join(response)}) ~ {interaction_formula}, data=data)
            print(summary(model))
        """,
        "mixed": f"""
            {ensure_r_package('lme4')}
            library(lme4)
            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})

            model <- lmer({response} ~ {factors_formula} + (1|subject), data=data)
            print(summary(model))
            {posthoc_code}
            """,
        "permutation": f"""
            {ensure_r_package('lmPerm')}
            library(lmPerm)

            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})

            model <- aovp({response_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "repeated": f"""
            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})

            model <- aov({response} ~ {factors[0]} + Error(subject/{factors[0]}), data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "welch": f"""
            model <- oneway.test({response} ~ {factors[0]}, data=data)
            print(model)
            {posthoc_code}
        """,
    }

    if method not in models:
        raise ValueError("Invalid method specified.")

    r_script = f"""
    data <- read.csv("{csv_path}")
    data${factors[0]} <- as.factor(data${factors[0]})
    {f'data${factors[1]} <- as.factor(data${factors[1]})' if len(factors) > 1 else ''}
    {f'data${covariate} <- as.numeric(data${covariate})' if covariate else ''}

    {models[method]}
    """

    if "diagnostic" in plots and method in ["ancova", "anova", "mixed", "permutation", "repeated"]:
        r_script = r_script + f"""
            residuals <- residuals(model)
            fitted <- fitted.values(model)

            if (!is.null(residuals) && all(!is.na(residuals))) {{
                pdf("e{epoch}-diagnostic_plot-{method}.pdf")
                diagnostics_anova <- function(residuals, fitted, label) {{
                    par(mfrow=c(1, 2))

                    qqnorm(residuals, main=paste("QQ-Plot:", label))
                    qqline(residuals, col="red")

                    plot(fitted, residuals,
                         main=paste("Residuals vs Fitted:", label),
                         xlab="Fitted values", ylab="Residuals", pch=19, col="darkblue")
                    abline(h=0, col="red", lty=2)

                    par(mfrow=c(1,1))
                }}
                diagnostics_anova(residuals, fitted, "{method}")
                dev.off()
            }} else {{
                cat("Residuals are missing or invalid. Skipping diagnostic plots.\\n")
            }}
            """

    with open(r_script_path, "w") as f:
        f.write(r_script)

    command = [rscript_exe_path, "--vanilla", r_script_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running R script:\n{e.stderr}")
        raise
    finally:
        pytime.sleep(0.2)
        os.remove(csv_path)
        os.remove(r_script_path)

    return result.stdout.strip().split("\n")
     
def regression(df, response, predictors=None, model_type="lm", rscript_exe_path="portable_R\\bin\\Rscript.exe"):
    """"
    Runs a regression in R using subprocess with a specific R executable.
    Supports lm, glm, poisson, negbinom, multinom, polr, hurdle, zeroinfl, 
    randomForest, svm, lasso, ridge, svr, decision tree, gradient boosting, ElasticNet.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    response (str): The response variable.
    predictors (list, optional): List of predictor variables. If None, uses all other columns.
    model_type (str, optional): The regression model type. Default is "lm".
    rscript_exe_path (str, optional): Path to Rscript.exe (Windows) or Rscript (Linux/Mac). Defaults to "..\\portable_R\\bin\\Rscript.exe".

    Returns:
    list: Output from R as a list of strings.
    """

    rscript_exe_path = os.path.abspath(rscript_exe_path)

    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    # Generate temporary file names
    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"script_{unique_id}.R"

    if predictors is None:
        predictors = [col for col in df.columns if col != response]

    formula = f"{response} ~ {' + '.join(predictors)}"
    df.to_csv(csv_path, index=False)

    # Handling small datasets for GBM
    gbm_adjustment = """
    if (nrow(data) < 10) {
        n_minobsinnode <- 1
        bag_fraction <- 0.5
    } else {
        n_minobsinnode <- min(10, floor(nrow(data) / 3))
        bag_fraction <- 0.75
    }
    """

    model_calls = {
        "lm": f"model <- lm({formula}, data=data)",
        "poisson": f"model <- glm({formula}, data=data, family=poisson())",
        "negbinom": f"{ensure_r_package('MASS')} model <- MASS::glm.nb({formula}, data=data)",
        "multinom": f"{ensure_r_package('nnet')} model <- nnet::multinom({formula}, data=data)",
        "polr": f"""
            {ensure_r_package('MASS')}
            data${response} <- as.factor(data${response})  # Convert to factor
            if (length(unique(data${response})) >= 3) {{
                model <- MASS::polr({formula}, data=data)
            }} else {{
                stop("Error: polr() requires the response to have at least 3 levels.")
            }}
        """,
        "hurdle": f"{ensure_r_package('pscl')} model <- pscl::hurdle({formula}, data=data)",
        "zeroinfl": f"{ensure_r_package('pscl')} model <- pscl::zeroinfl({formula}, data=data)",
        "randomforest": f"{ensure_r_package('randomForest')} model <- randomForest::randomForest({formula}, data=data)",
        "svm": f"{ensure_r_package('e1071')} model <- e1071::svm({formula}, data=data)",
        "lasso": f"""
            {ensure_r_package('glmnet')}
            X <- model.matrix({formula}, data)[,-1]
            Y <- data${response}
            model <- glmnet::cv.glmnet(X, Y, alpha=1)
        """,
        "ridge": f"""
            {ensure_r_package('glmnet')}
            X <- model.matrix({formula}, data)[,-1]
            Y <- data${response}
            model <- glmnet::cv.glmnet(X, Y, alpha=0)
        """,
        "svr": f"""
            {ensure_r_package('e1071')}
            model <- e1071::svm({formula}, data=data)
        """,
        "decision_tree": f"""
            {ensure_r_package('rpart')}
            model <- rpart::rpart({formula}, data=data)
        """,
        "gradient_boosting": f"""
            {ensure_r_package('gbm')}
            {gbm_adjustment}
            model <- gbm::gbm({formula}, data=data, n.trees=100, interaction.depth=3, shrinkage=0.01, n.minobsinnode=n_minobsinnode, bag.fraction=bag_fraction)
        """,
        "elasticnet": f"""
            {ensure_r_package('glmnet')}
            X <- model.matrix({formula}, data)[,-1]
            Y <- data${response}
            model <- glmnet::cv.glmnet(X, Y, alpha=0.5)
        """,
        "probit_regression": f"""
            model <- glm({formula}, data=data, family=binomial(link="probit"))
        """,
        "cloglog_regression": f"model <- glm({formula}, data=data, family=binomial(link='cloglog'))",
        "gamma_regression": f"model <- glm({formula}, data=data, family=Gamma(link='log'))",
        "inverse_gaussian": f"model <- glm({formula}, data=data, family=inverse.gaussian(link='log'))",
        "quasi_poisson": f"model <- glm({formula}, data=data, family=quasipoisson())",
        "quasi_binomial": f"model <- glm({formula}, data=data, family=quasibinomial())",
        "tweedie_regression": f"""
            {ensure_r_package('statmod')}
            library(statmod)
            model <- glm({formula}, data=data, family=statmod::tweedie(var.power=1.5, link.power=0))
        """,
    }

    if model_type not in model_calls:
        raise ValueError(f"Invalid model_type: {model_type}")

    r_script = f"""
    data <- read.csv("{csv_path}")
    {model_calls[model_type]}
    summary(model)
    """

    with open(r_script_path, "w") as f:
        f.write(r_script)

    command = [rscript_exe_path, "--vanilla", r_script_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running R script:\n{e.stderr}")
        raise
    finally:
        os.remove(csv_path)
        os.remove(r_script_path)

    return result.stdout.strip().split("\n")