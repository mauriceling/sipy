# Parse command-line arguments
args <- commandArgs(trailingOnly = TRUE)

# Default values
input_file <- "data_579e72a9.csv"
formula_str <- "yN ~ x1 + x2 + x3 + x4 + x5"

# Parse --inputfile and --formula arguments
for (i in seq_along(args)) {
    if (args[i] == "--inputfile" && i < length(args)) {
        input_file <- args[i + 1]
    }
    if (args[i] == "--formula" && i < length(args)) {
        formula_str <- args[i + 1]
    }
}

# Read data and fit model
if (!file.exists(input_file)) {
    stop(paste("Error: Input file not found:", input_file))
}

data <- read.csv(input_file)
model <- lm(as.formula(formula_str), data = data)
summary(model)