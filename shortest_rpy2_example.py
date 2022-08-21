import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from rpy2 import robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()
R = ro.r

df = pd.DataFrame({'x': [1,2,3,4,5], 
                   'y': [2,1,3,5,4]})

M = R.lm('y~x', data=df)
print(R.summary(M).rx2('coefficients'))