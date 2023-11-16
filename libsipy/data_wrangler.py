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
