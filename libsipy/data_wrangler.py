"""!
libsipy (Data Wrangler): Functions to Manipulate Pandas Data Frame and Other Data Structures in SiPy.

Date created: 9th September 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only.

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
"""
import os
import sys

import pandas as pd

def flatten(nested_list):
    """!
    Function to flatten n-dimensional nested list into 1-dimensional list. For example, [1, 2, 3, [4, 5], [6, 7, [8, 9, [10, 11, 12, [13, 14, [15], [16, 17], 18]]]]] to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].

    @param nested_list: Nested list to flatten
    @type nested_list: List
    @rtype: 1-dimensional list.
    """
    if len(nested_list) == 0:
        return nested_list
    if isinstance(nested_list[0], list):
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    return nested_list[:1] + flatten(nested_list[1:])

def df_extract(df, columns="all", rtype="list"):
    """!
    Function to extract column(s) from dataframe into list(s) or a new dataframe.

    @param df: dataframe
    @type df: Pandas.dataframe object
    @param columns: Column(s) to extract - delimited by "|". Default = "all" (all columns).
    @type columns: String
    @param: rtype: Return type of extracted column(s). Default = "list".
    @type rtype: String
    """
    if columns.lower() == "all" and rtype.lower() == "list":
        return [df[col].values.tolist() for col in df]
    elif columns.lower != "all" and rtype.lower() == "list":
        columns = [x.strip() for x in columns.split("|")]
        if len(columns) == 1:
            return df[columns[0]].values.tolist()
        else:
            return [df[col].values.tolist() for col in columns]

def df_remove(df, columns):
    """!
    Function to remove column(s) from dataframe.

    @param df: dataframe
    @type df: Pandas.dataframe object
    @param columns: Column(s) to extract - delimited by "|". Default = "all" (all columns).
    @type columns: String
    @rtype: Pandas.dataframe with column(s) removed.
    """
    df = df.drop(columns=[col.strip() for col in columns.split("|")], inplace=False)
    return df

def df_add(df, data, column_name):
    """!
    Function to add a column to dataframe.

    @param df: dataframe
    @type df: Pandas.dataframe object
    @param data: List of data column to add.
    @type data: List
    @param column_name: Name of added column
    @type column_name: String
    @rtype: Pandas.dataframe with column added.
    """
    column_name = column_name.strip()
    df[column_name] = data
    return df

def df_melt(df, id_vars, var_name, value_name):
    """!
    Function to convert from wide dataframe to long dataframe.

    @param df: wide dataframe to be converted
    @type df: Pandas.dataframe object
    @param id_vars: Specifies the columns that should remain unchanged.
    @type id_vars: List
    @param var_name: Specifies the name for the new column that will contain the variable names.
    @type var_name: String
    @param value_name: Specifies the name for the new column that will contain the values.
    @type value_name: String
    @rtype: Pandas.dataframe with data in long dataframe format.
    """
    melted_df = pd.melt(df, id_vars=id_vars, var_name=var_name, value_name=value_name)
    return melted_df

def df_pivot(df, columns, values):
    """!
    Function to convert from long dataframe to wide dataframe.

    @param df: long dataframe to be converted
    @type df: Pandas.dataframe object
    @param columns: Column(s) to set as columns - delimited by "|"
    @type columns: String
    @param values: Column(s) to set as values - delimited by "|"
    @type values: String
    @rtype: Pandas.dataframe with data in wide dataframe format
    """
    # Strip whitespace and handle case sensitivity
    columns = [x.strip() for x in columns.split("|")]
    values = [x.strip() for x in values.split("|")]
    
    # Verify columns exist in dataframe
    missing_cols = [col for col in columns + values if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in dataframe: {missing_cols}")
    
    try:
        # Create sequential index for each unique value in columns
        df = df.copy()
        df['_seq'] = df.groupby(columns[0]).cumcount()
        
        # Pivot the data using the sequence as index
        pivoted_df = pd.pivot(
            data=df,
            index='_seq',
            columns=columns[0],
            values=values[0]
        )
        
        # Reset index to get rid of _seq
        pivoted_df = pivoted_df.reset_index(drop=True)
        
        return pivoted_df
    except Exception as e:
        raise ValueError(f"Pivot failed: {str(e)}\nCheck that:\n" + 
                        "1. Column names are correct (case sensitive)\n" +
                        "2. Values are numeric\n" +
                        "3. Data is in correct format\n\n" +
                        f"DataFrame columns: {list(df.columns)}")

def df_merge(dfA, dfB, on, how='inner'):
    """!
    Function to merge two dataframes.

    @param dfA: First dataframe
    @type dfA: Pandas.dataframe object
    @param dfB: Second dataframe
    @type dfB: Pandas.dataframe object
    @param on: Column(s) to merge on - delimited by "|". For cross join, this is ignored.
    @type on: String
    @param how: Type of merge to perform ('inner', 'outer', 'left', 'right', 'cross')
    @type how: String
    @rtype: Merged Pandas.dataframe
    """
    try:
        # Handle cross join separately
        if how.lower() == 'cross':
            # Create dummy key column for cross join
            dfA = dfA.copy()
            dfB = dfB.copy()
            dfA['_cross_key'] = 1
            dfB['_cross_key'] = 1
            # Perform merge and drop dummy key
            result = pd.merge(dfA, dfB, on='_cross_key', how='inner')
            return result.drop('_cross_key', axis=1)
        else:
            # For other join types, process normally
            on = [x.strip() for x in on.split("|")]
            return pd.merge(dfA, dfB, how=how, on=on)
    except Exception as e:
        raise ValueError(f"Merge failed: {str(e)}\nCheck that:\n" + 
                        "1. Column names are correct (case sensitive)\n" +
                        "2. For non-cross joins, merge columns must exist in both dataframes\n" +
                        "3. Data types are compatible\n" +
                        "4. Valid merge types are: inner, outer, left, right, cross\n\n" +
                        f"DataFrame A columns: {list(dfA.columns)}\n" +
                        f"DataFrame B columns: {list(dfB.columns)}")
