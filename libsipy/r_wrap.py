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
import uuid

def regression(df, response, predictors=None, model_type="lm", family=None, rscript_exe_path="portable_R\\bin\\Rscript.exe"):
    """"
    Runs a regression in R using subprocess with a specific R executable.
    Supports lm, glm, poisson, negbinom, multinom, polr, hurdle, zeroinfl, 
    randomForest, svm, lasso, ridge, svr, decision tree, gradient boosting, ElasticNet.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    response (str): The response variable.
    predictors (list, optional): List of predictor variables. If None, uses all other columns.
    model_type (str, optional): The regression model type. Default is "lm".
    family (str, optional): The family argument for glm(). Required for glm().
    rscript_exe_path (str, optional): Path to Rscript.exe (Windows) or Rscript (Linux/Mac). Defaults to "..\\portable_R\\bin\\Rscript.exe".

    Returns:
    list: Output from R as a list of strings.
    """

    rscript_exe_path = os.path.abspath("portable_R\\bin\\Rscript.exe")

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

    def ensure_r_package(package_name):
        return f"""
        if (!requireNamespace("{package_name}", quietly = TRUE)) {{
            install.packages("{package_name}", repos="https://cloud.r-project.org")
        }}
        """

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
        "glm": f"model <- glm({formula}, data=data, family={family})",
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
        """
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