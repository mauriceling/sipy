# Creating a combined ANOVA + survival case study dataset with 1000 patients
import numpy as np
import pandas as pd
from pathlib import Path
rng = np.random.default_rng(42)

n = 1000
centers = 20

ids = np.arange(1, n+1)
center = rng.integers(1, centers+1, size=n)
arm = rng.choice(['Drug', 'Control'], size=n, p=[0.5,0.5])
age = rng.normal(60, 10, size=n).round(1)
sex = rng.choice(['M','F'], size=n)
stage = rng.choice(['I','II','III'], size=n, p=[0.4,0.4,0.2])

# Baseline biomarker (continuous) and QoL score for ANOVA
biomarker_baseline = rng.normal(50, 10, size=n).round(2)
qol_baseline = rng.normal(70, 12, size=n).round(1)  # quality of life score (0-100)

# Simulate treatment effects on biomarker at 3 and 6 months (for ANOVA repeated measures)
# Drug reduces biomarker moderately; Control slight change
effect_drug_3m = -5.0  # mean change at 3 months
effect_drug_6m = -8.0  # mean change at 6 months
effect_control_3m = -1.0
effect_control_6m = -0.5

biomarker_3m = []
biomarker_6m = []
qol_6m = []
for i in range(n):
    if arm[i] == 'Drug':
        b3 = biomarker_baseline[i] + rng.normal(effect_drug_3m, 3.0)
        b6 = biomarker_baseline[i] + rng.normal(effect_drug_6m, 4.0)
        q6 = qol_baseline[i] + rng.normal(4.0, 5.0)
    else:
        b3 = biomarker_baseline[i] + rng.normal(effect_control_3m, 3.0)
        b6 = biomarker_baseline[i] + rng.normal(effect_control_6m, 4.0)
        q6 = qol_baseline[i] + rng.normal(1.0, 5.0)
    biomarker_3m.append(round(b3,2))
    biomarker_6m.append(round(b6,2))
    qol_6m.append(round(q6,1))

biomarker_3m = np.array(biomarker_3m)
biomarker_6m = np.array(biomarker_6m)
qol_6m = np.array(qol_6m)

# Time-to-event (months) simulation using Weibull baseline with covariate effects
shape = 1.2
base_scale = 24.0  # baseline scale parameter (months)
# coefficients
beta_arm = -0.4  # treatment reduces hazard
beta_age = 0.02  # older increases hazard
beta_stage = {'I':0.0,'II':0.3,'III':0.6}
beta_biomarker = -0.01  # higher biomarker somewhat protective here (example)
# center frailty gamma
theta = 0.3
frailty_center = rng.gamma(shape=1/theta, scale=theta, size=centers)  # mean 1
frailty = frailty_center[center-1]

linpred = (beta_arm * (arm=='Drug').astype(float) +
           beta_age * ((age-60)/10.0) +
           np.array([beta_stage[s] for s in stage]) +
           beta_biomarker * ((biomarker_baseline-50)/10.0) +
           np.log(frailty))

u = rng.random(size=n)
scale = base_scale * np.exp(-linpred)  # scale adjusted
time_event = scale * (-np.log(u))**(1/shape)
# administrative censoring at 36 months + random loss to follow-up
censor = rng.uniform(12, 48, size=n)
time_months = np.minimum(time_event, censor).round(2)
status = (time_event <= censor).astype(int)

# competing risks: if event occurred, assign cause 1 (progression) with p=0.75 else cause 2 (toxicity)
cause = np.zeros(n, dtype=int)
idx_event = np.where(status==1)[0]
cause[idx_event] = rng.choice([1,2], size=len(idx_event), p=[0.75,0.25])

# time-dependent covariate: simple binary indicator if biomarker dropped >5 at 3 months
treatment_td = ((biomarker_3m - biomarker_baseline) < -5).astype(int)  # 1 if dropped >5

# Package into DataFrame
df = pd.DataFrame({
    "id": ids,                                  # ID
    "center": center,                           # Center (20 centers)
    "arm": arm,                                 # Arm {Drug|Control}
    "age": age.round(1),                        # Age
    "sex": sex,                                 # Gender {M|F}
    "stage": stage,                             # Stage {I|II|III}
    "biomarker_baseline": biomarker_baseline,   # Biomarker at detection
    "biomarker_3m": biomarker_3m,               # Biomarker after 3 months
    "biomarker_6m": biomarker_6m,               # Biomarker after 6 months
    "qol_baseline": qol_baseline,               # Quality of Life at detection
    "qol_6m": qol_6m,                           # Quality of Life after 3 months
    "time_months": time_months,                 # Survival time
    "status": status,                           # Event indicator
    "cause": cause,                             # Cause (1=primary event, 2=competing event)
    "treatment_td": treatment_td                # Time-dependent indicator
})

# Save CSV
out_path = Path("survival_dataset.csv")
df.to_csv(out_path, index=False)
