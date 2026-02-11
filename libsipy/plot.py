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

import seaborn as sns
import matplotlib.pyplot as plt

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
    plt.show()
    return fig