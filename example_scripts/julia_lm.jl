import Pkg

for pkg in ("CSV", "DataFrames")
    try
        @eval using $(Symbol(pkg))
    catch
        Pkg.add(pkg)
        @eval using $(Symbol(pkg))
    end
end

using LinearAlgebra
using Statistics
using CSV
using DataFrames

function main()
    # Parse command-line arguments
    args = ARGS
    input_file = "data_86e8b058.csv"
    response_col = "yN"
    predictor_cols = ["x1", "x2", "x3", "x4", "x5"]

    idx = 1
    while idx <= length(args)
        if args[idx] == "--inputfile" && idx < length(args)
            input_file = args[idx + 1]
            idx += 2
        elseif args[idx] == "--response" && idx < length(args)
            response_col = args[idx + 1]
            idx += 2
        elseif args[idx] == "--predictors" && idx < length(args)
            # Parse comma-separated predictor list
            predictor_cols = split(args[idx + 1], ",")
            predictor_cols = [strip(p) for p in predictor_cols]
            idx += 2
        else
            idx += 1
        end
    end

    # Read data and validate
    if !isfile(input_file)
        error("Error: Input file not found: $input_file")
    end

    data = CSV.read(input_file, DataFrame)

    # Validate columns exist
    if !(response_col in names(data))
        error("Response column '$response_col' not found in data")
    end
    for col in predictor_cols
        if !(col in names(data))
            error("Predictor column '$col' not found in data")
        end
    end

    # Ordinary Least Squares (OLS)
    y = data[:, response_col]
    X = Matrix(data[:, predictor_cols])
    X = hcat(ones(size(X, 1)), X)  # add intercept

    beta = X \ y
    yhat = X * beta
    residuals = y - yhat

    ss_total = sum((y .- mean(y)).^2)
    ss_residual = sum(residuals.^2)
    r_squared = 1 - ss_residual / ss_total
    rmse = sqrt(mean(residuals.^2))

    println("OLS Regression Results:")
    println("Response: $response_col")
    println("Predictors: $(join(predictor_cols, ", "))")
    println("Coefficients:")
    println(beta)
    println("\nRMSE: $(rmse)")
    println("R-squared: $(r_squared)")
end

main()

