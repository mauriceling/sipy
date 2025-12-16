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

def regression(df, response, predictors=None, model_type="ols", julia_exe_path="/usr/bin/julia"):
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

    # Julia script
    jl_script = f"""
    using CSV
    using DataFrames
    using LinearAlgebra
    using Statistics

    data = CSV.read("{csv_path}", DataFrame)

    y = data[:, "{response}"]
    X = data[:, {predictors}]
    X = hcat(ones(size(X,1)), Matrix(X))  # add intercept

    β = X \\ y
    ŷ = X * β
    residuals = y - ŷ

    println("Coefficients:")
    println(β)

    println("\\nResidual standard error:")
    println(sqrt(mean(residuals.^2)))

    println("\\nR-squared:")
    println(1 - sum(residuals.^2) / sum((y .- mean(y)).^2))
    """

    with open(jl_script_path, "w") as f:
        f.write(jl_script)

    command = [julia_exe_path, "--startup-file=no", jl_script_path]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Julia error:")
        print(e.stderr)
        raise
    finally:
        os.remove(csv_path)
        os.remove(jl_script_path)

    return result.stdout.strip().split("\n")
