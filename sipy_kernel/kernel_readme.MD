# SiPy Kernel for Jupyter

## Overview

The SiPy kernel provides a Jupyter Notebook and JupyterLab interface to the SiPy interactive shell. Rather than re-implementing Python semantics or introducing a notebook-specific execution model, the kernel exposes SiPy’s existing REPL behaviour directly within Jupyter. Each notebook cell is interpreted as a sequence of SiPy commands, executed line-by-line, with outputs captured and rendered using standard Jupyter mechanisms.

The kernel is intentionally lightweight. It does not embed R, Julia, or Python execution logic itself, nor does it attempt to emulate their native kernels. Instead, it treats Jupyter as a graphical user interface and documentation layer layered on top of SiPy’s orchestration framework.

---

## Kernel Installation and Discovery

The kernel is installed via the `install()` function in `kernel.py`. During installation:

- The kernel is registered under the name **SiPy**
- The environment variable `SIPY_PY` is stored in the kernel specification
- The kernel entry point invokes `kernel.py` using the active Python interpreter

At runtime, the kernel locates `sipy.py` using one of two mechanisms:

1. If `SIPY_PY` is set and points to a valid `sipy.py`, that file is used directly
2. Otherwise, the kernel searches upward from the current working directory to locate `sipy.py`

Once located, the directory containing `sipy.py` becomes the kernel’s working directory. This ensures consistent file resolution across notebook cells and during external script execution.

---

## Execution Model

### Default Cell Behaviour (SiPy Mode)

By default, every notebook cell is treated as a **SiPy command cell**. No cell magics or language selectors are required.

Execution proceeds as follows:

- Cell contents are split into individual lines
- Empty lines and comment lines (`#`) are ignored
- Each remaining line is passed to `SiPy_Shell.interpret()`
- Output written to standard output or standard error is captured and returned to Jupyter

This preserves SiPy’s REPL semantics while allowing multiple commands to be executed within a single cell.

---

## Session Management Commands

The kernel exposes a small set of session-level commands that control kernel behaviour rather than SiPy itself. These commands are intercepted by the kernel and are not forwarded to the SiPy interpreter.

Supported commands:

- `session.get_timeout`  
  Display the current execution timeout (in seconds)

- `session.set_timeout = <int>`  
  Set the maximum execution time for a cell

- `session.get_cwd`  
  Display the current working directory

- `session.set_cwd = <path>`  
  Change the working directory for subsequent execution

---

## Execution Timeout and Safety

All SiPy execution occurs inside a worker thread with a configurable timeout:

- Default timeout is 30 seconds
- The timeout can be modified using `session.set_timeout`
- If execution exceeds the timeout, the cell is terminated and an error is returned

This prevents long-running or blocking operations from freezing the Jupyter server.

---

## HTML Cells

The kernel supports a minimal, explicit mechanism for rendering HTML output.

Cells beginning with `%%html` are treated as HTML cells rather than SiPy command cells. The remainder of the cell is rendered directly as HTML output in the notebook.

Example:

```
%%html

<h3>Analysis Notes</h3> <p>This result was generated using an external R backend.</p>
```

HTML rendering is intentionally limited to this explicit opt-in mechanism. The kernel does not attempt to support Markdown rendering, widgets, or interactive UI components.

---

## Output Handling

- Standard output (stdout) is captured and displayed as notebook output
- Standard error (stderr) is captured and displayed separately
- Tracebacks are returned verbatim when execution fails
- No implicit result inspection or object rendering is performed

This ensures that notebook output is a faithful representation of what SiPy actually executed.

---

## Logging and Diagnostics

The kernel includes structured logging to support debugging and auditing:

- Console log level controlled by the SIPY_KERNEL_LOG_LEVEL environment variable
- Persistent log file written to sipy-kernel.log by default
- All internal kernel activity is logged at DEBUG level to file

These logs are independent of notebook output and are intended for developers and advanced users.

---

## Design Philosophy

The SiPy kernel follows the same design principles as the core SiPy framework:

- Explicit execution rather than abstraction
- Script-level extensibility rather than API wrapping
- Reproducibility through inspectable artefacts
- Minimal coupling between languages and interfaces

The kernel does not attempt to turn SiPy into a notebook-native language. Instead, it treats Jupyter as a familiar interface layered on top of a deterministic, script-driven execution model.

---

## Intended Use

The SiPy kernel is designed for:

- Interactive exploration of SiPy workflows
- Literate documentation of multi-language analytical pipelines
- Teaching and demonstration of reproducible statistical analysis
- Orchestrating external R, Julia, Python, and shell-based tools from a unified interface

It is not intended to replace Python, R, or Julia kernels, nor to serve as a general-purpose notebook language.
