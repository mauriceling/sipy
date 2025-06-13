import pandas as pd
import subprocess
import os
import time as pytime
import uuid

def ensure_r_package(package_name):
    return f"""
    if (!requireNamespace("{package_name}", quietly = TRUE)) install.packages("{package_name}", repos="https://cloud.r-project.org")
    """

def categorical_test(df, method="chisq-gof", variable=None, expected_probs=None, row_var=None, col_var=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"categorical_script_{unique_id}.R"
    df.to_csv(csv_path, index=False)

    expected_code = ""
    if expected_probs:
        expected_str = ", ".join(str(p) for p in expected_probs)
        expected_code = f"expected_probs <- c({expected_str})"

    models = {
        "chisq-gof": f"""
            {ensure_r_package("stats")}
            library(stats)
            data <- read.csv("{csv_path}")
            data${variable} <- as.factor(data${variable})
            observed <- table(data${variable})
            {expected_code}
            print("Chi-Square Goodness-of-Fit Test:")
            print(chisq.test(observed{', p = expected_probs' if expected_probs else ''}))
        """,
        "chisq-assoc": f"""
            {ensure_r_package("vcd")}
            library(vcd)
            data <- read.csv("{csv_path}")
            data${row_var} <- as.factor(data${row_var})
            data${col_var} <- as.factor(data${col_var})
            tbl <- table(data${row_var}, data${col_var})
            chi_result <- chisq.test(tbl)
            print("Chi-Square Test of Association:")
            print(tbl)
            print(chi_result)
            cramer_v <- assocstats(tbl)$cramer
            stats <- assocstats(tbl)
            cat("Contingency Coefficient:", stats$contingency, "\\n")
            cat("Cramer's V:", stats$cramer, "\\n")
            if (all(dim(tbl) == c(2,2))) {{
                phi <- sqrt(chi_result$statistic / sum(tbl))
                cat("Phi Coefficient:", phi, "\\n")
            }}
        """,
        "mcnemar": f"""
            data <- read.csv("{csv_path}")
            data${row_var} <- as.factor(data${row_var})
            data${col_var} <- as.factor(data${col_var})
            tbl <- table(data${row_var}, data${col_var})
            if (all(dim(tbl) == c(2, 2))) {{
                print("McNemar's Test:")
                print(tbl)
                test_result <- mcnemar.test(tbl)
                print(test_result)
                b <- tbl[1,2]
                c <- tbl[2,1]
                if ((b + c) > 0) {{
                    g <- abs(b - c) / sqrt(b + c)
                    cat("Cohen's g (effect size):", g, "\\n")
                }} else {{
                    cat("Cohen's g not computed: no discordant pairs (b + c = 0)\\n")
                }}
            }} else {{
                print("Error: McNemar's Test requires a 2x2 contingency table.")
            }}
        """,
        "fisher": f"""
            data <- read.csv("{csv_path}")
            data${row_var} <- as.factor(data${row_var})
            data${col_var} <- as.factor(data${col_var})
            tbl <- table(data${row_var}, data${col_var})
            if (all(dim(tbl) == c(2, 2))) {{
                print("Fisher's Exact Test (2x2):")
                print(tbl)
                print(fisher.test(tbl))
            }} else {{
                print("Fisher's Exact Test (generalized for larger tables):")
                print(tbl)
                print(fisher.test(tbl, simulate.p.value=TRUE))
            }}
        """
    }

    if method not in models:
        raise ValueError("Invalid method specified.")

    r_script = models[method]

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


# Example usage
if __name__ == "__main__":
    df = pd.DataFrame({
        'color': ['red', 'blue', 'red', 'green', 'red', 'blue', 'green', 'green', 'blue', 'blue'],
        'gender': ['M', 'F', 'F', 'M', 'M', 'F', 'M', 'F', 'F', 'M'],
    })

    df2 = pd.DataFrame({
        'department': ['HR', 'HR', 'HR', 'IT', 'IT', 'IT', 'Sales', 'Sales', 'Sales', 'Ops', 'Ops', 'Ops'],
        'satisfaction': ['High', 'Medium', 'Low', 'High', 'Low', 'Low', 'Medium', 'Medium', 'High', 'Low', 'High', 'Medium']
    })

    df3 = pd.DataFrame({
        'before': ['Yes', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes', 'No'],
        'after':  ['Yes', 'No',  'No', 'No',  'No', 'Yes', 'Yes', 'No']
    })

    print("🔹 Chi-Square Goodness of Fit (equal expected):")
    print("\n".join(categorical_test(df, method="chisq-gof", variable="color")))

    print("\n🔹 Chi-Square Goodness of Fit (custom expected):")
    print("\n".join(categorical_test(df, method="chisq-gof", variable="color", expected_probs=[0.3, 0.3, 0.4])))

    print("\n🔹 Chi-Square Test of Association:")
    print("\n".join(categorical_test(df, method="chisq-assoc", row_var="gender", col_var="color")))
    print("\n".join(categorical_test(df2, method="chisq-assoc", row_var="department", col_var="satisfaction")))

    print("\n🔹 McNemar's Test:")
    print("\n".join(categorical_test(df3, method="mcnemar", row_var="before", col_var="after")))

    print("\n🔹 Fisher's Exact Test:")
    print("\n".join(categorical_test(df3, method="fisher", row_var="before", col_var="after")))
