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
    config.optionxform = str  # Preserve case of keys
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


def load_execution_log_ini(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Execution log file not found: {filepath}")
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case of keys
    config.read(filepath, encoding="utf-8")
    sipy_info = dict(config["sipy"])
    environment = dict(config["environment"])
    for k in environment:
        if environment[k] == "True": environment[k] = True
        if environment[k] == "False": environment[k] = False
    data = {"sipy_version": sipy_info["sipy_version"], 
            "sipy_codename": sipy_info["sipy_codename"], 
            "sipy_release_date": sipy_info["sipy_release_date"],
            "environment": environment, 
            "log_generation_timestamp": dict(config["log_generation_timestamp"]), 
            "history": dict(config["history"]), 
            "result": dict(config["result"]), 
            "timestamp": dict(config["timestamp"]), 
            "system_information": dict(config["system_information"]), 
            "important_python_packages": dict(config["important_python_packages"])
            }
    return data


def load_execution_log_json(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Execution log file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    environment = raw.get("environment", {})
    for k in environment:
        if environment[k] == "True": environment[k] = True
        if environment[k] == "False": environment[k] = False
    data = {"sipy_version": raw.get("sipy_version", None), 
            "sipy_codename": raw.get("sipy_codename", None),  
            "sipy_release_date": raw.get("sipy_release_date", None), 
            "environment": environment, 
            "log_generation_timestamp": raw.get("log_generation_timestamp", {}),  
            "history": raw.get("history", {}), 
            "result": raw.get("result", {}),  
            "timestamp": raw.get("timestamp", {}), 
            "system_information": raw.get("system_information", {}), 
            "important_python_packages": raw.get("important_python_packages", {})
            }
    return data

"""
env = {
    "sipy_version": sipy_info.release_number, 
    "sipy_codename": sipy_info.release_code_name, 
    "sipy_release_date": sipy_info.release_date,
    "environment": self.environment, 
    "log_generation_timestamp": log_timestamp, 
    "history": self.history, 
    "result": self.result, 
    "timestamp": self.timestamp, 
    "system_information": libsipy.execution_log.get_system_information(self.environment), 
    "important_python_packages": libsipy.execution_log.get_package_information()
    }
"""


def _normalize_for_comparison(value):
    """
    Normalize values for comparison, handling type conversions from INI/JSON formats.
    - Converts tuples to lists (JSON doesn't preserve tuples)
    - Parses string representations of tuples/lists to actual lists
    - Leaves other types unchanged
    """
    # If it's a tuple, convert to list
    if isinstance(value, tuple):
        return list(value)
    
    # If it's a string that looks like a tuple or list, try to parse it
    if isinstance(value, str):
        value_stripped = value.strip()
        if (value_stripped.startswith('(') and value_stripped.endswith(')')) or \
           (value_stripped.startswith('[') and value_stripped.endswith(']')):
            try:
                # Use ast.literal_eval for safe evaluation
                import ast
                parsed = ast.literal_eval(value_stripped)
                # Convert tuples to lists for consistency
                if isinstance(parsed, tuple):
                    return list(parsed)
                return parsed
            except (ValueError, SyntaxError):
                # If parsing fails, keep as string
                return value
    
    return value


def compare_system(filepath):
    """
    Compare system information and important Python packages from a log file with the current system.
    
    Args:
        filepath (str): Path to the execution log file (.SLogI or .SLogJ)
    
    Returns:
        list: List of comparison output lines
    """
    results = []
    # Determine format
    if '.SLogJ' in filepath:
        data = load_execution_log_json(filepath)
    else:
        data = load_execution_log_ini(filepath)
    # Get current system information
    # Assume portable executables are in the workspace
    workspace_dir = os.path.dirname(os.path.dirname(__file__))
    environment = {
        "rscript_exe": os.path.join(workspace_dir, "portable_R", "bin", "Rscript.exe"),
        "julia_exe": os.path.join(workspace_dir, "portable_julia", "bin", "julia.exe")
    }
    current_sys = get_system_information(environment)
    current_pkg = get_package_information()
    # Compare system_information
    logged_sys = data.get("system_information", {})
    results.append("Comparing system_information:")
    for key in set(logged_sys.keys()) | set(current_sys.keys()):
        log_val = logged_sys.get(key, 'Not present')
        curr_val = current_sys.get(key, 'Not present')
        # Normalize values for comparison
        log_val_normalized = _normalize_for_comparison(log_val)
        curr_val_normalized = _normalize_for_comparison(curr_val)
        status = 'Match' if log_val_normalized == curr_val_normalized else 'Mismatch'
        results.append(f"(log file) {key} = {log_val}")
        results.append(f"(this system) {key} = {curr_val}")
        results.append(f"Status = {status}")
        results.append("")
    # Compare important_python_packages
    logged_pkg = data.get("important_python_packages", {})
    results.append("Comparing important_python_packages:")
    for key in set(logged_pkg.keys()) | set(current_pkg.keys()):
        log_val = logged_pkg.get(key, 'Not present')
        curr_val = current_pkg.get(key, 'Not present')
        # Normalize values for comparison
        log_val_normalized = _normalize_for_comparison(log_val)
        curr_val_normalized = _normalize_for_comparison(curr_val)
        status = 'Match' if log_val_normalized == curr_val_normalized else 'Mismatch'
        results.append(f"(log file) {key} = {log_val}")
        results.append(f"(this system) {key} = {curr_val}")
        results.append(f"Status = {status}")
        results.append("")
    results = "\n".join(results)
    return results
