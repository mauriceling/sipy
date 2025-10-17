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
       
def anova(df, response, factors, method="anova", covariates=None, posthoc_tests=None, plots=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
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
    covariates_formula = " + ".join(covariates)

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
            model <- aov({response} ~ {interaction_formula} + {covariates_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "anova": f"""
            model <- aov({response_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        # friedman not working
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
        "mancova": f"""
            model <- manova(cbind({', '.join(response)}) ~ {interaction_formula} + {covariates_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        "manova": f"""
            model <- manova(cbind({', '.join(response)}) ~ {interaction_formula}, data=data)
            print(summary(model))
            {posthoc_code}
        """,
        # mixed not working
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
        # repeated not working
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

    conversion_code = ""
    for f in factors:
        conversion_code = conversion_code + """
            data$%s <- as.factor(data$%s)""" % (f, f)
    for c in covariates:
        conversion_code = conversion_code + """
            data$%s <- as.numeric(data$%s)""" % (c, c) 
   
    r_script = f"""
    data <- read.csv("{csv_path}")
    
    {conversion_code}

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

    #print(r_script)
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
     
def regression(df, response, predictors=None, model_type="lm", rscript_exe_path="/usr/local/bin/Rscript"):
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

def survival_analysis(df, time, event, time2=None, method="kaplan-meier", group=None, covariates=None, plots=None, rscript_exe_path="/usr/local/bin/Rscript", cause=None, dist=None):
    """
    Run survival analysis in R via subprocess from Python.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing survival times, event indicators, and optional grouping/covariate columns.

    time : str
        Name of the column in `df` representing the survival time (or follow-up time).

    event : str
        Name of the column in `df` representing the event indicator.
        Typically coded as 1 = event occurred, 0 = censored.

    method : str, default="kaplan-meier"
        Survival analysis method to apply. Options include:
        - "kaplan-meier"         : Non-parametric Kaplan-Meier estimator
        - "log-rank"             : Log-rank test for group differences
        - "cox"                  : Cox proportional hazards model
        - "cox-interaction"      : Cox PH model with interaction (e.g., group * age)
        - "time-dependent-cox"   : Cox model with time-dependent covariates
        - "frailty-cox"          : Cox PH model with frailty term
        - "left-truncated-cox"   : Cox PH with left-truncated data
        - "aft"                  : Parametric accelerated failure time model (Weibull)
        - "exponential-aft"      : AFT with exponential distribution
        - "competing-risks"      : Fine-Gray competing risks regression
        - Interval-censored models (require `time1`/`time2` columns):
            * "interval-aft"     : Parametric AFT model (log-logistic dist.)
            * "interval-censored": Parametric survival model for intervals
            * "interval-np"      : Nonparametric interval-censored model (NPMLE)
            * "interval-par"     : Parametric interval-censored model (Weibull)
            * "interval-sp"      : Semiparametric interval-censored model

    group : str, optional
        Name of a categorical column in `df` to use as a grouping variable
        or covariate. If provided:
        - Kaplan-Meier → produces separate survival curves by group.
        - Log-rank → tests group differences.
        - Cox/AFT models → treats group as a covariate.
        If None, analyses are performed without stratification (overall survival only).

    plots : list of str, optional
        If provided, generates plots as PDF files. Available options:
        - "survival" : Survival curve (supported for Kaplan-Meier, Cox, Stratified Cox, Left-truncated Cox)

    rscript_exe_path : str, default="..\\portable_R\\bin\\Rscript.exe"
        Path to the Rscript executable.

    Returns
    -------
    list of str
        Console output from the R analysis, split line by line.

    Notes
    -----
    - Requires R and the relevant R packages installed.
    - For interval-censored methods, `df` must include `time1` and `time2` columns.
    - Event column must be binary (1 = event, 0 = censored).
    - Group column should be categorical if specified.

    Examples
    --------
    >>> survival_analysis(df, time="time", event="event", method="kaplan-meier", group="treatment")
    Runs a Kaplan-Meier survival analysis comparing groups in `treatment`.

    >>> survival_analysis(df, time="time", event="event", method="cox", group="sex", plots=["survival"])
    Fits a Cox proportional hazards model by sex and saves survival curves.
    """
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    epoch = str(int(pytime.time()))
    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"survival_script_{unique_id}.R"
    df.to_csv(csv_path, index=False)

    method = method.lower()

    if covariates is None and group:
        covariates = [group]

    formula = " + ".join(covariates) if covariates else "1"
    
    factor_conversion = "\n".join([
        f'if (!is.numeric(data${var})) data${var} <- as.factor(data${var})'
        for var in covariates])

    models = {
        "aft": f"""
            surv_obj <- Surv(data${time}, data${event})
            aft_model <- survreg(surv_obj ~ {formula}, data = data, dist = "weibull")
            print(summary(aft_model))

            cat("\\nScale parameter:\\n")
            print(aft_model$scale)

            cat("\\nLinear predictors (first 10):\\n")
            print(head(predict(aft_model, type = "lp"), 10))
        """,
        "competing-risks": f"""
            {ensure_r_package('cmprsk')}
            library(cmprsk)

            # Convert group to numeric (if it's not already)
            data$group_numeric <- as.numeric(as.factor(data${group}))
            fg_model <- crr(ftime = data${time}, fstatus = data${cause}, cov1 = data.frame(group = data$group_numeric))
            print(summary(fg_model))
        """,
        "cox": f""" 
            surv_obj <- Surv(data${time}, data${event})
            cox_model <- coxph(surv_obj ~ {formula}, data = data)
            print(summary(cox_model))

            cat("\\nTesting proportional hazards assumption:\\n")
            zph_test <- cox.zph(cox_model)
            print(zph_test)

            cat("\\nMartingale residuals (first 10):\\n")
            martingale_resid <- residuals(cox_model, type = "martingale")
            print(head(martingale_resid, 10))

            cat("\\nDeviance residuals (first 10):\\n")
            deviance_resid <- residuals(cox_model, type = "deviance")
            print(head(deviance_resid, 10))
        """,
        "cox-interaction": f"""
            surv_obj <- Surv(data${time}, data${event})
            # Build formula with 2-way interactions
            rhs <- paste("(", paste(c({', '.join([f'"{v}"' for v in covariates])}), collapse=" + "), ")", sep="")
            formula_str <- as.formula(paste("surv_obj ~", rhs, "^2"))
            
            interaction_model <- coxph(formula_str, data = data)
            print(summary(interaction_model))

            cat("\\nTesting proportional hazards assumption:\\n")
            suppressWarnings(print(cox.zph(interaction_model)))
        """,
        "exponential-aft": f"""
            surv_obj <- Surv(data${time}, data${event})
            exp_model <- survreg(surv_obj ~ {formula}, data = data, dist = "exponential")
            print(summary(exp_model))

            cat("\\nLinear predictors (first 10):\\n")
            print(head(predict(exp_model, type = "lp"), 10))
        """,
        "frailty-cox": f"""
            surv_obj <- Surv(data${time}, data${event})
            frailty_term <- "{covariates[0]}"
            fixed_effects <- c({', '.join([f'"{v}"' for v in covariates[1:]])})
            if (length(fixed_effects) > 0) {{
                rhs <- paste(c(fixed_effects, paste0("frailty(", frailty_term, ")")), collapse = " + ")
            }} else {{
                rhs <- paste0("frailty(", frailty_term, ")")
            }}
            formula_str <- as.formula(paste("surv_obj ~", rhs))
            frailty_model <- coxph(formula_str, data = data)
            print(summary(frailty_model))
        """,
        "interval-aft": f"""
            {ensure_r_package('icenReg')}
            library(icenReg)

            # AFT-style model for interval-censored data using loglogistic distribution
            aft_fit <- ic_par(Surv({time}, {time2}, type = "interval2") ~ {formula}, data = data, dist = "loglogistic")
            print(summary(aft_fit))

            cat("\\nBaseline survival estimates:\\n")
            print(getFitEsts(aft_fit))
        """,
        "interval-censored": f"""
            {ensure_r_package('icenReg')}
            library(icenReg)

            # icenReg requires left and right times as vectors
            fit <- ic_par(Surv({time}, {time2}, type = "interval2") ~ {formula}, data = data, dist = "loglogistic")
            print(summary(fit))

            cat("\\nFit estimates:\\n")
            print(getFitEsts(fit))
        """,
        "interval-np": f"""
            {ensure_r_package('icenReg')}
            library(icenReg)

            to_df_from_sc <- function(sc) {{
              intervals <- as.data.frame(sc$Tbull_ints)
              if (ncol(intervals) == 1) {{
                colnames(intervals) <- c("Start")
                intervals$End <- intervals$Start
              }} else {{
                colnames(intervals) <- c("Start", "End")
              }}
              surv_probs <- unlist(sc$S_curves)
              n_intervals <- nrow(intervals)
              surv_probs <- surv_probs[seq_len(min(length(surv_probs), n_intervals))]
              df0 <- cbind(intervals, Survival = surv_probs)
              return(df0)
            }}

            # Decide fit mode: use group if available, else pooled
            if ("{group}" %in% colnames(data)) {{
              if (!is.factor(data${group})) {{
                data${group} <- as.factor(data${group})
              }}
              groups <- levels(data${group})
              fits <- lapply(groups, function(g) {{
                sub <- subset(data, data${group} == g)
                ic_np(Surv({time}, {time2}, type = "interval2") ~ 0, data = sub)
              }})
              names(fits) <- groups
              all_curves <- do.call(rbind, lapply(seq_along(fits), function(i) {{
                sc <- getSCurves(fits[[i]])
                df0 <- to_df_from_sc(sc)
                df0$Group <- names(fits)[i]
                return(df0)
              }}))
              print(all_curves)
            }} else {{
              np_fit <- ic_np(Surv({time}, {time2}, type = "interval2") ~ 0, data = data)
              sc <- getSCurves(np_fit)
              df0 <- to_df_from_sc(sc)
              df0$Group <- "pooled"
              print(df0)
            }}
        """,
        "interval-par": f"""
            {ensure_r_package('icenReg')}
            library(icenReg)

            # Fit parametric model (default: Weibull) for interval-censored data
            par_fit <- ic_par(Surv({time}, {time2}, type = "interval2") ~ {formula}, data = data, dist = "weibull")

            cat("Parametric model coefficients (Weibull):\\n")
            print(coef(par_fit))  # Correct way to extract coefficients

            cat("\\nBaseline survival estimates:\\n")
            fit_ests <- getFitEsts(par_fit)
            print(fit_ests)
        """,
        "interval-sp": f"""
            {ensure_r_package('icenReg')}
            library(icenReg)

            sp_fit <- ic_sp(Surv({time}, {time2}, type = "interval2") ~ {formula}, data = data)
            print(summary(sp_fit))

            cat("\\nSmoothed survival estimates:\\n")
            print(getSCurves(sp_fit))
        """,
        "kaplan-meier": f"""
            surv_obj <- Surv(data${time}, data${event})
            fit <- survfit(surv_obj ~ {formula}, data = data)
            print(summary(fit))

            cat("\\nMedian survival times:\\n")
            print(summary(fit)$table[,"median"])
        """,
        "left-truncated-cox": f"""
            surv_obj <- Surv(data$entry, data${time}, data${event})
            cox_lt_model <- coxph(surv_obj ~ {formula}, data = data)
            print(summary(cox_lt_model))

            cat("\\nPH assumption test:\\n")
            print(cox.zph(cox_lt_model))
        """,
        "log-rank": f"""
            surv_obj <- Surv(data${time}, data${event})
            logrank <- survdiff(surv_obj ~ {formula}, data = data)
            print(logrank)
        """,
        "time-dependent-cox": f"""
            surv_obj <- Surv(data${time}, data${event})
            # Convert group (or whichever variable) into numeric
            data$group_numeric <- as.numeric(as.factor(data${group}))
            
            # Fit time-dependent Cox model (log-time interaction with group_numeric)
            cox_td_model <- coxph(surv_obj ~ tt(group_numeric), data = data,
                                  tt = function(x, t, ...) x * log(t))
            print(summary(cox_td_model))
        """,
    }

    if method not in models:
        raise ValueError(f"Invalid method: {method}. Choose from: kaplan-meier, log-rank, cox.")

    survival_curve = {
        "kaplan-meier": f"""
            surv_obj <- Surv(data${time}, data${event})
            fit <- survfit(surv_obj ~ data${group}, data = data)
            plot(fit, col = 1:length(levels(data${group})), lty = 1,
                 main = "Kaplan-Meier Survival Curve",
                 xlab = "Time", ylab = "Survival Probability")
            legend("topright", legend = levels(data${group}),
                   col = 1:length(levels(data${group})), lty = 1)
        """,
        "cox": f"""
            surv_obj <- Surv(data${time}, data${event})
            cox_model <- coxph(surv_obj ~ data${group}, data = data)
            fit <- survfit(cox_model)
            plot(fit, col = 1:length(levels(data${group})), lty = 1,
                 main = "Cox Model Survival Curve",
                 xlab = "Time", ylab = "Survival Probability")
        """,
        "left-truncated-cox": f"""
            surv_obj <- Surv(data$entry, data${time}, data${event})
            cox_lt_model <- coxph(surv_obj ~ data${group}, data = data)
            fit <- survfit(cox_lt_model)
            plot(fit, col = 1:length(levels(data${group})), lty = 1,
                 main = "Left-Truncated Cox Model Survival Curve",
                 xlab = "Time", ylab = "Survival Probability")
        """
    }

    r_script = f"""
    {ensure_r_package('survival')}
    library(survival)

    data <- read.csv("{csv_path}")
    data${event} <- as.numeric(data${event})
    {f'data${group} <- as.factor(data${group})' if group else ''}

    {factor_conversion}
    {models[method]}
    """

    if plots == None: pass
    elif "survival" in plots and method in survival_curve:
        r_script = r_script + f"""
        pdf("e{epoch}-survival_plot-{method}.pdf")
        {survival_curve[method]}
        dev.off()
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