import os
import sys
import uuid
import subprocess
import pandas as pd


def regression(df, response, predictors=None, model_type="ols", julia_exe_path="..\\portable_julia\\bin\\julia.exe"):
    """
    Runs a regression in Julia using subprocess.
    Demonstrates Julia as a numerical backend for SiPy.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    response : str
        Response variable
    predictors : list, optional
        Predictor variables
    model_type : str
        Currently supports: 'ols'
    julia_exe_path : str
        Path to Julia executable

    Returns
    -------
    list of str
        Output from Julia
    """

    julia_exe_path = os.path.abspath(julia_exe_path)
    if not os.path.exists(julia_exe_path):
        raise FileNotFoundError(f"Julia executable not found at {julia_exe_path}")

    if predictors is None:
        predictors = [c for c in df.columns if c != response]

    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    jl_script_path = f"script_{unique_id}.jl"

    df.to_csv(csv_path, index=False)

    # Format predictors as a Julia string literal list, e.g. ["x1", "x2"]
    predictors_jl = "[" + ", ".join(f'"{p}"' for p in predictors) + "]"

    # Julia script (use ASCII variable names to avoid any filesystem encoding issues)
    # The block below ensures required packages are installed if missing.
    jl_script = f"""
    import Pkg

    for pkg in ["CSV", "DataFrames"]
        try
            eval(Meta.parse("using " * pkg))
        catch
            Pkg.add(pkg)
            eval(Meta.parse("using " * pkg))
        end
    end

    using LinearAlgebra
    using Statistics

    data = CSV.read("{csv_path}", DataFrame)

    y = data[:, "{response}"]
    X = Matrix(data[:, {predictors_jl}])
    X = hcat(ones(size(X,1)), X)  # add intercept

    beta = X \\ y
    yhat = X * beta
    residuals = y - yhat

    println("Coefficients:")
    println(beta)

    println("\\nResidual standard error:")
    println(sqrt(mean(residuals.^2)))

    println("\\nR-squared:")
    println(1 - sum(residuals.^2) / sum((y .- mean(y)).^2))
    """

    # Write using explicit UTF-8 encoding to avoid errors writing non-ASCII
    with open(jl_script_path, "w", encoding='utf-8') as f:
        f.write(jl_script)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            # os.fsync may not be available on some platforms; ignore if so
            pass
    print(f"Wrote Julia script {jl_script_path} ({len(jl_script)} bytes)")

    command = [julia_exe_path, "--startup-file=no", jl_script_path]

    try:
        # Force UTF-8 decoding of subprocess output so we correctly capture Unicode
        # characters produced by Julia. We'll handle console encoding at print time.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
    except subprocess.CalledProcessError as e:
        safe_msg = getattr(e, 'stderr', str(e))
        # Use safe printing to avoid UnicodeEncodeError when writing to a
        # Windows console with a limited code page.
        print("Julia error:")
        print(safe_msg)
        raise
    finally:
        os.remove(csv_path)
        os.remove(jl_script_path)

    return result.stdout.strip().split("\n")


# Example dataset and runner (modeled after prototyping_station/r_regression.py)
if __name__ == '__main__':
    # Example dataset
    df = pd.DataFrame({
        'yN': [1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5],  # Numeric response
        'x1': [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
        'x2': [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
        'x3': [5, 8, 6, 10, 12, 14, 18, 20, 24, 30],
        'x4': [3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3],
        'x5': [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
    })

    # Models supported by this Julia runner
    all_models = {
        "ols": "yN",
    }

    independent_vars = ["x1", "x2", "x3", "x4", "x5"]

    for model_type, response_var in all_models.items():
        print(f"\n🔹 Running {model_type} model with response variable: {response_var}\n")
        try:
            output = regression(df, response_var, independent_vars, model_type)
            for line in output:
                print(line)
        except Exception as e:
            print(f"⚠️ Error in {model_type}: {e}")

        print("\n" + "="*50 + "\n")
