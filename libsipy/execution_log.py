'''!
libsipy (Execution Log): Functions to Process Execution Logs

Date created: 25th April 2026

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
'''
import configparser
import json
import os
import subprocess
import sys


def get_system_information(environment):
    import platform
    system_information = {}
    system_information["OS_System"] = platform.system()
    system_information["OS_Release"] = platform.release()
    system_information["OS_Version"] = platform.version()
    system_information["OS_Machine"] = platform.machine()
    system_information["OS_Processor"] = platform.processor()
    system_information["Python_Version"] = platform.python_version()
    system_information["Python_Build"] = platform.python_build()
    system_information["Python_Compiler"] = platform.python_compiler()
    system_information["CPU_Count"] = os.cpu_count()
    system_information["Platform"] = sys.platform
    try:
        r_version = subprocess.run([environment["rscript_exe"], "-e", "cat(R.version.string)"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception as e:
        r_version = f"R version not available ({e})"
    try:
        julia_version = subprocess.run([environment["julia_exe"], "-e", "print(VERSION)"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception as e:
        julia_version = f"Julia version not available ({e})"
    system_information["R_Version"] = r_version
    system_information["Julia_Version"] = julia_version
    return system_information


def get_package_information():
    from importlib.metadata import distributions
    packages = {}
    for dist in distributions():
        name = dist.metadata["Name"]
        version = dist.version
        if name in ["numpy", "scipy", "pandas", "statsmodels", "scikit-learn", "xarray", "pingouin", "threadpoolctl", "libblas", "liblapack", "libgomp", "llvm-openmp", "python_abi"]:
            packages[name] = version
    return packages


def save_execution_log_json(filepath, workspace_dict):
    """Save execution log to JSON file (human-readable, cross-version safe)."""
    to_store = {
        "sipy_version": workspace_dict.get("sipy_version", 0),
        "sipy_codename": workspace_dict.get("sipy_codename", 0),
        "sipy_release_date": workspace_dict.get("sipy_release_date", 0),
        "environment": workspace_dict.get("environment", {}),
        "log_generation_timestamp": workspace_dict.get("log_generation_timestamp", {}),
        "history": workspace_dict.get("history", {}),
        "result": workspace_dict.get("result", {}),
        "timestamp": workspace_dict.get("timestamp", {}),
        "system_information": workspace_dict.get("system_information", {}),
        "important_python_packages": workspace_dict.get("important_python_packages", {})
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_store, f, indent=2)


def save_execution_log_ini(filepath, workspace_dict):
    config = configparser.ConfigParser()
    config["sipy"] = {
        "sipy_version": str(workspace_dict.get("sipy_version", 0)),
        "sipy_codename": str(workspace_dict.get("sipy_codename", 0)),
        "sipy_release_date": str(workspace_dict.get("sipy_release_date", 0))
    }
    config["environment"] = {k: str(v) for k, v in workspace_dict.get("environment", {}).items()}
    config["log_generation_timestamp"] = {k: str(v) for k, v in workspace_dict.get("log_generation_timestamp", {}).items()}
    config["history"] = {k: str(v) for k, v in workspace_dict.get("history", {}).items()}
    config["result"] = {k: str(v) for k, v in workspace_dict.get("result", {}).items()}
    config["timestamp"] = {k: str(v) for k, v in workspace_dict.get("timestamp", {}).items()}
    config["system_information"] = {k: str(v) for k, v in workspace_dict.get("system_information", {}).items()}
    config["important_python_packages"] = {k: str(v) for k, v in workspace_dict.get("important_python_packages", {}).items()}
    with open(filepath, "w", encoding="utf-8") as f:
        config.write(f)

