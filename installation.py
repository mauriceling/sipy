"""!
Environment Management for SiPy

Date created: 28th January 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only.

Bactome package is free software: you can redistribute it and/or 
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

if __name__ == "__main__":
    command = sys.argv[1]
    if command.lower() == "freeze":
        os.system("conda list --explicit > conda_sipy_environment.txt")
        os.system("pip list --format=freeze > pip_sipy_environment.txt")
    elif command.lower() == "build":
        environment = sys.argv[1]
        os.system("conda create --name %s --file conda_sipy_environment.txt" % environment)
        try:
            os.system("activate %s" % environment)
        except:
            os.system("source activate %s" % environment)
        pip_packages = open("pip_sipy_environment.txt").readlines()
        pip_packages = [x[:-1] for x in pip_packages]
        for package in pip_packages:
            trusted_hosts = "--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org"
            os.system("pip install %s %s" % (trusted_hosts, package))
    elif command.lower() == "remove":
        environment = sys.argv[2]
        os.system("conda remove --name %s --all" % environment)
