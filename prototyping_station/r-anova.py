import pandas as pd
import subprocess
import os
import uuid

def ensure_r_package(package_name):
    return f"""
    if (!requireNamespace(\"{package_name}\", quietly = TRUE)) {{
        install.packages(\"{package_name}\", repos=\"https://cloud.r-project.org\")
    }}
    """

def anova(df, response, factors, method="anova", covariate=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"anova_script_{unique_id}.R"

    df.to_csv(csv_path, index=False)

    factors_formula = " + ".join(factors)
    interaction_formula = " * ".join(factors) 

    response_formula = f"{response} ~ {interaction_formula}" if len(factors) > 1 else f"{response} ~ {factors_formula}"

    repeated_formula = f"""
    install.packages("ez", repos="https://cloud.r-project.org")
    library(ez)

    data <- read.csv("{csv_path}")
    data$subject <- as.factor(data$subject)
    {f'data${factors[0]} <- as.factor(data${factors[0]})' if len(factors) > 0 else ''}
    {f'data${factors[1]} <- as.factor(data${factors[1]})' if len(factors) > 1 else ''}

    result <- ezANOVA(
        data = data,
        dv = {response},
        wid = subject,
        within = .({", ".join(factors)}),
        type = 3
    )

    print(result)
    """

    friedman_formula = f"""
    if (!requireNamespace("tidyr", quietly = TRUE)) install.packages("tidyr", repos="https://cloud.r-project.org")
    if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr", repos="https://cloud.r-project.org")
    library(tidyr)
    library(dplyr)

    data <- read.csv("{csv_path}")
    data${factors[0]} <- as.factor(data${factors[0]})
    data$subject <- as.factor(data$subject)

    long_data <- data %>%
        select(subject, {factors[0]}, {response}) %>%
        pivot_wider(names_from = {factors[0]}, values_from = {response})

    long_data <- na.omit(long_data)

    if (nrow(long_data) == 0) {{
        stop("No complete blocks found for Friedman test.")
    }}

    response_matrix <- as.matrix(long_data[, -1])
    res <- friedman.test(response_matrix)
    print(res)
    """

    mixed_formula = f"""
    if (!requireNamespace("lme4", quietly = TRUE)) install.packages("lme4", repos="https://cloud.r-project.org")
    library(lme4)

    data <- read.csv("{csv_path}")
    data${factors[0]} <- as.factor(data${factors[0]})
    data$subject <- as.factor(data$subject)

    model <- lmer({response} ~ {factors_formula} + (1|subject), data=data)
    print(summary(model))
    """

    permutation_formula = f"""
    if (!requireNamespace("lmPerm", quietly = TRUE)) install.packages("lmPerm", repos="https://cloud.r-project.org")
    library(lmPerm)

    data <- read.csv("{csv_path}")
    data${factors[0]} <- as.factor(data${factors[0]})
    data$subject <- as.factor(data$subject)

    perm <- aovp({response} ~ {factors_formula}, data=data)
    print(summary(perm))
    """

    posthoc = f"""
    if (length(unique(data${factors[0]})) > 2) {{
        posthoc_result <- pairwise.t.test(data${response}, data${factors[0]}, p.adjust.method = "bonferroni")
        print("\nPost-hoc Pairwise T-Tests:")
        print(posthoc_result)

        tukey_model <- aov({response} ~ {factors[0]}, data = data)
        tukey_result <- TukeyHSD(tukey_model)
        print("\nTukey's HSD:")
        print(tukey_result)
    }}
    """

    models = {
        "anova": f"aov({response_formula}, data=data)\n{posthoc}",
        "manova": f"manova(cbind({', '.join(response)}) ~ {factors[0]}, data=data)",
        "ancova": f"aov({response} ~ {interaction_formula} + {covariate}, data=data)\n{posthoc}",
        "repeated": repeated_formula,
        "welch": f"oneway.test({response} ~ {factors[0]}, data=data)\n{posthoc}",
        "kruskal": f"kruskal.test({response} ~ {factors[0]}, data=data)",
        "friedman": friedman_formula,
        "permutation": permutation_formula,
        "mixed": mixed_formula
    }

    if method not in models:
        raise ValueError("Invalid method specified.")

    r_script = f"""
    data <- read.csv("{csv_path}")
    data${factors[0]} <- as.factor(data${factors[0]})
    data$subject <- as.factor(data$subject)
    {f'data${factors[1]} <- as.factor(data${factors[1]})' if len(factors) > 1 else ''}
    {f'data${covariate} <- as.numeric(data${covariate})' if covariate else ''}

    {models[method]}
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
    'response': [10, 20, 15, 25, 30, 35, 40, 50, 45, 55],
    'response2': [5, 10, 8, 12, 15, 18, 20, 25, 22, 30],
    'factor1': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'B', 'C', 'A'],
    'factor2': ['X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y'],
    'covariate': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'subject': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
})

# Run different ANOVA analyses
methods = ["anova", "manova", "ancova", "welch", "kruskal", "friedman", "permutation", "mixed"]
for method in methods:
    print(f"\n🔹 {method.replace('_', ' ').title()}:")
    if method == "manova":
        print("\n".join(anova(df, ['response', 'response2'], ['factor1', 'factor2'], method=method)))
    elif method == "ancova":
        print("\n".join(anova(df, 'response', ['factor1', 'factor2'], method=method, covariate='covariate')))
    else:
        print("\n".join(anova(df, 'response', ['factor1'], method=method)))
