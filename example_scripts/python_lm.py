import sys
import os
import pandas as pd
import numpy as np


def parse_args(args):
    """
    Parse command-line arguments in both --key value and key=value formats.
    Returns a dictionary of parsed arguments with defaults.
    """
    params = {
        "inputfile": "",
        "response": "",
        "predictors": ""
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        # Handle key=value format
        if "=" in arg and not arg.startswith("--"):
            key, value = arg.split("=", 1)
            value = value.strip().strip('"').strip("'")
            params[key] = value
            i += 1
        # Handle --key value format
        elif arg.startswith("--"):
            key = arg[2:]  # Remove leading --
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1].strip().strip('"').strip("'")
                params[key] = value
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    return params


def main():
    # Parse command-line arguments
    params = parse_args(sys.argv[1:])
    input_file = params.get("inputfile", "")
    response_col = params.get("response", "")
    predictor_str = params.get("predictors", "")
    predictor_cols = [p.strip() for p in predictor_str.split(",")]
    
    # Normalize path (handle backslashes)
    input_file = input_file.replace("\\", "/")
    
    # Read data and validate
    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError as e:
        print(f"Error: Input file not found: {input_file}")
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Validate columns exist
    if response_col not in data.columns:
        print(f"Error: Response column '{response_col}' not found in data")
        sys.exit(1)
    
    for col in predictor_cols:
        if col not in data.columns:
            print(f"Error: Predictor column '{col}' not found in data")
            sys.exit(1)
    
    # Ordinary Least Squares (OLS)
    y = data[response_col].values
    X = data[predictor_cols].values
    
    # Add intercept (column of ones)
    X = np.column_stack([np.ones(X.shape[0]), X])
    
    # Solve: beta = (X^T X)^-1 X^T y
    # Using numpy's least squares for numerical stability
    beta, residuals_sum, _, _ = np.linalg.lstsq(X, y, rcond=None)
    
    # Calculate predictions and residuals
    yhat = X @ beta
    residuals = y - yhat
    
    # Calculate metrics
    ss_total = np.sum((y - np.mean(y))**2)
    ss_residual = np.sum(residuals**2)
    r_squared = 1 - (ss_residual / ss_total)
    rmse = np.sqrt(np.mean(residuals**2))
    
    # Print results
    print("OLS Regression Results:")
    print(f"Response: {response_col}")
    print(f"Predictors: {', '.join(predictor_cols)}")
    print("Coefficients:")
    print(beta)
    print(f"\nRMSE: {rmse}")
    print(f"R-squared: {r_squared}")


if __name__ == "__main__":
    main()
