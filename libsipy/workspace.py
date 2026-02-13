'''!
libsipy (Workspace): Functions to Save and Load Workspace

Date created: 16th September 2025

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
import pandas as pd
import os

version = "SiPy-Workspace-1.0"

# -----------------------------
# Internal Helpers
# -----------------------------
def _serialize_data_json(data_dict):
    """Convert Pandas objects into JSON-serializable form."""
    serialized = {}
    for name, obj in data_dict.items():
        if isinstance(obj, pd.DataFrame):
            serialized[name] = {
                "__type__": "DataFrame",
                "value": obj.to_json(orient="split")
            }
        elif isinstance(obj, pd.Series):
            serialized[name] = {
                "__type__": "Series",
                "value": obj.to_json(orient="split")
            }
        else:
            raise TypeError(f"Unsupported type {type(obj)} for {name}")
    return serialized

def _deserialize_data_json(data_dict):
    """Reconstruct Pandas objects from JSON-serialized form."""
    deserialized = {}
    for name, obj in data_dict.items():
        if obj["__type__"] == "DataFrame":
            deserialized[name] = pd.read_json(obj["value"], orient="split")
        elif obj["__type__"] == "Series":
            deserialized[name] = pd.read_json(obj["value"], orient="split", typ="series")
        else:
            raise ValueError(f"Unsupported type {obj['__type__']} for {name}")
    return deserialized


# -----------------------------
# JSON Save / Load
# -----------------------------
def save_execution_log_json(filepath, workspace_dict):
    """Save execution log to JSON file (human-readable, cross-version safe)."""
    to_store = {
        "sipy_version": workspace_dict.get("sipy_version", 0),
        "sipy_codename": workspace_dict.get("sipy_codename", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "result": workspace_dict.get("result", {}),
        "timestamp": workspace_dict.get("timestamp", {}),
        "system_information": workspace_dict.get("system_information", {}),
        "python_packages": workspace_dict.get("python_packages", {}),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_store, f, indent=2)

def save_workspace_json(filepath, workspace_dict):
    """Save workspace to JSON file (human-readable, cross-version safe)."""
    to_store = {
        "version": version,
        "count": workspace_dict.get("count", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "data": _serialize_data_json(workspace_dict.get("data", {})),
        "result": workspace_dict.get("result", {}),
        "timestamp": workspace_dict.get("timestamp", {})
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_store, f, indent=2)

def load_workspace_json(filepath):
    """Load workspace from JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Workspace file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    environment = raw.get("environment", {})
    for k in environment:
        if environment[k] == "True": environment[k] = True
        if environment[k] == "False": environment[k] = False

    workspace = {
        "count": raw.get("count", 0),
        "environment": environment,
        "history": raw.get("history", {}),
        "data": _deserialize_data_json(raw.get("data", {})),
        "result": raw.get("result", {}),
        "timestamp": raw.get("timestamp", {})
    }

    return workspace

# -----------------------------
# INI Save / Load
# -----------------------------
def save_execution_log_ini(filepath, workspace_dict):
    config = configparser.ConfigParser()

    # Metadata
    config["sipy"] = {
        "sipy_version": str(workspace_dict.get("sipy_version", 0)),
        "sipy_codename": str(workspace_dict.get("sipy_codename", 0))
    }

    # Environment, history, result, timestamp — all strings
    config["environment"] = {k: str(v) for k, v in workspace_dict.get("environment", {}).items()}
    config["history"] = {k: str(v) for k, v in workspace_dict.get("history", {}).items()}
    config["result"] = {k: str(v) for k, v in workspace_dict.get("result", {}).items()}
    config["timestamp"] = {k: str(v) for k, v in workspace_dict.get("timestamp", {}).items()}
    config["system_information"] = {k: str(v) for k, v in workspace_dict.get("system_information", {}).items()}
    config["python_packages"] = {k: str(v) for k, v in workspace_dict.get("python_packages", {}).items()}

    # Write to disk
    with open(filepath, "w", encoding="utf-8") as f:
        config.write(f)

def save_workspace_ini(filepath, workspace_dict):
    config = configparser.ConfigParser()

    # Metadata
    config["meta"] = {
        "version": version,
        "count": str(workspace_dict.get("count", 0))
    }

    # Environment, history, result, timestamp — all strings
    config["environment"] = {k: str(v) for k, v in workspace_dict.get("environment", {}).items()}
    config["history"] = {k: str(v) for k, v in workspace_dict.get("history", {}).items()}
    config["result"] = {k: str(v) for k, v in workspace_dict.get("result", {}).items()}
    config["timestamp"] = {k: str(v) for k, v in workspace_dict.get("timestamp", {}).items()}

    # Data (Series + DataFrames → tagged JSON)
    config["data"] = {}
    for k, v in workspace_dict.get("data", {}).items():
        if isinstance(v, pd.Series):
            payload = {"__type__": "series", "data": v.to_dict()}
        elif isinstance(v, pd.DataFrame):
            payload = {"__type__": "dataframe", "data": v.to_dict(orient="split")}
        else:
            payload = {"__type__": "raw", "data": v}
        config["data"][k] = json.dumps(payload)

    # Write to disk
    with open(filepath, "w", encoding="utf-8") as f:
        config.write(f)


def load_workspace_ini(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Workspace file not found: {filepath}")

    config = configparser.ConfigParser()
    config.read(filepath, encoding="utf-8")

    data = {}
    for k, v in config["data"].items():
        try:
            payload = json.loads(v)
            t = payload.get("__type__")
            if t == "series":
                data[k] = pd.Series(payload["data"])
            elif t == "dataframe":
                data[k] = pd.DataFrame(**payload["data"])
            else:
                data[k] = payload.get("data", v)
        except Exception:
            data[k] = v  # fallback: keep raw string

    environment = dict(config["environment"])
    for k in environment:
        if environment[k] == "True": environment[k] = True
        if environment[k] == "False": environment[k] = False

    return {
        "count": int(config["meta"].get("count", 0)),
        "environment": environment,
        "history": dict(config["history"]),
        "result": dict(config["result"]),
        "timestamp": dict(config["timestamp"]),
        "data": data
    }
