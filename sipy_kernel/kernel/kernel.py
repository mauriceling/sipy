"""!
SiPy Kernel for Jupyter Notebook / JupyterLab

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
import base64
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from ipykernel.kernelbase import Kernel
from jupyter_client.kernelspec import KernelSpecManager
import importlib.util
import logging
import threading
import traceback
import logging
import importlib.metadata

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class SiPySecurityError(Exception):
    """Raised when a security policy violation is detected."""
    def __init__(self, command, triggered_keywords):
        self.command = command
        self.triggered_keywords = triggered_keywords
        super().__init__(f"Security policy violation: command contains restricted keywords")

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
        "env": {"SIPY_PY": sipy_py}}
    tmp = Path.cwd() / "_sipy_kernelspec"
    tmp.mkdir(exist_ok=True)
    (tmp / "kernel.json").write_text(json.dumps(spec, indent=2))
    ksm = KernelSpecManager()
    ksm.install_kernel_spec(str(tmp), "sipy", user=True, replace=True)
    print("Installed Jupyter kernel: SiPy")
    print("Verify with: jupyter kernelspec list")

class SiPyKernel(Kernel):
    implementation = "SiPy"
    implementation_version = "0.3.0"
    language = "sipy"
    language_version = "0.1"
    language_info = {"name": "bash", "mimetype": "text/x-sh", "file_extension": ".sipy", "codemirror_mode": "shell"}
    banner = "SiPy Kernel - REPL Mode"

    def _send_matplotlib_figures(self):
        """
        Capture and send all matplotlib figures as inline images to Jupyter.
        This function converts matplotlib figures to PNG images, encodes them as base64,
        and sends them as display_data messages for rendering in the notebook.
        
        Figures are automatically closed after sending to prevent them from appearing
        in a separate GUI window.
        """
        if not HAS_MATPLOTLIB:
            return
        
        try:
            # Get all current figure numbers
            fig_nums = plt.get_fignums()
            
            for fig_num in fig_nums:
                try:
                    fig = plt.figure(fig_num)
                    
                    # Render figure to PNG in memory
                    buffer = io.BytesIO()
                    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                    buffer.seek(0)
                    img_data = buffer.read()
                    buffer.close()
                    
                    # Encode to base64
                    b64 = base64.b64encode(img_data).decode('ascii')
                    
                    # Send to Jupyter as display_data
                    try:
                        self.send_response(
                            self.iopub_socket,
                            "display_data",
                            {
                                "data": {
                                    "image/png": b64
                                },
                                "metadata": {}
                            }
                        )
                    except Exception as e:
                        self._log.error("Failed to send figure display_data: %s", e)
                    
                    # Close the figure to prevent GUI window
                    plt.close(fig)
                    
                except Exception as e:
                    self._log.error("Error processing figure %d: %s", fig_num, e)
        
        except Exception as e:
            self._log.debug("Error in _send_matplotlib_figures: %s", e)

    def _is_safe_command(self, line):
        """
        Security check for SiPy commands.
        Blacklists dangerous keywords that could lead to code execution or system access.
        
        Returns
        -------
        tuple
            (is_safe: bool, triggered_keywords: list)
        """
        if not getattr(self, '_security_enabled', True):
            return (True, [])  # Security disabled
        
        dangerous_keywords = [
            "import", "os.", "sys.", "eval",  "open(", "file(", "__", "subprocess", "shutil", "socket", "urllib", "requests", "http", "rm ", "del ", ".rm", ".del", "format(", "f\"", "f'", ".format"
        ]
        triggered = [kw for kw in dangerous_keywords if kw in line]
        return (len(triggered) == 0, triggered)

    def __init__(self, *args, **kwargs):
        # Version checks for compatibility
        try:
            ipykernel_version = importlib.metadata.version('ipykernel')
            jupyter_client_version = importlib.metadata.version('jupyter_client')
            # Minimum versions (adjust as needed)
            min_ipykernel = (6, 0, 0)
            min_jupyter_client = (7, 0, 0)
            current_ipykernel = tuple(map(int, ipykernel_version.split('.')[:3]))
            current_jupyter_client = tuple(map(int, jupyter_client_version.split('.')[:3]))
            if current_ipykernel < min_ipykernel:
                raise RuntimeError(f"ipykernel version {ipykernel_version} is too old. Minimum required: {'.'.join(map(str, min_ipykernel))}")
            if current_jupyter_client < min_jupyter_client:
                raise RuntimeError(f"jupyter_client version {jupyter_client_version} is too old. Minimum required: {'.'.join(map(str, min_jupyter_client))}")
        except importlib.metadata.PackageNotFoundError as e:
            raise RuntimeError(f"Required package not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Version check failed: {e}")

        super().__init__(*args, **kwargs)

        # Configurable security mode
        self._security_enabled = os.environ.get("SIPY_SECURITY_ENABLED", "true").lower() in ("true", "1", "yes")

        # Resource monitoring: thread limits and output limits
        self._max_concurrent_threads = int(os.environ.get("SIPY_MAX_THREADS", "10"))
        self._max_output_size = int(os.environ.get("SIPY_MAX_OUTPUT_SIZE", "1048576"))  # 1MB default
        self._active_threads = []

        # Configure logger: console level controlled by SIPY_KERNEL_LOG_LEVEL; file handler will capture DEBUG
        log_level_name = os.environ.get("SIPY_KERNEL_LOG_LEVEL", "WARNING").upper()
        console_level = getattr(logging, log_level_name, logging.WARNING)
        self._log = logging.getLogger("sipy.kernel")
        # Always set logger to DEBUG so handlers can filter independently
        self._log.setLevel(logging.DEBUG)

        # Console handler (stderr) with configurable level
        if not any(isinstance(h, logging.StreamHandler) for h in self._log.handlers):
            ch = logging.StreamHandler(sys.stderr)
            ch.setLevel(console_level)
            ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            self._log.addHandler(ch)

        self._log.debug("Initialization starting, cwd=%s", os.getcwd())
        sipy_py_env = os.environ.get("SIPY_PY", "")
        sipy_py = Path(sipy_py_env).expanduser() if sipy_py_env else None

        # If SIPY_PY not set or file not found, walk up from cwd to locate sipy.py
        if not sipy_py or not sipy_py.exists():
            self._log.debug("Searching for sipy.py...")
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
                self._log.debug("Found sipy.py at %s", sipy_py)
            else:
                # Fallback: check in user home
                user_sipy = Path.home() / ".sipy" / "sipy.py"
                if user_sipy.exists():
                    sipy_py = user_sipy
                    self._log.debug("Found sipy.py in user home at %s", sipy_py)
                else:
                    self._log.error("Could not find sipy.py. Searched in current directory tree (up to 32 levels) and %s. Set SIPY_PY environment variable to the path of sipy.py.", user_sipy)
                    self.sipy_shell = None
                    self.sipy_ready = False
                    return

        # Ensure sipy directory is on sys.path and make it the working directory
        sipy_dir = str(sipy_py.parent.resolve())
        self._log.debug("Setting up sipy_dir=%s", sipy_dir)
        if sipy_dir not in sys.path:
            sys.path.insert(0, sipy_dir)
        try:
            os.chdir(sipy_dir)
            self._log.debug("Changed cwd to %s", sipy_dir)
        except Exception as e:
            self._log.debug("Failed to chdir: %s", e)
            pass
        # Export SIPY_PY for downstream code that expects it
        os.environ["SIPY_PY"] = str(sipy_py)

        # Add file handler for persistent logs (always capture DEBUG)
        log_file = os.environ.get("SIPY_KERNEL_LOG_FILE", str(Path(sipy_dir) / "sipy-kernel.log"))
        try:
            if not any(isinstance(h, logging.FileHandler) for h in self._log.handlers):
                fh = logging.FileHandler(log_file)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
                self._log.addHandler(fh)
                self._log.debug("File logging enabled at %s", log_file)
        except Exception:
            pass

        try:
            self._log.debug("Loading sipy module from %s", sipy_py)
            spec = importlib.util.spec_from_file_location("sipy", str(sipy_py))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sipy = module
            self._log.debug("Creating SiPy_Shell instance")
            self.sipy_shell = sipy.SiPy_Shell()
            # Validate SiPy_Shell has required method
            if not hasattr(self.sipy_shell, 'interpret') or not callable(getattr(self.sipy_shell, 'interpret')):
                raise RuntimeError("SiPy_Shell does not have a callable 'interpret' method.")
            self._log.info("SiPy_Shell created and validated successfully")
            self.sipy_ready = True
            try:
                self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": f"SiPy kernel initialized. SIPY_PY={sipy_py} cwd={sipy_dir}\n"})
            except Exception:
                pass
        except Exception as e:
            self._log.exception("Exception during initialization: %s", e)
            import traceback
            traceback.print_exc()
            try:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": f"Failed to initialize SiPy: {e}\n"})
            except Exception:
                pass
            self.sipy_shell = None
            self.sipy_ready = False

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        """
        Execute a block of code in the SiPy environment.

        Parameters
        ----------
        code : str
            The code to be executed in the SiPy environment.
        silent : bool
            Whether to suppress output to the Jupyter notebook.
        store_history : bool
            Whether to store the code block in the SiPy history.
        user_expressions : dict
            A dictionary of user expressions to be evaluated after the code block has been executed.
        allow_stdin : bool
            Whether to allow access to the standard input stream.

        Returns
        -------
        A dictionary containing information about the result of the execution.
        """
        code = (code or "").strip()
        if not code:
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {}}

        thread = None  # Initialize to handle all code paths
        self._log.debug("Starting execution of code (length=%d): %s", len(code), code[:100] + "..." if len(code) > 100 else code)

        if not self.sipy_ready:
            msg = (
                "SiPy kernel is not properly initialized.\n"
                "Ensure SIPY_PY environment variable points to a valid sipy.py file.\n")
            if not silent:
                try:
                    self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": msg})
                except Exception as e:
                    self._log.error("Failed to send error response: %s", e)
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "SiPyInitError",
                "evalue": msg,
                "traceback": []}

        # Run interpret in a worker thread with timeout to avoid blocking the server
        # Prefer session timeout set by `sipy.set_timeout`, then fall back to env or default
        exec_timeout = getattr(self, "_exec_timeout", None)
        if exec_timeout is None:
            try:
                exec_timeout = int(os.environ.get("SIPY_EXEC_TIMEOUT", "30"))
            except Exception:
                exec_timeout = 30
        self._log = getattr(self, "_log", logging.getLogger("sipy.kernel"))
        self._log.debug("Executing code (timeout=%ss): %s", exec_timeout, code)

        def session_manager(line):
            # Handle session.get_timeout and session.set_timeout
            """
            Handle special session commands sent from the client.

            The session commands are prefixed with "session." and are used to query
            or modify the state of the kernel. The following session commands are
            supported:

            - `session.get_timeout`: Returns the current execution timeout in seconds.
            - `session.set_timeout=<val>`: Sets the execution timeout to `<val>` seconds.
            - `session.get_cwd`: Returns the current working directory.
            - `session.set_cwd=<cwd>`: Sets the current working directory to `<cwd>`.
            - `session.get_log_level`: Returns a list of the current log levels.
            - `session.set_log_level=<level>`: Sets the log level to `<level>`.
            - `session.get_security`: Returns whether security is enabled.
            - `session.set_security=<val>`: Enables or disables security based on `<val>`.
            """
            if line.startswith("session.get_timeout"):
                val = getattr(self, "_exec_timeout", int(os.environ.get("SIPY_EXEC_TIMEOUT", "30")))
                print(f"SiPy Kernel execution timeout is {val} seconds")
            if line.startswith("session.set_timeout"):
                parts = line.split("=")
                try:
                    val = int(parts[1].strip())
                    self._exec_timeout = val
                    print(f"SiPy Kernel execution timeout set to {val} seconds")
                except Exception:
                    print("Error: Invalid timeout value", file=sys.stderr)
            # Handle session.get_cwd and session.set_cwd
            if line.startswith("session.get_cwd"):
                print(f"Current working directory: {os.getcwd()}")
            if line.startswith("session.set_cwd"):
                parts = line.split("=")
                try:
                    cwd = parts[1].strip()
                    os.chdir(cwd)
                    print(f"Working directory changed to {os.getcwd()}")
                except Exception as e:
                    print(f"Error: Could not change directory: {e}", file=sys.stderr)
            # Handle session.get_log_level and session.set_log_level
            if line.startswith("session.get_log_level"):
                levels = [logging.getLevelName(h.level) for h in self._log.handlers]
                print(f"Current log levels: {levels}")
            if line.startswith("session.set_log_level"):
                parts = line.split("=")
                try:
                    level_name = parts[1].strip().upper()
                    numeric_level = getattr(logging, level_name, None)
                    if numeric_level is not None and isinstance(numeric_level, int):
                        for handler in self._log.handlers:
                            handler.setLevel(numeric_level)
                        print(f"Log level set to {level_name}")
                    else:
                        print(f"Error: Invalid log level '{level_name}'", file=sys.stderr)
                except Exception:
                    print("Error: Invalid log level format", file=sys.stderr)
            # Handle session.get_security and session.set_security
            if line.startswith("session.get_security"):
                print(f"Security enabled: {self._security_enabled}")
            if line.startswith("session.set_security"):
                parts = line.split("=")
                try:
                    val = parts[1].strip().lower()
                    if val in ("true", "1", "yes"):
                        self._security_enabled = True
                    elif val in ("false", "0", "no"):
                        self._security_enabled = False
                    else:
                        print("Error: Invalid security value. Use true/false", file=sys.stderr)
                        return None
                    print(f"Security set to {self._security_enabled}")
                except Exception:
                    print("Error: Invalid security format", file=sys.stderr)
            return None

        result_container = {}

        def sipy_worker():
            """
            Internal worker function for executing SiPy commands

            This function splits the input code by newlines, filters out empty lines and comment lines,
            and executes each line as a separate SiPy command. It also performs security checks
            to ensure that only safe commands are executed.

            The function captures stdout and stderr output from the commands and stores them in a result
            container, along with any exceptions that occur during execution.

            The function also audits each command in a log file and limits the size of the output
            to prevent excessive memory usage.

            :param code: The input code to execute as a SiPy command
            :type code: str
            :return: A dictionary containing the result of the command execution, stdout output, stderr output,
                and any exceptions that occur during execution
            :rtype: dict
            """
            try:
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Split by newlines to allow multiple commands per cell
                    lines = code.split('\n')
                    for line in lines:
                        line = line.strip()
                        if (not line) or (line.startswith("#")):  # Skip empty lines or comment lines
                            continue
                        if line.startswith("session."):
                            result = session_manager(line)
                        else:
                            # Security: Validate command
                            is_safe, triggered_keywords = self._is_safe_command(line)
                            if not is_safe:
                                raise SiPySecurityError(line, triggered_keywords)
                            # Audit log
                            self._log.info("Executing SiPy command: %s", line)
                            # Regular SiPy command
                            result = self.sipy_shell.interpret(line)
                result_container["result"] = result
                result_container["stdout"] = stdout_capture.getvalue()
                result_container["stderr"] = stderr_capture.getvalue()
                
                # Capture matplotlib figures as inline images
                result_container["has_figures"] = len(plt.get_fignums()) > 0 if HAS_MATPLOTLIB else False
                # Resource monitoring: limit output sizes
                if len(result_container["stdout"]) > self._max_output_size:
                    result_container["stdout"] = result_container["stdout"][:self._max_output_size] + "\n... [stdout truncated]"
                    self._log.warning("Stdout output truncated to %d bytes", self._max_output_size)
                if len(result_container["stderr"]) > self._max_output_size:
                    result_container["stderr"] = result_container["stderr"][:self._max_output_size] + "\n... [stderr truncated]"
                    self._log.warning("Stderr output truncated to %d bytes", self._max_output_size)
                result_container["exc"] = None
            except SiPySecurityError as e:
                # Format security error nicely without full traceback
                security_msg = (
                    f"[SECURITY] Policy Violation\n\n"
                    f"Command: {e.command}\n\n"
                    f"Restricted keywords detected: {', '.join(repr(kw) for kw in e.triggered_keywords)}\n\n"
                    f"Your command contains operations that are blocked for security reasons.\n"
                    f"Blocked keywords: file operations (open, del), imports, eval, system calls, etc.\n\n"
                    f"[TIP] Use SiPy commands instead. To disable security, set:\n"
                    f"   SIPY_SECURITY_ENABLED=false or\n"
                    f"   session.set_security=false"
                )
                result_container["exc"] = security_msg
                result_container["is_security_error"] = True
            except Exception:
                result_container["exc"] = traceback.format_exc()
                result_container["is_security_error"] = False

        """
        Main routine for cell operation
        """
        # HTML cell support (explicit opt-in)
        if code.startswith("%%html"):
            html_content = "\n".join(code.splitlines()[1:])
            if not silent:
                try:
                    self.send_response(self.iopub_socket, "display_data",
                        {"data": {"text/html": html_content},
                         "metadata": {}})
                except Exception as e:
                    self._log.error("Failed to send HTML response: %s", e)
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {}}
        else:
            # Default - SiPy cell
            # Resource monitoring: check thread limit
            if len(self._active_threads) >= self._max_concurrent_threads:
                msg = f"Too many concurrent executions. Maximum allowed: {self._max_concurrent_threads}"
                self._log.warning(msg)
                if not silent:
                    try:
                        self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": msg + "\n"})
                    except Exception as e:
                        self._log.error("Failed to send thread limit response: %s", e)
                return {
                    "status": "error",
                    "execution_count": self.execution_count,
                    "ename": "ThreadLimitError",
                    "evalue": msg,
                    "traceback": []}
            self._log.debug("Starting SiPy execution thread")
            thread = threading.Thread(target=sipy_worker, daemon=True)
            self._active_threads.append(thread)
            thread.start()
            thread.join(exec_timeout)
            # Cleanup: remove from active threads
            if thread in self._active_threads:
                self._active_threads.remove(thread)
            if thread.is_alive():
                self._log.warning("Thread did not complete within timeout; potential resource leak")
            self._log.debug("SiPy execution thread completed")
        """
        End - Main routine for cell operation
        """

        if thread is not None and thread.is_alive():
            # timed out
            self._log.warning("Execution timed out after %d seconds", exec_timeout)
            timeout_msg = f"Execution timed out after {exec_timeout} seconds.\n"
            if not silent:
                try:
                    self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": timeout_msg})
                except Exception as e:
                    self._log.error("Failed to send timeout response: %s", e)
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "SiPyExecutionTimeout",
                "evalue": timeout_msg,
                "traceback": []}

        # Check for exception in worker
        if result_container.get("exc"):
            exc_msg = result_container.get("exc")
            is_security_error = result_container.get("is_security_error", False)
            self._log.error("Exception in SiPy execution: %s", exc_msg)
            
            # Structured error response
            if is_security_error:
                ename = "SiPySecurityError"
                evalue = "Security policy violation detected."
                error_text = exc_msg  # Already formatted nicely
            elif "SiPy" in exc_msg or "interpret" in exc_msg:
                ename = "SiPyExecutionError"
                evalue = "SiPy command execution failed. See stderr for details."
                error_text = f"Error executing code:\n{exc_msg}\n"
            else:
                ename = "ExecutionError"
                evalue = "Code execution failed. See stderr for details."
                error_text = f"Error executing code:\n{exc_msg}\n"
            
            if not silent:
                try:
                    self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": error_text})
                except Exception as e:
                    self._log.error("Failed to send exception response: %s", e)
            
            # Always include error_text in traceback so it's displayed in notebook
            traceback_lines = error_text.split("\n")
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": ename,
                "evalue": evalue,
                "traceback": traceback_lines}

        stdout_text = result_container.get("stdout", "")
        stderr_text = result_container.get("stderr", "")

        # Send captured output to Jupyter
        if not silent:
            # Render stdout as rich display (Markdown + Plain fallback)
            if stdout_text:
                try:
                    self.send_response(self.iopub_socket,
                        "display_data",
                        {"data": {
                                "text/markdown": f"```\n{stdout_text}\n```",
                                "text/plain": stdout_text},
                            "metadata": {}
                        })
                except Exception as e:
                    self._log.error("Failed to send display_data for stdout: %s", e)

            # Keep stderr as stream (errors should look like errors)
            if stderr_text:
                try:
                    self.send_response(
                        self.iopub_socket,
                        "stream",
                        {"name": "stderr", "text": stderr_text})
                except Exception as e:
                    self._log.error("Failed to send stderr response: %s", e)

            # Send matplotlib figures as inline images
            if result_container.get("has_figures"):
                self._send_matplotlib_figures()

        self._log.debug("Execution completed successfully")
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {}}

    def do_complete(self, code, cursor_pos):
        """
        Handle tab completion and code introspection.
        
        Parameters
        ----------
        code : str
            The code string to provide completions for.
        cursor_pos : int
            The position of the cursor in the code string.
        
        Returns
        -------
        dict
            A dictionary with 'matches', 'cursor_start', 'cursor_end', 'metadata', and 'status'.
        """
        self._log.debug("do_complete called with cursor_pos=%d, code length=%d", cursor_pos, len(code))
        
        if not self.sipy_ready:
            return {"status": "error", "matches": [], "cursor_start": cursor_pos, "cursor_end": cursor_pos, "metadata": {}}
        
        # Extract the word being completed
        line = code[:cursor_pos]
        word_start = cursor_pos
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] in "_."):
            word_start -= 1
        word = code[word_start:cursor_pos]
        
        matches = []
        
        # Get SiPy shell available commands from interpret method's recognized patterns
        # Common SiPy commands
        sipy_commands = [
            "let", "list", "set", "load", "save", "describe", "compute", "mean", "median",
            "variance", "std", "min", "max", "count", "correlate", "regression", "ttest",
            "anova", "normality", "survival", "execute", "import", "export", "help", "info"
        ]
        
        # Get workspace variables from sipy_shell if available
        workspace_vars = []
        try:
            if hasattr(self.sipy_shell, 'data'):
                workspace_vars = list(self.sipy_shell.data.keys())
        except Exception as e:
            self._log.debug("Failed to extract workspace variables: %s", e)
        
        # Get session commands
        session_commands = [
            "session.get_timeout", "session.set_timeout", "session.get_cwd", "session.set_cwd",
            "session.get_log_level", "session.set_log_level", "session.get_security", "session.set_security"
        ]
        
        # Filter matches based on current word
        all_completions = sipy_commands + workspace_vars + session_commands
        matches = [c for c in all_completions if c.startswith(word)]
        
        # Remove duplicates and sort
        matches = sorted(list(set(matches)))
        
        self._log.debug("do_complete found %d matches for word '%s'", len(matches), word)
        
        return {
            "status": "ok",
            "matches": matches,
            "cursor_start": word_start,
            "cursor_end": cursor_pos,
            "metadata": {}
        }

    def do_kernel_info(self):
        """
        Return information about the SiPy kernel for IDE integration.
        
        Returns
        -------
        dict
            Kernel information including language, version, and capabilities.
        """
        self._log.debug("do_kernel_info called")
        return {
            "protocol_version": "5.3",
            "implementation": self.implementation,
            "implementation_version": self.implementation_version,
            "language_info": {
                "name": "SiPy",
                "version": self.language_version,
                "mimetype": "text/x-sipy",
                "file_extension": ".sipy",
                "pygments_lexer": "bash",
                "codemirror_mode": "shell",
                "nbconvert_exporter": "script"
            },
            "banner": self.banner,
            "status": "ok",
            "help_links": [
                {"text": "SiPy Documentation", "url": "https://github.com/sipy/sipy"},
                {"text": "SiPy Command Help", "url": "https://github.com/sipy/sipy/wiki"}
            ]
        }