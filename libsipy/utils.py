'''!
libsipy (Utils): Utility Functions

Date created: 16th December 2025

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
import platform
import os
import subprocess

def find_executable(name):
    """Helper function to find executable using system commands.

    This is at module level so it's available to SiPy_Shell during
    initialization (avoids UnboundLocalError when called before a
    nested definition).
    """
    try:
        if platform.system() == "Windows":
            # Use 'where' on Windows
            result = subprocess.run(['where', name], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        else:
            # Use 'which' on Unix-like systems
            result = subprocess.run(['which', name], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception:
        return None
    return None

def find_R_executable():
    # Detect operating system and find R executable        
    system = platform.system()
    rscript_exe = None        
    if system == "Windows":
        # Try portable R first (Windows)
        portable_r = os.path.abspath("portable_R\\bin\\Rscript.exe")
        if os.path.exists(portable_r):
            rscript_exe = portable_r
        else:
            # Try using 'where' to find Rscript
            rscript_exe = find_executable('Rscript.exe')
            # If not found, try common installation paths
            if not rscript_exe:
                # Check PATH for R
                r_cmd = shutil.which('R')
                if r_cmd:
                    r_dir = os.path.dirname(os.path.dirname(r_cmd))
                    possible_rscript = os.path.join(r_dir, 'bin', 'Rscript.exe')
                    if os.path.exists(possible_rscript):
                        rscript_exe = possible_rscript
                if not rscript_exe:
                    # Try installed R on Windows - common paths
                    win_paths = [
                        os.path.join(os.environ.get("ProgramFiles", ""), "R"),
                        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "R"),
                        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "R")
                    ]
                    for base in win_paths:
                        if os.path.exists(base):
                            # Find latest R version
                            r_versions = [d for d in os.listdir(base) if d.startswith("R-")]
                            if r_versions:
                                latest = sorted(r_versions)[-1]
                                rpath = os.path.join(base, latest, "bin", "Rscript.exe")
                                if os.path.exists(rpath):
                                    rscript_exe = rpath
                                    break
    else:
        # Unix-like systems (Linux/Mac)
        # First try using 'which'
        rscript_exe = find_executable('Rscript')
        
        if not rscript_exe:
            # Try using R to find Rscript
            r_cmd = shutil.which('R')
            if r_cmd:
                try:
                    # Ask R where it is installed
                    result = subprocess.run([r_cmd, '--slave', '-e', 
                                          'cat(file.path(R.home("bin"), "Rscript"))'],
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        possible_rscript = result.stdout.strip()
                        if os.path.exists(possible_rscript):
                            rscript_exe = possible_rscript
                except:
                    pass
        if not rscript_exe:
            # Fall back to common Unix paths
            unix_paths = [
                "/usr/bin/Rscript",
                "/usr/local/bin/Rscript",
                "/opt/local/bin/Rscript",  # MacPorts
                "/usr/lib/R/bin/Rscript",  # Some Linux distributions
                os.path.expanduser("~/Library/R/bin/Rscript"),  # Mac user install
                "/Library/Frameworks/R.framework/Resources/bin/Rscript"  # Mac framework install
            ]
            for path in unix_paths:
                if os.path.exists(path):
                    rscript_exe = path
                    break
    return rscript_exe

def find_julia_executable():
    """
    Attempts to locate the Julia executable across platforms.
    Returns the absolute path to julia, or None if not found.
    """

    system = platform.system()
    julia_exe = None

    if system == "Windows":
        # 1. Try portable Julia first (if you later decide to ship one)
        portable_julia = os.path.abspath("portable_julia\\bin\\julia.exe")
        if os.path.exists(portable_julia):
            return portable_julia

        # 2. Try PATH lookup
        julia_exe = shutil.which("julia.exe")
        if julia_exe:
            return julia_exe

        # 3. Common Windows installation paths
        win_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Julia"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Julia"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Julia")
        ]

        for base in win_paths:
            if os.path.exists(base):
                # Julia versions are typically julia-1.x.y
                versions = [d for d in os.listdir(base) if d.lower().startswith("julia")]
                if versions:
                    latest = sorted(versions)[-1]
                    candidate = os.path.join(base, latest, "bin", "julia.exe")
                    if os.path.exists(candidate):
                        return candidate

    else:
        # Unix-like systems (Linux / macOS)

        # 1. Try PATH lookup
        julia_exe = shutil.which("julia")
        if julia_exe:
            return julia_exe

        # 2. Ask Julia itself (if callable indirectly)
        try:
            result = subprocess.run(
                ["julia", "--startup-file=no", "-e", "print(Sys.BINDIR)"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                bindir = result.stdout.strip()
                candidate = os.path.join(bindir, "julia")
                if os.path.exists(candidate):
                    return candidate
        except:
            pass

        # 3. Common Unix installation paths
        unix_paths = [
            "/usr/bin/julia",
            "/usr/local/bin/julia",
            "/opt/julia/bin/julia",               # manual installs
            "/opt/local/bin/julia",               # MacPorts
            "/Applications/Julia.app/Contents/Resources/julia/bin/julia",  # macOS app
            os.path.expanduser("~/bin/julia")
        ]

        for path in unix_paths:
            if os.path.exists(path):
                return path
    return None
    