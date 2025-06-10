import pandas as pd
import subprocess
import os
import uuid

def anova(df, response, factors, method="anova", covariate=None, posthoc_tests=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
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

    if posthoc_tests is None:
        posthoc_tests = ["dunn", "games-howell", "lsd", "mixed-posthoc", "pairwise", "perm", "scheffe", "tukey", "wilcoxon"]

    posthoc_code = ""
    if posthoc_tests and factors:
        posthoc_code += f"""
        if (length(unique(data${factors[0]})) > 2) {{
        """
        if "dunn" in posthoc_tests and method == "kruskal":
            posthoc_code += f"""
            if (!requireNamespace("dunn.test", quietly = TRUE)) install.packages("dunn.test", repos="https://cloud.r-project.org")
            library(dunn.test)
            print("Dunn's posthoc test:")
            dunn.test::dunn.test(data${response}, data${factors[0]}, method = "bonferroni")
            """
        if "games-howell" in posthoc_tests and method == "welch":
            posthoc_code += f"""
            if (!requireNamespace("PMCMRplus", quietly = TRUE)) install.packages("PMCMRplus", repos="https://cloud.r-project.org")
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
            if (!requireNamespace("emmeans", quietly = TRUE)) install.packages("emmeans", repos="https://cloud.r-project.org")
            if (!requireNamespace("multcomp", quietly = TRUE)) install.packages("multcomp", repos="https://cloud.r-project.org")
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
            if (!requireNamespace("RVAideMemoire", quietly=TRUE)) install.packages("RVAideMemoire", repos="https://cloud.r-project.org")
            library(RVAideMemoire)
            print("Pairwise Permutation t-tests posthoc (Bonferroni):")
            print(pairwise.perm.t.test(data${response}, data${factors[0]}))
            """
        if "scheffe" in posthoc_tests and method in ["anova", "ancova"]:
            posthoc_code += f"""
            if (!requireNamespace("agricolae", quietly = TRUE)) install.packages("agricolae", repos="https://cloud.r-project.org")
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
            if (!requireNamespace("tidyr", quietly = TRUE)) install.packages("tidyr", repos="https://cloud.r-project.org")
            if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr", repos="https://cloud.r-project.org")
            library(tidyr)
            library(dplyr)

            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})
            data$subject <- as.factor(data$subject)

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
            print(kruskal.test({response} ~ {factors[0]}, data=data))
            {posthoc_code}
        """,
        "manova": f"""
            model <- manova(cbind({', '.join(response)}) ~ {factors[0]}, data=data)
            print(summary(model))
        """,
        "mixed": f"""
            if (!requireNamespace("lme4", quietly = TRUE)) install.packages("lme4", repos="https://cloud.r-project.org")
            library(lme4)

            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})
            data$subject <- as.factor(data$subject)

            model <- lmer({response} ~ {factors_formula} + (1|subject), data=data)
            print(summary(model))
            {posthoc_code}
            """,
        "permutation": f"""
            if (!requireNamespace("lmPerm", quietly = TRUE)) install.packages("lmPerm", repos="https://cloud.r-project.org")
            library(lmPerm)

            data <- read.csv("{csv_path}")
            data${factors[0]} <- as.factor(data${factors[0]})
            data$subject <- as.factor(data$subject)

            perm <- aovp({response} ~ {factors_formula}, data=data)
            print(summary(perm))
            {posthoc_code}
        """,
        "repeated": f"""
            data <- read.csv("{csv_path}")
            data$subject <- as.factor(data$subject)
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


# Example usage
df = pd.DataFrame({
    'response': [10, 20, 15, 25, 30, 35, 40, 50, 45, 55],
    'response2': [5, 10, 8, 12, 15, 18, 20, 25, 22, 30],
    'factor1': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'B', 'C', 'A'],
    'factor2': ['X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y'],
    'covariate': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'subject': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
})

methods = ["anova", "ancova", "friedman", "kruskal", "manova", "mixed", "permutation", "repeated", "welch"]
posthocs = ["dunn", "games-howell", "lsd", "mixed-posthoc", "pairwise", "perm", "scheffe", "tukey", "wilcoxon"]
for method in methods:
    print(f"\n🔹 {method.title()}:")
    if method == "manova":
        print("\n".join(anova(df, ['response', 'response2'], ['factor1'], method=method)))
    elif method == "ancova":
        print("\n".join(anova(df, 'response', ['factor1'], method=method, covariate='covariate',posthoc_tests=posthocs)))
    else:
        print("\n".join(anova(df, 'response', ['factor1'], method=method, posthoc_tests=posthocs)))

