# SiPy (Statistics in Python) - AI Agent Instructions

This document provides key information for AI agents working with the SiPy codebase.

## Project Overview

SiPy is a statistical analysis tool that combines Python and R capabilities with both CLI and GUI interfaces. The project aims to provide an accessible yet powerful platform for statistical analysis.

## Core Architecture

### Key Components

1. **Command Shell (`sipy.py`)**
   - Main entry point implementing `SiPy_Shell` class
   - Handles command parsing and execution
   - Manages data workspace and variable states

2. **Library Core (`libsipy/`)**
   - `base.py`: Core functionality and base classes
   - `data_wrangler.py`: Data manipulation utilities
   - `r_wrap.py`: R language integration
   - `workspace.py`: Workspace management

3. **Plugin System (`sipy_plugins/`)**
   - Plugin management through `sipy_pm.py`
   - Example plugins in `sipy_plugins/` directory
   - Plugins must inherit from `base_plugin.py`

### Data Flow

1. Commands flow: User input -> Command parsing -> Function execution -> Result display
2. Data handling: File input -> Data wrangling -> Statistical analysis -> Output
3. R integration: Python call -> R wrapper -> R execution -> Result conversion

## Development Workflows

### Running SiPy

```powershell
# GUI mode
python sipy.py

# CLI mode
python sipy.py shell

# Execute script
python sipy.py script_execute path/to/script.sipy
```

### Testing

1. Test scripts are in `test_scripts/*.sipy`
2. Run test suite: Execute `all-test.sipy`
3. Test reports are generated in `test_reports/`

## Project Conventions

### Command Format
- Commands follow pattern: `COMMAND [SUBCOMMAND] [ARGS]`
- Variable assignment: `let NAME be TYPE VALUE`
- Example: `let x be list 1,2,3,4,5`

### Plugin Development
1. Create new file in `sipy_plugins/`
2. Inherit from `BasePlugin`
3. Implement required methods
4. Register in plugin manager

### R Integration
- R functions are wrapped in `r_wrap.py`
- Use `portable_R/` for R environment
- Handle R-Python data conversion explicitly

## Key Integration Points

1. **R Integration**
   - Entry point: `r_wrap.py`
   - Data conversion in both directions
   - R environment configuration

2. **Plugin System**
   - Entry: `sipy_pm.py`
   - Plugin discovery and loading
   - Command registration

3. **Data Import/Export**
   - Excel file handling
   - Workspace state management
   - Data type conversion

## Best Practices

1. Follow existing command patterns when adding new functionality
2. Use proper error handling with informative messages
3. Document new commands in both code and user documentation
4. Maintain R-Python compatibility in statistical functions

## Reference Files

- `sipy.py`: Main implementation and command patterns
- `libsipy/base.py`: Core functionality examples
- `sipy_plugins/sample_plugin.py`: Plugin implementation template
- `test_scripts/all-test.sipy`: Testing patterns