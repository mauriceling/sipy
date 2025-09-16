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

import json
import pandas as pd
import os

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
def _save_json(filepath, workspace_dict):
    to_store = {
        "count": workspace_dict.get("count", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "data": _serialize_data_json(workspace_dict.get("data", {})),
        "result": workspace_dict.get("result", {})
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_store, f, indent=2)

def _load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return {
        "count": raw.get("count", 0),
        "environment": raw.get("environment", {}),
        "history": raw.get("history", {}),
        "data": _deserialize_data_json(raw.get("data", {})),
        "result": raw.get("result", {})
    }


# -----------------------------
# HDF5 Save / Load
# -----------------------------
def _save_hdf5(filepath, workspace_dict):
    metadata = {
        "count": workspace_dict.get("count", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "result": workspace_dict.get("result", {})
    }

    store = pd.HDFStore(filepath, mode="w")
    try:
        store.put("metadata", pd.Series({"json": json.dumps(metadata)}))

        for name, obj in workspace_dict.get("data", {}).items():
            if isinstance(obj, pd.DataFrame):
                store.put(f"data/{name}", obj)
            elif isinstance(obj, pd.Series):
                store.put(f"data/{name}", obj.to_frame(name="value"))
            else:
                raise TypeError(f"Unsupported type {type(obj)} for {name}")
    finally:
        store.close()

def _load_hdf5(filepath):
    store = pd.HDFStore(filepath, mode="r")
    try:
        metadata_json = store["metadata"]["json"].iloc[0]
        metadata = json.loads(metadata_json)

        data = {}
        for key in store.keys():
            if key.startswith("/data/"):
                name = key.split("/")[-1]
                obj = store[key]
                if isinstance(obj, pd.DataFrame) and obj.shape[1] == 1 and "value" in obj.columns:
                    data[name] = obj["value"]  # restore Series
                else:
                    data[name] = obj

        return {
            "count": metadata.get("count", 0),
            "environment": metadata.get("environment", {}),
            "history": metadata.get("history", {}),
            "result": metadata.get("result", {}),
            "data": data
        }
    finally:
        store.close()


# -----------------------------
# JSON Save / Load
# -----------------------------
def save_workspace_json(filepath, workspace_dict):
    """Save workspace to JSON file (human-readable, cross-version safe)."""
    to_store = {
        "count": workspace_dict.get("count", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "data": _serialize_data_json(workspace_dict.get("data", {})),
        "result": workspace_dict.get("result", {})
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_store, f, indent=2)

def load_workspace_json(filepath):
    """Load workspace from JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Workspace file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    workspace = {
        "count": raw.get("count", 0),
        "environment": raw.get("environment", {}),
        "history": raw.get("history", {}),
        "data": _deserialize_data_json(raw.get("data", {})),
        "result": raw.get("result", {})
    }

    return workspace


# -----------------------------
# HDF5 Save / Load
# -----------------------------
def save_workspace_hdf5(filepath, workspace_dict):
    """Save workspace to HDF5 (efficient for large datasets)."""
    # Metadata: everything except 'data'
    metadata = {
        "count": workspace_dict.get("count", 0),
        "environment": workspace_dict.get("environment", {}),
        "history": workspace_dict.get("history", {}),
        "result": workspace_dict.get("result", {})
    }

    # Save metadata as JSON string inside HDF5
    store = pd.HDFStore(filepath, mode="w")
    try:
        store.put("metadata", pd.Series({"json": json.dumps(metadata)}))

        # Save each DataFrame/Series separately
        for name, obj in workspace_dict.get("data", {}).items():
            if isinstance(obj, pd.DataFrame):
                store.put(f"data/{name}", obj)
            elif isinstance(obj, pd.Series):
                store.put(f"data/{name}", obj.to_frame(name="value"))
            else:
                raise TypeError(f"Unsupported type {type(obj)} for {name}")
    finally:
        store.close()

def load_workspace_hdf5(filepath):
    """Load workspace from HDF5."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Workspace file not found: {filepath}")

    store = pd.HDFStore(filepath, mode="r")
    try:
        # Load metadata
        metadata_json = store["metadata"]["json"].iloc[0]
        metadata = json.loads(metadata_json)

        # Load data
        data = {}
        for key in store.keys():
            if key.startswith("/data/"):
                name = key.split("/")[-1]
                obj = store[key]
                if isinstance(obj, pd.DataFrame) and obj.shape[1] == 1 and "value" in obj.columns:
                    data[name] = obj["value"]  # restore Series
                else:
                    data[name] = obj

        workspace = {
            "count": metadata.get("count", 0),
            "environment": metadata.get("environment", {}),
            "history": metadata.get("history", {}),
            "result": metadata.get("result", {}),
            "data": data
        }

        return workspace
    finally:
        store.close()

