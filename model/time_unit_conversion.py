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
from numba import njit
import numpy as np
import pandas as pd

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = (os.path.basename(__file__))
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
    yearly_m3_year_data: numpy.ndarray
        Array containing converted data for each year with unit m3/year. The
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


def convert_monthly_to_daily(monthly_data):
    """
    Convert data array unit from m3/month to m3/day.

    Convert monthly water volume data from cubic meters per month to cubic
    meters per day, assuming each month's length as per a non-gregorian
    calendar with February always having 28 days.

    Parameters
    ----------
    monthly_data: np.ndarray
        The NumPy array containing monthly water volumes in cubic meters for
        the period of entire years.

    Returns
    -------
    daily_data : np.ndarray
        The NumPy array with water volumes converted to cubic meters per day.
    """
    # Number of days in each month; February is always 28 days
    days_per_month = \
        np.array([31.0, 28.0, 31.0, 30.0,
                  31.0, 30.0, 31.0, 31.0,
                  30.0, 31.0, 30.0, 31.0], dtype=np.int32)
    num_years = int(monthly_data.shape[0] // 12)
    # Replicate this array to match the total number of years in the data
    days_per_month = np.tile(days_per_month, num_years)
    days_per_month_reshaped = days_per_month[:, None, None]

    # Convert monthly data to daily data by dividing by the number of days in
    # each month
    daily_data = monthly_data / days_per_month_reshaped

    return daily_data


# convert_sect_annual_to_daily
@njit(cache = True)
def convert_yearly_to_daily(yearly_data):
    """
    Convert water volume from cubic meters per year to cubic meters per day.

    The function is used for the following sectors:
        - Domestic
        - Manufacturing
        - Thermal Power
        - Livestock

    This function divides the input xarray DataArray containing water volumes
    in m³ per year by the number of days per year to convert it to m³ per day.

    Parameters
    ----------
    yearly_data : np.ndarray
        The DataArray containing water volumes in cubic meters per year.
    days_per_year : int, optional
        Number of days per year to use for conversion, defaults to 365.

    Returns
    -------
    daily_data : xr.DataArray
        The DataArray with water volumes converted to cubic meters per day.
    """
    days_per_year = 365
    daily_data = yearly_data / days_per_year
    return daily_data


def convert_daily_to_monthly(monthly_array_with_daily_values):
    """
    Convert data array unit from m3/month to m3/day.

    Convert monthly water volume data from cubic meters per month to cubic
    meters per day, assuming each month's length as per a non-gregorian
    calendar with February always having 28 days.

    Parameters
    ----------
    monthly_data: np.ndarray
        The NumPy array containing monthly water volumes in cubic meters for
        the period of entire years.

    Returns
    -------
    daily_data : np.ndarray
        The NumPy array with water volumes converted to cubic meters per day.
    """
    # Number of days in each month; February is always 28 days
    days_per_month = \
        np.array([31.0, 28.0, 31.0, 30.0,
                  31.0, 30.0, 31.0, 31.0,
                  30.0, 31.0, 30.0, 31.0])
    num_years = int(monthly_array_with_daily_values.shape[0] / 12.0)
    # Replicate this array to match the total number of years in the data
    days_per_month = np.tile(days_per_month, num_years)
    days_per_month_reshaped = days_per_month[:, None, None]

    monthly_array_values = \
        monthly_array_with_daily_values * days_per_month_reshaped

    return monthly_array_values


def get_time_step_in_array(array, start_year, end_year):
    """
    Determine the time step frequency in the given array.

    This function calculates the time step frequency (monthly or yearly)
    of the given array based on the number of time steps and the simulation
    period from start_year to end_year. It raises a ValueError if the number
    of time steps does not match the expected 'monthly' or 'yearly' data.

    Parameters
    ----------
    array : numpy.ndarray
        The input array where the first dimension represents time steps.
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.

    Returns
    -------
    tuple
        A tuple containing the time step frequency ('monthly' or 'yearly')
        and the number of simulation years.

    Raises
    ------
    ValueError
        If the number of time steps does not match the expected 'monthly'
        or 'yearly' data.
    """
    sim_num_years = (end_year + 1) - start_year

    num_of_time_steps = array.shape[0]
    if num_of_time_steps/12 == sim_num_years:
        time_step = 'monthly'
    elif num_of_time_steps == sim_num_years:
        time_step = 'yearly'
    else:
        raise ValueError("The number of time steps does not match the expected"
                         "'monthly' or 'yearly' data.")

    return time_step, sim_num_years


def convert_daily_to_yearly(daily_values_array, start_year, end_year):
    """
    Convert daily values from m³/day to yearly values in m³/year.

    This function converts an array of daily values (m³/day) to yearly values
    (m³/year) based on the provided simulation period from start_year to
    end_year. The function handles both yearly and monthly time steps.

    Parameters
    ----------
    daily_values_array : numpy.ndarray
        The input array of daily values with dimensions [time, lat, lon].
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.

    Returns
    -------
    numpy.ndarray
        The converted array of yearly values with dimensions [years, lat, lon].

    Raises
    ------
    ValueError
        If the number of time steps in the input array does not match the
        expected 'monthly' or 'yearly' data.
    """
    time_step, sim_num_years = get_time_step_in_array(daily_values_array,
                                                      start_year,
                                                      end_year)
    lat_size = daily_values_array.shape[1]
    lon_size = daily_values_array.shape[2]

    if time_step == 'yearly':
        yearly_values = daily_values_array * 365.0

    elif time_step == 'monthly':
        monthly_values = convert_daily_to_monthly(daily_values_array)
        yearly_values = np.full((sim_num_years, lat_size, lon_size), np.nan)
        for year in range(sim_num_years):
            start_idx = year * 12
            end_idx = start_idx + 12
            yearly_values[year] = np.sum(monthly_values[start_idx:end_idx],
                                         axis=0)

    return yearly_values


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

    # Initialisieren des monatlichen Arrays
    monthly_array = \
        np.empty((num_years * num_month_per_year,
                  size_lat_coords,
                  size_lon_coords),
                 dtype=annual_array.dtype)

    # Wiederholen der jährlichen Daten für jeden Monat des Jahres
    for year in range(num_years):
        for month in range(num_month_per_year):
            monthly_array[year * num_month_per_year + month, :, :] = \
                annual_array[year, :, :]

    return monthly_array


def get_np_coords_cell_output(xr_data, sector, cell_specific_output):
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