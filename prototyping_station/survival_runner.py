import pandas as pd
from r_survival import survival_analysis  # adjust import if needed

# ----------------------------------------------------
# Load dataset
# ----------------------------------------------------
df = pd.read_csv("survival_dataset.csv")

print("Dataset preview:")
print(df.head())

# ----------------------------------------------------
# Nonparametric methods
# ----------------------------------------------------

print("\n--- Kaplan–Meier estimator ---")
print("Q: What are the survival curves for Drug vs Control arms?")
survival_analysis(
    method="kaplan-meier",
    df=df,
    time="time",
    event="status",
    group="treatment",
    plots="survival"
)

print("\n--- Nelson–Aalen estimator ---")
print("Q: What is the cumulative hazard over time for the two arms?")
survival_analysis(
    method="nelson-aalen",
    df=df,
    time="time",
    event="status",
    group="treatment",
    plots="survival"
)

print("\n--- Log-rank test ---")
print("Q: Is there a significant difference in survival between Drug and Control?")
survival_analysis(
    method="log-rank",
    df=df,
    time="time",
    event="status",
    group="treatment"
)

# ----------------------------------------------------
# Semi-parametric methods
# ----------------------------------------------------

print("\n--- Cox Proportional Hazards model ---")
print("Q: Does the treatment arm predict survival after adjusting for covariates?")
survival_analysis(
    method="cox",
    df=df,
    time="time",
    event="status",
    covariates=["treatment", "age", "sex"]
)

print("\n--- Stratified Cox model ---")
print("Q: After stratifying by stage, is there still a treatment effect?")
survival_analysis(
    method="stratified-cox",
    df=df,
    time="time",
    event="status",
    covariates=["treatment"],
    strata="stage"
)

print("\n--- Time-dependent Cox model ---")
print("Q: Does the effect of treatment vary over time?")
if "treatment_td" in df.columns:
    survival_analysis(
        method="time-dependent-cox",
        df=df,
        time="time",
        event="status",
        covariates=["treatment_td", "age", "sex"]
    )
else:
    print("⚠️ Skipping time-dependent Cox — no 'treatment_td' column found.")

print("\n--- Cox model with interaction terms ---")
print("Q: Is there an interaction between treatment and age on survival?")
survival_analysis(
    method="cox-interaction",
    df=df,
    time="time",
    event="status",
    covariates=["treatment", "age", "treatment:age"]
)

print("\n--- Frailty Cox model ---")
print("Q: Accounting for center as a random effect, does treatment remain significant?")
if "center" in df.columns:
    survival_analysis(
        method="frailty-cox",
        df=df,
        time="time",
        event="status",
        covariates=["treatment", "age", "sex"],
        cluster="center"
    )
else:
    print("⚠️ Skipping frailty Cox — no 'center' column found.")

# ----------------------------------------------------
# Parametric models
# ----------------------------------------------------

print("\n--- Weibull AFT model ---")
print("Q: How does treatment arm affect survival time under a Weibull distribution?")
survival_analysis(
    method="aft",
    df=df,
    time="time",
    event="status",
    covariates=["treatment", "age", "sex"],
    dist="weibull"
)

print("\n--- Exponential AFT model ---")
print("Q: Is survival time consistently affected by treatment under an exponential model?")
survival_analysis(
    method="exponential-aft",
    df=df,
    time="time",
    event="status",
    covariates=["treatment", "age", "sex"],
    dist="exponential"
)

# ----------------------------------------------------
# Interval-censored models (requires L and R columns)
# ----------------------------------------------------

if {"L", "R"}.issubset(df.columns):

    print("\n--- Interval-censored Log-logistic AFT ---")
    print("Q: How does treatment affect survival when some times are interval-censored?")
    survival_analysis(
        method="interval-aft",
        df=df,
        L="L",
        R="R",
        covariates=["treatment", "age", "sex"],
        dist="loglogistic"
    )

    print("\n--- Interval-censored Weibull parametric model ---")
    print("Q: What are the parametric estimates for interval-censored data?")
    survival_analysis(
        method="interval-par",
        df=df,
        L="L",
        R="R",
        covariates=["treatment", "age", "sex"],
        dist="weibull"
    )

    print("\n--- Interval-censored Semiparametric model ---")
    print("Q: What is the smoothed survival estimate for interval-censored patients?")
    survival_analysis(
        method="interval-sp",
        df=df,
        L="L",
        R="R",
        covariates=["treatment"]
    )

    print("\n--- Interval-censored Nonparametric model ---")
    print("Q: What is the empirical survival curve under interval censoring?")
    survival_analysis(
        method="interval-np",
        df=df,
        L="L",
        R="R"
    )

else:
    print("⚠️ Interval-censored models skipped — no 'L' and 'R' columns found.")

print("\n✅ All case study analyses complete.")
