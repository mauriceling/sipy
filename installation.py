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

def help():
    print('''
"python installation.py build <environment name>" to build new environment from generated conda and pip environment files.
"python installation.py create_env <environment name>" to build new environment from essential packages.
"python installation.py freeze" to generate conda and pip environment files.
"python installation.py help" to print this help text. 
"python installation.py pyinstaller onedir" to generate a one-directory executable.
"python installation.py pyinstaller onefile" to generate a one-directory executable.
"python installation.py remove <environment name>" to remove environment.
        ''')

def build(environment):
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

def create_env(environment):
    packageList = "openpyxl pandas scipy pingouin pyinstaller scikit-learn statsmodels"
    os.system("conda create --name %s -c conda-forge %s" % (environment, packageList))
    try:
        os.system("activate %s" % environment)
    except:
        os.system("source activate %s" % environment)
    os.system("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fire")

def freeze():
    os.system("conda list --explicit > conda_sipy_environment.txt")
    os.system("pip list --format=freeze > pip_sipy_environment.txt")

def pyinstaller(option="onefile"):
    scriptfile = os.sep.join([os.getcwd(), "sipy.py"])
    iconfile = os.sep.join([os.getcwd(), "images", "sipy_icon.ico"])
    cmdline = '''pyinstaller --noconfirm --%s --console --icon "%s" "%s"''' % (option, iconfile, scriptfile)
    print(cmdline)
    os.system(cmdline)

if __name__ == "__main__":
    command = sys.argv[1]
    if command.lower() == "help": help()
    elif command.lower() == "create_env": create_env(sys.argv[2])
    elif command.lower() == "freeze": freeze()
    elif command.lower() == "build": build(sys.argv[2])
    elif command.lower() == "remove":
        environment = sys.argv[2]
        os.system("conda remove --name %s --all" % environment)
    elif command.lower() == "pyinstaller": pyinstaller(sys.argv[2].lower())
