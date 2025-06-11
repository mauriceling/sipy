import pandas as pd
import subprocess
import os
import uuid

def ensure_r_package(package_name):
    return f"""
    if (!requireNamespace("{package_name}", quietly = TRUE)) install.packages("{package_name}", repos="https://cloud.r-project.org")
    """
    
def regression(df, response, predictors=None, model_type="lm", rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
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

# Example dataset
df = pd.DataFrame({
    'yN': [1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5],  # Numeric response
    'yB': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],  # Binary response
    'yC': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'],  # Categorical response
    'x1': [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
    'x2': [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
    'x3': [5, 8, 6, 10, 12, 14, 18, 20, 24, 30],
    'x4': [3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3],
    'x5': [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
})

# Define all models and map them to appropriate response types
all_models = {
    "lm": "yN",
    "poisson": "yN",
    "negbinom": "yN",
    "multinom": "yC",
    "polr": "yC",
    "hurdle": "yN",
    "zeroinfl": "yN",
    "randomforest": "yN",
    "svm": "yN",
    "lasso": "yN",
    "ridge": "yN",
    "svr": "yN",
    "decision_tree": "yN",
    "gradient_boosting": "yN",
    "elasticnet": "yN",
    "probit_regression": "yB",
    "cloglog_regression": "yB",
    "gamma_regression": "yN",
    "inverse_gaussian": "yN",
    "quasi_poisson": "yN",
    "quasi_binomial": "yB",
    "tweedie_regression": "yN"
}

independent_vars = ["x1", "x2", "x3", "x4", "x5"]

# Run each model
for model_type, response_var in all_models.items():
    print(f"\n🔹 Running {model_type} model with response variable: {response_var}\n")
    try:
        output = regression(df, response_var, independent_vars, model_type)
        print("\n".join(output))
    except Exception as e:
        print(f"⚠️ Error in {model_type}: {e}")
    
    print("\n" + "="*50 + "\n")
