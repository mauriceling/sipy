import pandas as pd
import subprocess
import os
import uuid

def survival_analysis(df, time_column, event_column, covariates=None, strata=None, method="cox", rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"survival_script_{unique_id}.R"
    df.to_csv(csv_path, index=False)

    formula_parts = []
    if covariates:
        formula_parts.append(" + ".join(covariates))
    if strata:
        formula_parts.append(f"strata({strata})")
    formula_rhs = " + ".join(formula_parts) if formula_parts else "1"
    surv_formula = f"Surv({time_column}, {event_column}) ~ {formula_rhs}"

    model_code = {
        "cox": f"""
            model <- coxph({surv_formula}, data=data)
            print(summary(model))
        """,
        "kaplan": f"""
            model <- survfit({surv_formula}, data=data)
            print(summary(model))
        """
    }

    if method not in model_code:
        raise ValueError("Invalid method. Use 'cox' or 'kaplan'.")

    r_script = f"""
    if (!requireNamespace("survival", quietly=TRUE)) install.packages("survival", repos="https://cloud.r-project.org")
    library(survival)

    data <- read.csv("{csv_path}")
    data${event_column} <- as.numeric(data${event_column})
    data${time_column} <- as.numeric(data${time_column})
    {'; '.join([f'data${col} <- as.factor(data${col})' for col in covariates or []])}
    {'data$' + strata + ' <- as.factor(data$' + strata + ')' if strata else ''}

    {model_code[method]}
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
if __name__ == "__main__":
    df = pd.DataFrame({
        'time': [5, 8, 12, 4, 9, 15, 22, 6, 14, 10],
        'status': [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'group': ['A', 'A', 'B', 'A', 'B', 'B', 'A', 'B', 'A', 'B'],
        'sex': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F']
    })

    print("\n🔹 Cox PH Model:")
    print("\n".join(survival_analysis(df, time_column='time', event_column='status', covariates=['group', 'sex'], method='cox')))

    print("\n🔹 Kaplan-Meier Estimate:")
    print("\n".join(survival_analysis(df, time_column='time', event_column='status', covariates=['group', 'sex'], method='kaplan')))
