'''!
libsipy (Plot): Plotting Functions for SiPy

Date created: 11th February 2026

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

import matplotlib
import sys

# Detect if running in Jupyter kernel context
def _is_jupyter_kernel():
    """Check if we're running in a Jupyter kernel."""
    try:
        # Check if ipykernel is running
        if 'ipykernel' in sys.modules:
            return True
        # Check for IPython kernel
        from IPython import get_ipython
        if get_ipython() is not None and 'IPKernelApp' in get_ipython().config:
            return True
    except (ImportError, AttributeError):
        pass
    return False

# Use non-interactive Agg backend only in Jupyter kernel to prevent GUI initialization in thread contexts
# Use interactive TkAgg or default for regular CLI/IDE use
if _is_jupyter_kernel():
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

def seaborn_histogram(data, **kwargs):
    '''! 
    Plots a histogram using seaborn.histplot.
    
    @param data: List or array-like data to plot
    @param kwargs: Additional keyword arguments for seaborn.histplot
                   Common kwargs: 
                   - bins (int or sequence): Number of bins or bin edges
                   - kde (bool): Whether to plot kernel density estimate
                   - stat (str): Statistic to compute ('count', 'density', 'frequency', etc.)
                   - color (str): Color of the bars
                   - hue (str): Column name for color-coding by groups
                   - palette (str): Color palette name
    
    @return: matplotlib figure object
    
    Python Usage Examples:
        from libsipy.plot import seaborn_histogram
        
        # Basic histogram
        data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
        seaborn_histogram(data)
        
        # Histogram with custom bins
        seaborn_histogram(data, bins=10)
        
        # Histogram with KDE overlay
        seaborn_histogram(data, kde=True)
        
        # Histogram with custom color
        seaborn_histogram(data, bins=8, kde=True, color='skyblue')
        
        # Histogram with density instead of count
        seaborn_histogram(data, bins=12, stat='density', kde=True)
    '''
    fig, ax = plt.subplots()
    sns.histplot(data=data, **kwargs, ax=ax)
    # Only show in CLI mode (not in Jupyter where kernel handles display)
    if not _is_jupyter_kernel():
        plt.show()
    return fig

def seaborn_boxplot(df, **kwargs):
    '''! 
    Plots a boxplot using seaborn.boxplot.
    
    @param df: DataFrame containing the data to plot
    @param kwargs: Additional keyword arguments for seaborn.boxplot
                   Common kwargs: 
                   - x (str): Column name for x-axis (categorical variable)
                   - y (str): Column name for y-axis (numeric variable)
                   - hue (str): Column name for color-coding by groups
                   - palette (str): Color palette name
                   - orient (str): Orientation ('v' for vertical, 'h' for horizontal)
                   - color (str): Color of the boxes
    
    @return: matplotlib figure object
    
    Python Usage Examples:
        from libsipy.plot import seaborn_boxplot
        
        # Basic boxplot
        import pandas as pd
        df = pd.DataFrame({'x': ['A', 'A', 'B', 'B'], 'y': [1, 2, 3, 4]})
        seaborn_boxplot(df, x='x', y='y')
        
        # Boxplot with hue
        seaborn_boxplot(df, x='x', y='y', hue='category')
        
        # Boxplot with custom color palette
        seaborn_boxplot(df, x='x', y='y', palette='Set2')
        
        # Horizontal boxplot
        seaborn_boxplot(df, x='y', y='x', orient='h')
    '''
    fig, ax = plt.subplots()
    sns.boxplot(data=df, **kwargs, ax=ax)
    # Only show in CLI mode (not in Jupyter where kernel handles display)
    if not _is_jupyter_kernel():
        plt.show()
    return fig

def seaborn_scatterplot(df, **kwargs):
    '''! 
    Plots a scatterplot using seaborn.scatterplot.
    
    @param df: DataFrame containing the data to plot
    @param kwargs: Additional keyword arguments for seaborn.scatterplot
                   Common kwargs: 
                   - x (str): Column name for x-axis
                   - y (str): Column name for y-axis
                   - hue (str): Column name for color-coding by groups
                   - size (str): Column name for marker size
                   - palette (str): Color palette name
                   - s (int): Size of markers
                   - alpha (float): Transparency of markers (0-1)
                   - style (str): Column name for marker style
    
    @return: matplotlib figure object
    
    Python Usage Examples:
        from libsipy.plot import seaborn_scatterplot
        
        # Basic scatterplot
        import pandas as pd
        df = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
        seaborn_scatterplot(df, x='x', y='y')
        
        # Scatterplot with hue
        seaborn_scatterplot(df, x='x', y='y', hue='category')
        
        # Scatterplot with size and hue
        seaborn_scatterplot(df, x='x', y='y', hue='category', size='magnitude')
        
        # Scatterplot with custom palette and alpha
        seaborn_scatterplot(df, x='x', y='y', hue='category', palette='Set2', alpha=0.6)
    '''
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, **kwargs, ax=ax)
    # Only show in CLI mode (not in Jupyter where kernel handles display)
    if not _is_jupyter_kernel():
        plt.show()
    return fig

def seaborn_regplot(df, **kwargs):
    '''! 
    Plots a regression plot using seaborn.regplot.
    
    @param df: DataFrame containing the data to plot
    @param kwargs: Additional keyword arguments for seaborn.regplot
                   Common kwargs: 
                   - x (str): Column name for x-axis
                   - y (str): Column name for y-axis
                   - order (int): Degree of polynomial regression (default: 1 for linear)
                   - scatter (bool): Whether to plot the data points
                   - fit_reg (bool): Whether to fit and plot the regression line
                   - color (str): Color of the line and points
                   - scatter_kws (dict): kwargs for scatter plot
                   - line_kws (dict): kwargs for regression line
    
    @return: matplotlib figure object
    
    Python Usage Examples:
        from libsipy.plot import seaborn_regplot
        
        # Basic regression plot
        import pandas as pd
        df = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [2, 4, 5, 4, 5]})
        seaborn_regplot(df, x='x', y='y')
        
        # Polynomial regression with order 2
        seaborn_regplot(df, x='x', y='y', order=2)
        
        # Regression plot without scatter points
        seaborn_regplot(df, x='x', y='y', scatter=False)
        
        # Regression plot with custom color
        seaborn_regplot(df, x='x', y='y', color='red')
    '''
    fig, ax = plt.subplots()
    sns.regplot(data=df, **kwargs, ax=ax)
    # Only show in CLI mode (not in Jupyter where kernel handles display)
    if not _is_jupyter_kernel():
        plt.show()
    return fig