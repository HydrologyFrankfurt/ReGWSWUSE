# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

"""Module for print cell specific results during simulation."""

import numpy as np
import pandas as pd


def get_np_coords_cell_output(xr_data, sector, cell_specific_output):
    """
    Get NumPy indices for nearest lat, lon, and time in the xarray dataset.

    Parameters
    ----------
    xr_data : xarray.DataArray or xarray.Dataset
        The xarray object containing the data to find coordinates in.
    sector : str
        The sector type (e.g., 'irrigation') used to determine the date format.
    cell_specific_output : dict
        Dictionary with 'lat', 'lon', 'year', and optional 'month' to locate
        a specific cell's data:
        {
            'coords': {
                'lat': float,
                'lon': float,
                'year': int,
                'month': int (optional)
            }
        }

    Returns
    -------
    tuple
        Tuple of indices (time_idx, lat_idx, lon_idx) for the closest time,
        latitude, and longitude.

    """
    coords = cell_specific_output['coords']
    lat = coords['lat']
    lon = coords['lon']
    year = coords['year']
    month = coords['month']
    if sector == 'irrigation':
        date = pd.Timestamp(f'{year}-{month:02d}-01')
    else:
        date = pd.Timestamp(f'{year}-01-01')

    # Wähle den nächsten Punkt anhand von lat, lon und time
    selected_data = xr_data.sel(lat=lat, lon=lon, time=date, method='nearest')

    # Finde die NumPy-Indizes für die Koordinaten time, lat and lon
    time_idx = \
        np.where(xr_data.coords['time'].values ==
                 np.datetime64(selected_data.coords['time'].values))[0][0]
    lat_idx = \
        np.where(xr_data.coords['lat'].values ==
                 selected_data.coords['lat'].values)[0][0]

    lon_idx = \
        np.where(xr_data.coords['lon'].values ==
                 selected_data.coords['lon'].values)[0][0]

    return (time_idx, lat_idx, lon_idx)


def print_cell_value(var, var_name, coords_idx=None, unit="-", flag=False):
    """
    Print the value of the variable for specific cell indices.
    
    Parameters
    ----------
    var : numpy.ndarray, float, or int
        The variable whose value you want to print. It can be a 1D, 2D, 3D 
        array or a scalar (float/int).
    var_name : str
        The name of the variable as a string, which will be printed alongside 
        the value.
    coords_idx : tuple or list, optional
        A tuple or list containing the indices (time_idx, lat_idx, lon_idx) for 
        3D arrays, or (lat_idx, lon_idx) for 2D arrays. For 1D arrays, this is 
        ignored. If var is a scalar, this is ignored.
        - For 3D arrays: (time_idx, lat_idx, lon_idx)
        - For 2D arrays: (lat_idx, lon_idx)
    unit : str, optional
        The unit of the variable (default is "-"). This will be appended to the 
        printed value.
    flag : bool, optional
        If True, the function will print the value. If False, the function will 
        do nothing. Default is False.
    """
    if flag:
        # Check if var is a scalar (int, float)
        if isinstance(var, (float, int)):
            print(f'{var_name} [{unit}]: {var}')
        
        # If var is a numpy array, handle based on its dimensions
        elif hasattr(var, 'ndim'):
            if var.ndim == 3:
                print(f'{var_name} [{unit}]: ' 
                      f'{var[coords_idx[0], coords_idx[1], coords_idx[2]]}')
            elif var.ndim == 2:
                print(f'{var_name} [{unit}]: '
                      f'{var[coords_idx[1], coords_idx[2]]}')
            elif var.ndim == 1:
                print(f'{var_name} [{unit}]: {var[0]}')
            else:
                print(f'{var_name} [{unit}]: {var}')
        else:
            print(f'{var_name} [{unit}]: {var}')
