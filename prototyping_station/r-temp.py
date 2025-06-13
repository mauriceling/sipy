import pandas as pd
import subprocess
import os
import time as pytime
import uuid

def ensure_r_package(package_name):
    return f"""
    if (!requireNamespace("{package_name}", quietly = TRUE)) install.packages("{package_name}", repos="https://cloud.r-project.org")
    """

def r(df, method="", plots=None, rscript_exe_path="..\\portable_R\\bin\\Rscript.exe"):
    rscript_exe_path = os.path.abspath(rscript_exe_path)
    if not os.path.exists(rscript_exe_path):
        raise FileNotFoundError(f"Rscript.exe not found at {rscript_exe_path}")

    epoch = str(int(pytime.time()))
    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    r_script_path = f"survival_script_{unique_id}.R"
    df.to_csv(csv_path, index=False)

    method = method.lower()

    r_script = f"""
    data <- read.csv("{csv_path}")
    data${event} <- as.numeric(data${event})
    {f'data${group} <- as.factor(data${group})' if group else ''}

    {models[method]}
    """

    if "survival" in plots and method in survival_curve:
        r_script = r_script + f"""
        pdf("e{epoch}-_plot-{method}.pdf")
        
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


# Example usage
if __name__ == "__main__":
    df = pd.DataFrame({
        'entry': [0, 1, 2, 0, 3, 1, 2, 0, 4, 1],
        'time': [5, 6, 6, 2, 4, 3, 10, 12, 8, 9],
        'time1': [1, 2, 2, 0, 4, 3, 5, 0, 6, 5],
        'time2': [3, 4, 4, 2, 5, 5, 6, 2, 7, 6],
        'event': [1, 1, 0, 1, 1, 0, 1, 0, 1, 1],
        'group': ['A', 'A', 'A', 'B', 'B', 'B', 'A', 'B', 'B', 'A'],
        'age': [30, 45, 38, 50, 60, 41, 33, 55, 48, 36] 
    })

    methods = []
    plots = []
    for method in methods:
        print(f"\n🔹 {method.title()}:")
        print("\n".join(r(df, "time", "event", plots=plots, method=method, group="group")))