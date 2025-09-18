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
"python installation.py pyinstaller windows" to generate a one-directory executable GUI and CLI/CUI together based on sipy_windows.spec for Windows operating system.
"python installation.py remove <environment name>" to remove environment.
"python installation.py update" to update environment from generated conda and pip environment files.
"python installation.py update_all" to update entire environment.
"python installation.py update_core" to update essential and its dependent packages in the environment.
"python installation.py update_conda_pip" to update conda and pip.

Important: Turn off Dropbox / OneDrive synchronizations before generating executables or it will give you errors.
        ''')

data = {"conda_env": "conda_sipy_environment.txt",
        "pip_env": "pip_sipy_environment.txt",
        "conda_packageList": "openpyxl pandas scipy pingouin pyinstaller scikit-learn statsmodels",
        "pip_packageList": "fire fitter FreeSimpleGUI",
        "CLI_scriptfile": "sipy_CLI.py",
        "GUI_scriptfile": "sipy.py",
        "folder_spec": "sipy_windows.spec"}

def build(environment):
    os.system("conda create --name %s --file %s" % (environment, data["conda_env"]))
    try:
        os.system("activate %s" % environment)
    except:
        os.system("source activate %s" % environment)
    pip_packages = open(data["pip_env"]).readlines()
    pip_packages = [x[:-1] for x in pip_packages]
    for package in pip_packages:
        os.system("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org %s" % (package))

def create_env(environment):
    os.system("conda create --name %s -c conda-forge %s" % (environment, data["conda_packageList"]))
    try:
        os.system("activate %s" % environment)
    except:
        os.system("source activate %s" % environment)
    os.system("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org %s" % data["pip_packageList"])

def freeze():
    os.system("conda list --explicit > %s" % data["conda_env"])
    os.system("pip list --format=freeze > %s" % data["pip_env"])

def update(): 
    os.system("conda update -n sipy --file %s" % data["conda_env"])
    os.system("pip install --upgrade --force-reinstall -r %s" % data["pip_env"])

def update_all():
    os.system("conda update -n base -c defaults conda")
    os.system("python -m pip install --upgrade pip")
    os.system("conda update -n sipy --update-all")

def update_core():
    os.system("conda update -n sipy  %s" % data["conda_packageList"])
    os.system("pip install --upgrade --force-reinstall %s" % data["pip_packageList"])

def update_conda_pip():
    os.system("conda update -n base conda")
    os.system("python -m pip install --upgrade pip")

if __name__ == "__main__":
    command = sys.argv[1]
    if command.lower() == "help": help()
    elif command.lower() == "create_env": create_env(sys.argv[2])
    elif command.lower() == "freeze": freeze()
    elif command.lower() == "build": build(sys.argv[2])
    elif command.lower() == "remove":
        environment = sys.argv[2]
        os.system("conda remove --name %s --all" % environment)
    elif command.lower() == "update": update()
    elif command.lower() == "update_all": update_all()
    elif command.lower() == "update_core": update_core()
    elif command.lower() == "update_conda_pip": update_conda_pip()
