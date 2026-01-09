"""!
SiPy Kernel for Jupyter

Date created: 10th January 2026

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
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

from ipykernel.kernelbase import Kernel
from jupyter_client.kernelspec import KernelSpecManager

def install():
    sipy_py = os.environ.get("SIPY_PY")
    spec = {
        "argv": ["python", "-m", "kernel", "-f", "{connection_file}"],
        "display_name": "SiPy",
        "language": "sipy",
        "env": {"SIPY_PY": sipy_py},
    }
    tmp = Path.cwd() / "_sipy_kernelspec"
    tmp.mkdir(exist_ok=True)
    (tmp / "kernel.json").write_text(json.dumps(spec, indent=2))
    ksm = KernelSpecManager()
    ksm.install_kernel_spec(str(tmp), "sipy", user=True, replace=True)
    print("Installed Jupyter kernel: SiPy")
    print("Verify with: jupyter kernelspec list")

class SiPyKernel(Kernel):
    implementation = "SiPy"
    implementation_version = "0.1.0"
    language = "sipy"
    language_version = "0.1"
    language_info = {"name": "sipy", "mimetype": "text/plain", "file_extension": ".sipy"}
    banner = "SiPy Kernel"

    def do_execute(
        self,
        code,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=False,
    ):
        code = (code or "").strip()
        if not code:
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

        sipy_py = Path(os.environ.get("SIPY_PY", "")).expanduser()
        if not sipy_py.exists():
            msg = (
                f"SIPY_PY not set or invalid.\n"
                f"Current SIPY_PY={sipy_py}\n"
                "Fix by setting SIPY_PY to your sipy.py full path in the kernelspec.\n"
            )
            if not silent:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": msg})
            return {"status": "error", "execution_count": self.execution_count, "ename": "SiPyConfigError", "evalue": msg, "traceback": []}

        # Write cell content to a temp .sipy file and run your SiPy engine on it
        with tempfile.NamedTemporaryFile("w", suffix=".sipy", delete=False) as f:
            f.write(code + "\n")
            script_path = f.name

        try:
            p = subprocess.run(
                [sys.executable, str(sipy_py), "script_execute", script_path],
                cwd=str(sipy_py.parent),
                capture_output=True,
                text=True,
            )

            if not silent:
                if p.stdout:
                    self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": p.stdout})
                if p.stderr:
                    self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": p.stderr})

            if p.returncode != 0:
                return {"status": "error", "execution_count": self.execution_count, "ename": "SiPyError", "evalue": f"SiPy exited with code {p.returncode}", "traceback": []}

            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        finally:
            try:
                os.remove(script_path)
            except OSError:
                pass