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


def print_cell_output_headline(sector, cell_specific_option, flag):
    """
    Print information about the selected cell's coords based on sector type.

    Parameters
    ----------
    sector : str
        The sector type (e.g., 'irrigation') that determines the output message
        format.
    cell_specific_option : dict
        Dictionary containing the 'lat', 'lon', 'year', and optionally 'month'
        coordinates for the specific cell, in the format:
        {
            'coords': {
                'lat': float,
                'lon': float,
                'year': int,
                'month': int (optional)
            }
        }
    flag : bool
        If True, the function prints the coordinates information; if False,
        the function does not print anything.

    Returns
    -------
    None
        This function only prints the information.
    """
    if flag:
        coords = cell_specific_option['coords']
        lat = coords['lat']
        lon = coords['lon']
        year = coords['year']
        month = coords.get('month', None)

        if sector in ["irrigation", "total"]:
            # For sectors that use both year and month
            print(f"{sector} results for grid cell with lat: {lat}, "
                  f"lon: {lon},\n"
                  f"year: {year}, month: {month}")
        elif sector in ["domestic", "manufacturing", "thermal_power",
                        "livestock"]:
            # For sectors that use only the year
            print(f"{sector} results for grid cell with lat: {lat}, "
                  f"lon: {lon},\n"
                  f"year: {year}")
        print("-------------------------------------------------------------")


def get_np_coords_cell_idx(xr_data, sector, cell_specific_option, flag):
    """
    Get NumPy indices for nearest lat, lon, and time in the xarray dataset.

    Parameters
    ----------
    xr_data : xarray.DataArray or xarray.Dataset
        The xarray object containing the data to find coordinates in.
    sector : str
        The sector type (e.g., 'irrigation') used to determine the date format.
    cell_specific_option : dict
        Dictionary with 'lat', 'lon', 'year', and optional 'month' to locate
        a specific cell's data:
        {   'flag': bool,
            'coords': {
                'lat': float,
                'lon': float,
                'year': int,
                'month': int (optional)
            }
        }
    flag : bool
        If True, coordinates are searched for, otherwise None is returned.

    Returns
    -------
    tuple
        A tuple of indices (time_idx, lat_idx, lon_idx) for the nearest time,
        latitude, and longitude.
    """
    if flag:
        # Extract coordinate information from the cell_specific_option dict
        coords = cell_specific_option['coords']
        lat = coords['lat']  # Latitude of the specific cell
        lon = coords['lon']  # Longitude of the specific cell
        year = coords['year']  # Year of the specific cell
        month = coords.get('month', None)  # Month is optional, might be None

        # Determine the date based on sector and availability of 'month'
        if sector in ["irrigation", "total"] and month:
            # Timestamp for month-specific cases
            date = pd.Timestamp(f'{year}-{month:02d}-01')
        else:
            # Timestamp for start of the year
            date = pd.Timestamp(f'{year}-01-01')

        # Select the nearest point based on lat, lon, and time
        selected_data = xr_data.sel(
            lat=lat, lon=lon, time=date, method='nearest'
            )
        # Find the NumPy indices of the nearest time coordinate
        time_idx = np.where(
            xr_data.coords['time'].values ==
            np.datetime64(selected_data.coords['time'].values)
            )[0][0]

        # Find the NumPy indices for latitude and longitude
        lat_idx = np.where(
            xr_data.coords['lat'].values == selected_data.coords['lat'].values
            )[0][0]
        lon_idx = np.where(
            xr_data.coords['lon'].values == selected_data.coords['lon'].values
            )[0][0]

        # Return the indices and the actual coordinates
        return (time_idx, lat_idx, lon_idx)
    else:
        # If flag is False, return None
        return None, None


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
