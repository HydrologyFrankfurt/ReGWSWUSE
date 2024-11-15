# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE preprocessing functions for input_data_check_preprocessing."""

import dask
import xarray as xr
import pandas as pd
import numpy as np


# =============================================================
# PREPROCESSING FUCNTIONS
# =============================================================
def ensure_correct_dimension_order(data):
    """
    Ensure the dimensions of an xarray object are in the correct order.

    This function checks and, if necessary, transposes the dimensions of the
    input xarray object to follow the preferred order of ("time", "lat", "lon")
    if "time" is present or ("lat", "lon") otherwise.

    Parameters
    ----------
    data : xarray.DataArray or xarray.Dataset
        The xarray object to check and transpose if necessary.

    Returns
    -------
    data : xarray.DataArray or xarray.Dataset
        The xarray object with dimensions in the desired order.
    """
    # Get the current dimensions of the xarray object
    current_dims = tuple(data.dims)

    # Check if 'time' is a dimension
    if 'time' in current_dims:
        # Desired order if 'time' is present
        desired_dims = ("time", "lat", "lon")
    else:
        # Desired order if 'time' is not present
        desired_dims = ("lat", "lon")

    # Check if current dimensions match the desired order
    if current_dims != desired_dims:
        # Transpose the xarray object to the desired order
        data = data.transpose(*desired_dims)

    # Return the transposed xarray object
    return data


def sort_lat_desc_lon_asc_coords(data):
    """
    Sort xarray object latitude descending and longitude ascending.

    Parameters
    ----------
    data : xarray.DataArray or xarray.Dataset
        The xarray object whose 'lat' and 'lon' coordinates are to be sorted.

    Returns
    -------
    sorted_lat_desc_lon_asc_data : xarray.DataArray or xarray.Dataset
        The xarray object with 'lat' coordinates sorted in descending order
        and 'lon' coordinates sorted in ascending order, or the original object
        if already sorted.
    """
    if 'lat' not in data.coords or 'lon' not in data.coords:
        raise ValueError("'lat' or 'lon' coords miss in dataset.")

    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        sorted_lat_desc_data = data.sortby('lat', ascending=False)

        sorted_lat_desc_lon_asc_data = \
            sorted_lat_desc_data.sortby('lon', ascending=True)

    return sorted_lat_desc_lon_asc_data


def trim_xr_data(data, start_year, end_year):
    """
    Trim DataArray to cover the specified period.

    Parameters
    ----------
    data : xr.DataArray
        The original DataArray with time values.
    start_year : int
        The year from which the trimming begins.
    end_year : int
        The year until which the trimming continues.

    Returns
    -------
    trimmed_data : xr.DataArray
        The trimmed DataArray.
    """
    trimmed_data = data.sel(time=slice(str(start_year), str(end_year)))
    return trimmed_data


def extend_xr_data(data, start_year, end_year, time_freq):
    """
    Extend DataArray or Dataset to cover the specified period.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset with time values.
    start_year : int
        The year from which the extension begins.
    end_year : int
        The year until which the extension continues.
    time_freq : str
        The frequency of the adjusted time coordinates, either 'monthly' or
        'yearly', corresponding to 'MS' or 'YS'.

    Returns
    -------
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset.
    """
    original_time = data.coords['time']
    start_date, end_date = f'{start_year}-01-01', f'{end_year}-12-31'
    freq = 'MS' if time_freq == 'monthly' else 'YS'
    target_time = pd.date_range(start=start_date, end=end_date, freq=freq)

    extended_data = initialize_extended_data(data, target_time)

    number_time_slices = 12 if freq == 'MS' else 1

    extended_data = append_data_to_start(
        data, extended_data, target_time, number_time_slices
        )
    extended_data = append_data_to_end(
        data, extended_data, target_time, number_time_slices
        )
    extended_data = insert_original_data(data, extended_data, original_time)

    return extended_data


def initialize_extended_data(data, target_time):
    """
    Initialize an extended DataArray or Dataset to match the target time.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    target_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.

    Returns
    -------
    extended_data : xr.DataArray or xr.Dataset
        The initialized extended DataArray or Dataset.
    """
    if isinstance(data, xr.DataArray):
        extended_data = xr.DataArray(
            np.empty((len(target_time), *data.shape[1:])),
            coords=[target_time, *list(data.coords.values())[1:]],
            dims=data.dims
        )
    elif isinstance(data, xr.Dataset):
        extended_data = xr.Dataset(
            {var: (data.dims, np.empty((len(target_time), *data.shape[1:])))
             for var, data in data.data_vars.items()},
            coords={coord: ([coord], target_time) if coord == 'time' else
                    (coord, data.values)
                    for coord, data in data.coords.items()}
        )
    return extended_data


def append_data_to_start(data, extended_data, target_time, number_time_slices):
    """
    Append data to the start of the extended DataArray or Dataset.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    target_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.
    number_time_slices : int
        The number of time slices to append at each step.

    Returns
    -------
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset after data has been appended to the
        start.
    """
    for i in range(0, len(target_time), number_time_slices):
        if target_time[i] >= data.coords['time'][0]:
            break
        if isinstance(data, xr.DataArray):
            extended_data[i:i+number_time_slices] = (
                data.isel(time=slice(0, number_time_slices)).values
            )
        elif isinstance(data, xr.Dataset):
            for var in data.data_vars:
                extended_data[var][i:i+number_time_slices] = (
                    data[var].isel(time=slice(0, number_time_slices)).values
                )
    return extended_data


def append_data_to_end(data, extended_data, target_time, number_time_slices):
    """
    Append data to the end of the extended DataArray or Dataset.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    target_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.
    number_time_slices : int
        The number of time slices to append at each step.

    Returns
    -------
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset after data has been appended to the
        end.
    """
    for i in range(len(target_time) - number_time_slices, -1,
                   -number_time_slices):
        if target_time[i] <= data.coords['time'][-1]:
            break
        if isinstance(data, xr.DataArray):
            extended_data[i:i+number_time_slices] = (
                data.isel(time=slice(-number_time_slices, None)).values
            )
        elif isinstance(data, xr.Dataset):
            for var in data.data_vars:
                extended_data[var][i:i+number_time_slices] = (
                    data[var].isel(time=slice(-number_time_slices, None)
                                   ).values)

    return extended_data


def insert_original_data(data, extended_data, original_time):
    """
    Insert the original data into the extended DataArray or Dataset.

    Parameters
    ----------
    data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    original_time : xr.DataArray
        The time coordinates of the original DataArray or Dataset.

    Returns
    -------
    extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset with original data inserted.
    """
    original_time_index = extended_data.time.to_index().get_indexer(
        original_time.to_index()
    )
    if isinstance(data, xr.DataArray):
        extended_data[original_time_index] = data.values
    elif isinstance(data, xr.Dataset):
        for var in data.data_vars:
            extended_data[var][original_time_index] = data[var].values

    return extended_data
