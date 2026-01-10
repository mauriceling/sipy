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
import importlib.util

# Add sipy directory to path for imports
sipy_py_env = os.environ.get("SIPY_PY")
if sipy_py_env:
    sipy_dir = str(Path(sipy_py_env).parent)
    if sipy_dir not in sys.path:
        sys.path.insert(0, sipy_dir)

def install():
    sipy_py = os.environ.get("SIPY_PY")
    if sipy_py:
        sipy_path = Path(sipy_py)
        if not sipy_path.is_absolute():
            sipy_path = (Path.cwd() / sipy_path).resolve()
        sipy_py = str(sipy_path)
    else:
        sipy_py = ""
    print(f"Installing SiPy kernel with SIPY_PY={sipy_py}")
    spec = {
        "argv": [sys.executable, "-m", "kernel", "-f", "{connection_file}"],
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
        print(f"[SiPy Kernel] Initialization starting, cwd={os.getcwd()}", flush=True)
        sipy_py_env = os.environ.get("SIPY_PY", "")
        sipy_py = Path(sipy_py_env).expanduser() if sipy_py_env else None

        # If SIPY_PY not set or file not found, walk up from cwd to locate sipy.py
        if not sipy_py or not sipy_py.exists():
            print("[SiPy Kernel] Searching for sipy.py...", flush=True)
            found = None
            cur = Path.cwd()
            for _ in range(32):
                candidate = cur / "sipy.py"
                if candidate.exists():
                    found = candidate
                    break
                if cur.parent == cur:
                    break
                cur = cur.parent
            if found:
                sipy_py = found
                print(f"[SiPy Kernel] Found sipy.py at {sipy_py}", flush=True)
            else:
                print("[SiPy Kernel] Failed to find sipy.py", flush=True)
                self.sipy_shell = None
                self.sipy_ready = False
                return


        # Ensure sipy directory is on sys.path and make it the working directory
        sipy_dir = str(sipy_py.parent.resolve())
        print(f"[SiPy Kernel] Setting up sipy_dir={sipy_dir}", flush=True)
        if sipy_dir not in sys.path:
            sys.path.insert(0, sipy_dir)
        try:
            os.chdir(sipy_dir)
            print(f"[SiPy Kernel] Changed cwd to {sipy_dir}", flush=True)
        except Exception as e:
            print(f"[SiPy Kernel] Failed to chdir: {e}", flush=True)
            pass
        # Export SIPY_PY for downstream code that expects it
        os.environ["SIPY_PY"] = str(sipy_py)

        try:
            print(f"[SiPy Kernel] Loading sipy module from {sipy_py}...", flush=True)
            spec = importlib.util.spec_from_file_location("sipy", str(sipy_py))
            print("[SiPy Kernel] Creating module from spec...", flush=True)
            module = importlib.util.module_from_spec(spec)
            print("[SiPy Kernel] Executing module...", flush=True)
            spec.loader.exec_module(module)
            print("[SiPy Kernel] Module loaded successfully", flush=True)
            sipy = module
            print("[SiPy Kernel] Creating SiPy_Shell instance...", flush=True)
            self.sipy_shell = sipy.SiPy_Shell()
            print("[SiPy Kernel] SiPy_Shell created successfully", flush=True)
            self.sipy_ready = True
        except Exception as e:
            print(f"[SiPy Kernel] Exception during initialization: {e}", flush=True)
            import traceback
            traceback.print_exc()
            self.send_response(
                self.iopub_socket,
                "stream",
                {"name": "stderr", "text": f"Failed to initialize SiPy: {e}\n"},
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