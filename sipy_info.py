"""!
Information Regarding SiPy

Date created: 10th September 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only

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
release_number = "0.3.0"
release_code_name = "Durian"
release_date = "28 January 2023"

header = """
SiPy: Statistics in Python
Release %s (%s) dated %s
https://github.com/mauriceling/sipy
Type "copyright", "credits" or "license" for more information.
To exit this application, type "exit".
""" % (str(release_number), release_code_name, release_date)

import datetime
today = datetime.date.today()
copyright = """
Copyright (C) 2022-%s, Maurice HT Ling (on behalf of SiPy Team)
""" % str(today.year)

credits = """
SiPy Project Team
Project architect: Maurice HT Ling (mauriceling@acm.org)
Developers:
1. Nicholas TF Tan (https://github.com/NicholasTTF)
"""

citations = """"""