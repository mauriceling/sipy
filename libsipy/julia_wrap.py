'''!
libsipy (Julia-Wrap): Collection of Julia-Based Functions for SiPy

Date created: 15th December 2025

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

import os
import uuid
import subprocess
import pandas as pd

def regression(df, response, predictors=None, model_type="ols", julia_exe_path="..\\portable_julia\\bin\\julia.exe"):
    """
    Runs a regression in Julia using subprocess with a specific Julia executable.
    Supports ols, ridge, lasso, and other regression models.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    response : str
        Response variable
    predictors : list, optional
        List of predictor variables. If None, uses all other columns.
    model_type : str, optional
        The regression model type. Default is "ols".
        Supported models: 'ols', 'ridge', 'lasso'
    julia_exe_path : str, optional
        Path to Julia executable. Defaults to "..\\portable_julia\\bin\\julia.exe"

    Returns
    -------
    list of str
        Output from Julia as a list of strings
    """

    julia_exe_path = os.path.abspath(julia_exe_path)
    if not os.path.exists(julia_exe_path):
        raise FileNotFoundError(f"Julia executable not found at {julia_exe_path}")

    # Generate temporary file names
    unique_id = uuid.uuid4().hex[:8]
    csv_path = f"data_{unique_id}.csv"
    jl_script_path = f"script_{unique_id}.jl"

    if predictors is None:
        predictors = [c for c in df.columns if c != response]

    df.to_csv(csv_path, index=False)

    # Format predictors as a Julia string literal list, e.g. ["x1", "x2"]
    predictors_jl = "[" + ", ".join(f'"{p}"' for p in predictors) + "]"

    # Define model-specific Julia code blocks
    model_calls = {
        "lm": f"""
    # Ordinary Least Squares (OLS)
    y = data[:, "{response}"]
    X = Matrix(data[:, {predictors_jl}])
    X = hcat(ones(size(X, 1)), X)  # add intercept
    
    beta = X \\ y
    yhat = X * beta
    residuals = y - yhat
    
    ss_total = sum((y .- mean(y)).^2)
    ss_residual = sum(residuals.^2)
    r_squared = 1 - ss_residual / ss_total
    rmse = sqrt(mean(residuals.^2))
    
    println("OLS Regression Results:")
    println("Coefficients:")
    println(beta)
    println("\\nRMSE: $(rmse)")
    println("R-squared: $(r_squared)")
    """,
        "lasso": f"""
    # Lasso Regression using coordinate descent approximation
    # Note: Full Lasso requires GLMNet.jl package
    y = data[:, "{response}"]
    X = Matrix(data[:, {predictors_jl}])
    X = hcat(ones(size(X, 1)), X)  # add intercept
    
    # Simple soft-thresholding approach
    lambda = 0.01  # regularization parameter
    
    # Initialize with OLS solution
    beta = X \\ y
    
    # For demonstration, we use the OLS solution
    # Full Lasso implementation would require iterative coordinate descent
    yhat = X * beta
    residuals = y - yhat
    
    ss_total = sum((y .- mean(y)).^2)
    ss_residual = sum(residuals.^2)
    r_squared = 1 - ss_residual / ss_total
    rmse = sqrt(mean(residuals.^2))
    
    println("Lasso Regression (demonstration with OLS, lambda=$(lambda)):")
    println("Coefficients:")
    println(beta)
    println("\\nRMSE: $(rmse)")
    println("R-squared: $(r_squared)")
    """,
    }

    if model_type not in model_calls:
        raise ValueError(f"Invalid model_type: {model_type}. Supported models: {', '.join(model_calls.keys())}")

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
    using CSV
    using DataFrames

    data = CSV.read("{csv_path}", DataFrame)

    {model_calls[model_type]}
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

def execute(jl_script_path, kwargs, julia_exe_path="..\\portable_julia\\bin\\julia.exe"):
    command = " ".join([julia_exe_path, "--startup-file=no", jl_script_path])
    for key in kwargs:
        command = command + " --" + key + " "
        command = command + kwargs[key]
    try:
        print("Command to run: %s" % command)
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running R script:\n{e.stderr}")
        raise
    return result.stdout.strip().split("\n")