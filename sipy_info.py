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
draft = False

release_number = "0.8.0"
release_code_name = "Mango Yoghurt Cake"
release_day = "09 January"
release_year = "2026"
release_date = " ".join([release_day, release_year])

if draft: release_number = "(Under Development After) " + release_number

header = """
SiPy - Statistics in Python
Release %s (%s) dated %s
https://github.com/mauriceling/sipy
Type "copyright", "credits" or "license" for more information.
Type "citation" for information on how to cite SiPy or SiPy packages in publications.
To exit this application, type "exit".
""" % (str(release_number), release_code_name, release_date)

copyright = """Copyright (C) 2022-%s, Maurice HT Ling (on behalf of SiPy Team)
""" % str(release_year)

credits = """SiPy Project Team
Project architect: Maurice HT Ling (https://mauriceling.github.io; mauriceling@acm.org)
Current and Past Developers:
    2. Mathialagan Mugundhan (https://github.com/Mugu17777777)
    1. Nicholas TF Tan (https://github.com/NicholasTTF)
Current and Past Contributors:
    5. Alexander Y Tang
    4. Tiantong Liu
    3. Rick YH Tan
    2. Bryan JH Sim
    1. Jensen ZH Tan (https://github.com/Jensen19142)
"""

citations = """
To cite SiPy in publications, use

    Tan, NTF, Mugundhan, M, Liu, T, Tan, RYH, Tang, AY, Sim, BJH, Tan, JZH, Ling, MHT. 2025. SiPy – Bringing Python and R to the End-User in a Plugin-Extensible System. Medicon Medical Sciences 8(6): 32-41. https://doi.org/10.55162/MCMS.08.295

We have invested a lot of time and effort in creating SiPy,please cite it when using it.
"""