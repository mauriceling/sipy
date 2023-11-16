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
release_number = "0.5.0"
release_code_name = "Watermelon"
release_day = "17 November"
release_year = "2023"
release_date = " ".join([release_day, release_year])

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
Core Developers:
    1. Mathialagan Mugundhan (https://github.com/Mugu17777777)
    2. Nicholas TF Tan (https://github.com/NicholasTTF)
Contributors:
    1. Tan Zhi Hui Jensen (https://github.com/Jensen19142)
"""

citations = """"""

"""To cite SiPy in publications, use

    Nicholas TF Tan, Mugundhan Mathialagan, Jensen ZR Tan, and Maurice HT Ling. Year. SiPy - Statistics in Python. Journal Volume(Issue): StartPage–EndPage. 

A BibTeX entry for LaTeX users is

    @article{SiPy, 
        title={SiPy - Statistics in Python}, 
        volume={Volume}, 
        number={Issue}, 
        journal={Journal}, 
        author={Tan, Nicholas TF and Mathialagan, Mugundhan and Tan, Jensen ZR and Ling, Maurice HT}, 
        year={Year}, 
        pages={StartPage–EndPage}
    } 

We have invested a lot of time and effort in creating SiPy,please cite it when using it.
"""