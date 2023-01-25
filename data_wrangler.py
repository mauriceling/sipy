"""!
Data Wrangler for SiPy

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

import pandas

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
