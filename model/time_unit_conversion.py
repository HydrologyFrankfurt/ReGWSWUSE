# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""
GWSWUSE module with unit and data structure convert functions.
"""
import os
import numpy as np

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]

#                  =================================
#                  ||    UNIT CONVERT FUNCTIONS   ||
#                  =================================


def convert_yearly_to_monthly(annual_m3_year_data):
    """
    Convert yearly values from m³/yearly to monthly values in m³/month.

    Parameters
    ----------
    annual_m3_year_data: numpy.ndarray
        Array containing data for each year with unit m3/year. The shape of the
        array should be (num_years, size_lat_coords, size_lon_coords).

    Returns
    -------
    monthly_m3_month_data: numpy.ndarray
        Array containing converted data for each month with unit m3/month. The
        shape of the array will be (num_years * 12, size_lat_coords,
        size_lon_coords).
    """
    monthly_m3_year_array = expand_array_size(annual_m3_year_data)

    days_per_month = \
        np.array([31.0, 28.0, 31.0, 30.0,
                  31.0, 30.0, 31.0, 31.0,
                  30.0, 31.0, 30.0, 31.0], dtype=np.float64)
    num_years = annual_m3_year_data.shape[0]
    days_per_month = np.tile(days_per_month, num_years)
    days_per_month_reshaped = days_per_month[:, None, None]
    monthly_part_of_year = days_per_month_reshaped/365.0
    monthly_m3_month_data = monthly_m3_year_array * monthly_part_of_year

    return monthly_m3_month_data


def convert_monthly_to_yearly(monthly_m3_month_data):
    """
    Convert monthly values in m³/month to yearly values in m³/year.

    Parameters
    ----------
    monthly_m3_month_data: numpy.ndarray
        Array containing data for each month with unit m3/month. The shape of
        the array should be (num_years * 12, size_lat_coords, size_lon_coords).

    Returns
    -------
    monthly_m3_year_data: numpy.ndarray
        Array containing converted data for each month with unit m3/year. The
        shape of the array will be (num_years, size_lat_coords,
        size_lon_coords).
    """
    # calculate number of years
    num_years = monthly_m3_month_data.shape[0] // 12
    lat_size = monthly_m3_month_data.shape[1]
    lon_size = monthly_m3_month_data.shape[2]

    yearly_m3_year_data = np.full((num_years, lat_size, lon_size), np.nan)
    for year in range(num_years):
        start_idx = year * 12
        end_idx = start_idx + 12
        yearly_m3_year_data[year] = \
            np.sum(monthly_m3_month_data[start_idx:end_idx], axis=0)

    return yearly_m3_year_data


def expand_array_size(annual_array):
    """
    Expand annual data to monthly resolution.

    This function takes an array of annual data in m³/day and converts it into
    an array with monthly resolution by repeating the annual values for each
    month.

    Parameters
    ----------
    annual_array : numpy.ndarray
        Array containing data for each year. The shape of the array should be
        (num_years, size_lat_coords, size_lon_coords).

    Returns
    -------
    monthly_array : numpy.ndarray
        Array containing data for each month. The shape of the array will be
        (num_years * 12, size_lat_coords, size_lon_coords).
    """
    # Set number of month per year
    num_month_per_year = 12

    # Determine the shape of the annual array
    num_years, size_lat_coords, size_lon_coords = annual_array.shape

    # Initialize the monthly array
    monthly_array = \
        np.empty((num_years * num_month_per_year,
                  size_lat_coords,
                  size_lon_coords),
                 dtype=annual_array.dtype)

    # Repeat the annual data for each month of the year
    for year in range(num_years):
        for month in range(num_month_per_year):
            monthly_array[year * num_month_per_year + month, :, :] = \
                annual_array[year, :, :]

    return monthly_array
