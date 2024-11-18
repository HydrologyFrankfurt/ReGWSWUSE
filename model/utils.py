# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE utility functions for model component."""

import numpy as np
import pandas as pd
from gwswuse_logger import get_logger

logger = get_logger(__name__)


def print_cell_output_headline(sector, cell_specific_option, flag):
    """
    Log information about the selected cell's coords based on sector type.

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
        If True, the function logs the coordinates information; if False,
        the function does not log anything.

    Returns
    -------
    None
        This function only logs the information.
    """
    if flag:
        coords = cell_specific_option['coords']
        lat = coords['lat']
        lon = coords['lon']
        year = coords['year']
        month = coords.get('month', None)

        if sector in ["irrigation", "total", "cross-sector totals"]:
            # For sectors that use both year and month
            logger.info(
                "%s results for grid cell with lat: %s, lon: %s,\n"
                "year: %s, month: %s\n"
                "------------------------------------------------------------",
                sector, lat, lon, year, month
                )
        elif sector in ["domestic", "manufacturing", "thermal power",
                        "livestock"]:
            # For sectors that use only the year
            logger.info(
                "%s results for grid cell with lat: %s, lon: %s,\n"
                "year: %s\n"
                "------------------------------------------------------------",
                sector, lat, lon, year
                )


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
    return None, None


def print_cell_value(var, var_name, coords_idx=None, unit="-", flag=False):
    """
    Log value of the variable for specific cell indices.

    Parameters
    ----------
    var : numpy.ndarray, float, or int
        The variable whose value you want to log. It can be a 1D, 2D, 3D
        array or a scalar (float/int).
    var_name : str
        The name of the variable as a string, which will be loged alongside
        the value.
    coords_idx : tuple or list, optional
        A tuple or list containing the indices (time_idx, lat_idx, lon_idx) for
        3D arrays, or (lat_idx, lon_idx) for 2D arrays. For 1D arrays, this is
        ignored. If var is a scalar, this is ignored.
        - For 3D arrays: (time_idx, lat_idx, lon_idx)
        - For 2D arrays: (lat_idx, lon_idx)
    unit : str, optional
        The unit of the variable (default is "-"). This will be appended to the
        logged value.
    flag : bool, optional
        If True, the function will log the value. If False, the function will
        do nothing. Default is False.
    """

    if flag:
        # Check if var is a scalar (int, float)
        if isinstance(var, (float, int)):
            logger.info("%s [%s]: %s", var_name, unit, var)

        # If var is a numpy array, handle based on its dimensions
        elif hasattr(var, 'ndim'):
            if var.ndim == 3:
                logger.info(
                    "%s [%s]: %s", var_name, unit,
                    var[coords_idx[0], coords_idx[1], coords_idx[2]]
                    )
            elif var.ndim == 2:
                logger.info(
                    "%s [%s]: %s", var_name, unit,
                    var[coords_idx[1], coords_idx[2]]
                    )
            elif var.ndim == 1:
                logger.info("%s [%s]: %s", var_name, unit, var[0])
            else:
                logger.info("%s [%s]: %s", var_name, unit, var)
        else:
            logger.info("%s [%s]: %s", var_name, unit, var)


def test_net_abstraction_tot(
        consumptive_use_tot, net_abstraction_gw, net_abstraction_sw,
        sector
        ):
    """
    Verify if total consumptive use matches net abstraction totals.

    This function checks if the calculated total net abstraction
    (`net_abstraction_gw + net_abstraction_sw`) is nearly equal to the
    `consumptive_use_tot` for a given sector. If the values match within an
    absolute tolerance (1e-4) and relative tolerance (0.1%) while ignoring NaN
    values, the test passes. If tolerances are exceeded, a warning is issued.

    Parameters
    ----------
    consumptive_use_tot : np.ndarray
        Array representing the total consumptive water use for a sector.
    net_abstraction_gw : np.ndarray
        Array for groundwater net abstraction.
    net_abstraction_sw : np.ndarray
        Array for surface water net abstraction.
    sector : str
        Name of the sector being tested (e.g., 'Agriculture', 'Industry').

    Returns
    -------
    None
        Logs test results and warnings to the console.
    """
    # Calculate net_abstraction_tot
    net_abstraction_tot = net_abstraction_gw + net_abstraction_sw

    # First, use np.allclose to check if the arrays are nearly equal
    if np.allclose(
            net_abstraction_tot, consumptive_use_tot, equal_nan=True
            ):
        logger.debug(
            "Test for %s passed: Consumptive use in total is equal to net "
            "abstraction in total (ignoring NaN values).\n", sector
            )
    elif not np.allclose(
            net_abstraction_tot, consumptive_use_tot, rtol=1e-03, atol=1e-04,
            equal_nan=True
            ):
        logger.warning(
            "Test for %s failed: Consumptive use in total is not equal to net "
            "abstraction in total. Relative tolerance of 0.1%% and absolute "
            "tolerance of 0.0001 were exceeded!\n", sector
            )
