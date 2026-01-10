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
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from ipykernel.kernelbase import Kernel
from jupyter_client.kernelspec import KernelSpecManager

# Add sipy directory to path for imports
sipy_py_env = os.environ.get("SIPY_PY")
if sipy_py_env:
    sipy_dir = str(Path(sipy_py_env).parent)
    if sipy_dir not in sys.path:
        sys.path.insert(0, sipy_dir)

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
    implementation_version = "0.2.0"
    language = "sipy"
    language_version = "0.1"
    language_info = {"name": "sipy", "mimetype": "text/plain", "file_extension": ".sipy"}
    banner = "SiPy Kernel - REPL Mode"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize persistent SiPy REPL shell
        sipy_py = Path(os.environ.get("SIPY_PY", "")).expanduser()
        if not sipy_py.exists():
            self.sipy_shell = None
            self.sipy_ready = False
        else:
            try:
                # Import SiPy_Shell from sipy.py
                import sipy
                self.sipy_shell = sipy.SiPy_Shell()
                self.sipy_ready = True
            except Exception as e:
                self.send_response(
                    self.iopub_socket, 
                    "stream", 
                    {"name": "stderr", "text": f"Failed to initialize SiPy: {e}\n"}
                )
                self.sipy_shell = None
                self.sipy_ready = False

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
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

        if not self.sipy_ready:
            msg = (
                "SiPy kernel is not properly initialized.\n"
                "Ensure SIPY_PY environment variable points to a valid sipy.py file.\n"
            )
            if not silent:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": msg})
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "SiPyInitError",
                "evalue": msg,
                "traceback": [],
            }

        try:
            # Capture output from the shell's interpret method
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                result = self.sipy_shell.interpret(code)
            
            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()
            
            # Send captured output to Jupyter
            if not silent:
                if stdout_text:
                    self.send_response(
                        self.iopub_socket, 
                        "stream", 
                        {"name": "stdout", "text": stdout_text}
                    )
                if stderr_text:
                    self.send_response(
                        self.iopub_socket, 
                        "stream", 
                        {"name": "stderr", "text": stderr_text}
                    )
            
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            if not silent:
                self.send_response(
                    self.iopub_socket, 
                    "stream", 
                    {"name": "stderr", "text": f"Error executing code:\n{tb}\n"}
                )
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "SiPyExecutionError",
                "evalue": str(e),
                "traceback": tb.split('\n'),
            }