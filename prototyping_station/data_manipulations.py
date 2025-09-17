import pandas as pd

def read_csv(filepath, **kwargs):
    """Read data from CSV file"""
    return pd.read_csv(filepath, **kwargs)

def read_json(filepath, **kwargs): 
    """Read data from JSON file"""
    return pd.read_json(filepath, **kwargs)

def read_sql(query, connection, **kwargs):
    """Read data from SQL database"""
    return pd.read_sql(query, connection, **kwargs)

def read_parquet(filepath, **kwargs):
    """Read data from Parquet file"""
    return pd.read_parquet(filepath, **kwargs)

def read_hdf(filepath, key, **kwargs):
    """Read data from HDF5 file"""
    return pd.read_hdf(filepath, key, **kwargs)

import pandas as pd

def reshape_long_to_wide(df, id_vars, value_vars):
    """Convert data from long to wide format"""
    return pd.pivot(df, index=id_vars, columns=value_vars)

def reshape_wide_to_long(df, id_vars, value_vars):
    """Convert data from wide to long format"""
    return pd.melt(df, id_vars=id_vars, value_vars=value_vars)

def merge_datasets(df1, df2, how='inner', on=None):
    """Merge two datasets"""
    return pd.merge(df1, df2, how=how, on=on)

def aggregate_data(df, group_by, agg_funcs):
    """Aggregate data by groups"""
    return df.groupby(group_by).agg(agg_funcs)

def create_dummy_variables(df, columns):
    """Create dummy/indicator variables"""
    return pd.get_dummies(df, columns=columns)

import pandas as pd
import numpy as np

def check_missing_values(df):
    """Check for missing values in dataset"""
    missing = df.isnull().sum()
    percent = (df.isnull().sum()/len(df))*100
    return pd.DataFrame({'missing_count': missing, 
                        'missing_percent': percent})

def check_duplicates(df):
    """Check for duplicate records"""
    return df[df.duplicated()]

def validate_numeric_range(series, min_val=None, max_val=None):
    """Validate numeric values are within range"""
    if min_val is not None:
        below = series < min_val
    if max_val is not None:
        above = series > max_val
    return {'below_min': below.sum(), 'above_max': above.sum()}

def validate_categorical(series, valid_categories):
    """Validate categorical values"""
    invalid = ~series.isin(valid_categories)
    return series[invalid]

def detect_outliers(series, method='zscore', threshold=3):
    """Detect outliers using various methods"""
    if method == 'zscore':
        z = (series - series.mean())/series.std()
        return series[abs(z) > threshold]
    
import pandas as pd

def remove_duplicates(df, subset=None):
    """Remove duplicate records"""
    return df.drop_duplicates(subset=subset)

def fill_missing_values(df, method='mean'):
    """Fill missing values using various methods"""
    if method == 'mean':
        return df.fillna(df.mean())
    elif method == 'median':
        return df.fillna(df.median())
    elif method == 'mode':
        return df.fillna(df.mode().iloc[0])
    elif method == 'ffill':
        return df.fillna(method='ffill')
    elif method == 'bfill':
        return df.fillna(method='bfill')

def remove_outliers(series, method='zscore', threshold=3):
    """Remove outliers from data"""
    if method == 'zscore':
        z = (series - series.mean())/series.std()
        return series[abs(z) <= threshold]

def standardize_strings(series):
    """Standardize string values"""
    return series.str.strip().str.lower()

def coerce_datatypes(df, type_dict):
    """Convert columns to specified data types"""
    return df.astype(type_dict)

from libsipy.data import *

class SiPy_Shell(object):
    # ...existing code...
    
    def do_import(self, operand, kwargs):
        """Import data from various file formats"""
        if operand[0].lower() == "csv":
            self.data[operand[2]] = read_csv(operand[1], **kwargs)
        elif operand[0].lower() == "json":
            self.data[operand[2]] = read_json(operand[1], **kwargs)
        elif operand[0].lower() == "sql":
            self.data[operand[2]] = read_sql(operand[1], **kwargs)
        else:
            raise ValueError(f"Unknown format: {operand[0]}")

    def do_clean(self, operand, kwargs):
        """Clean data using various methods"""
        if operand[0].lower() == "duplicates":
            return remove_duplicates(self.data[operand[1]], **kwargs)
        elif operand[0].lower() == "missing":
            return fill_missing_values(self.data[operand[1]], **kwargs)
        else:
            raise ValueError(f"Unknown cleaning method: {operand[0]}")

    def do_validate(self, operand, kwargs):
        """Validate data quality"""
        if operand[0].lower() == "missing":
            return check_missing_values(self.data[operand[1]])
        elif operand[0].lower() == "duplicates":
            return check_duplicates(self.data[operand[1]])
        else:
            raise ValueError(f"Unknown validation method: {operand[0]}")