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
def ensure_correct_dimension_order(xr_data):
    """
    Ensure the dimensions of an xarray object are in the correct order.

    Parameters
    ----------
    xr_array : xarray.DataArray or xarray.Dataset
        The xarray object to check and transpose if necessary.

    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The xarray object with dimensions in the desired order.
    """
    # Get the current dimensions of the xarray object
    current_dims = tuple(xr_data.dims)

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
        xr_data = xr_data.transpose(*desired_dims)

    # Return the transposed xarray object
    return xr_data


def sort_lat_desc_lon_asc_coords(xr_data):
    """
    Sort xarray object latitude descending and longitude ascending.

    Parameters
    ----------
    xr_data : xarray.DataArray or xarray.Dataset
        The xarray object whose 'lat' and 'lon' coordinates are to be sorted.

    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The xarray object with 'lat' coordinates sorted in descending order
        and 'lon' coordinates sorted in ascending order.
    """
    if 'lat' not in xr_data.coords or 'lon' not in xr_data.coords:
        raise ValueError("'lat' oder 'lon' Koordinaten fehlen im Dataset.")

    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        sorted_lat_desc_xr_data = xr_data.sortby('lat', ascending=False)

        sorted_lat_desc_lon_asc_xr_data = \
            sorted_lat_desc_xr_data.sortby('lon', ascending=True)

    return sorted_lat_desc_lon_asc_xr_data


def trim_xr_data(xr_data, start_year, end_year):
    """
    Trim DataArray to cover the specified period.

    Parameters
    ----------
    xr_data : xr.DataArray
        The original DataArray with time values.
    start_year : int
        The year from which the trimming begins.
    end_year : int
        The year until which the trimming continues.

    Returns
    -------
    xr.DataArray
        The trimmed DataArray.
    """
    return xr_data.sel(time=slice(str(start_year), str(end_year)))


def extend_xr_data(xr_data, start_year, end_year, time_freq):
    """
    Extend DataArray or Dataset to cover the specified period.

    Parameters
    ----------
    xr_data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset with time values.
    start_year : int
        The year from which the extension begins.
    end_year : int
        The year until which the extension continues.
    time_freq : str
        The frequency of the adjusted time coordinates, either 'MS' for
        monthly or 'YS' for yearly.

    Returns
    -------
    xr.DataArray or xr.Dataset
        The extended DataArray or Dataset.
    """
    xr_data_time = xr_data.coords['time']
    start_date, end_date = f'{start_year}-01-01', f'{end_year}-12-31'
    freq = 'MS' if time_freq == 'monthly' else 'YS'
    simulation_time = pd.date_range(start=start_date, end=end_date, freq=freq)

    xr_extended_data = initialize_extended_data(xr_data, simulation_time)

    number_time_slices = 12 if freq == 'MS' else 1

    xr_extended_data = append_data_to_start(
        xr_data, xr_extended_data, simulation_time, number_time_slices
        )
    xr_extended_data = append_data_to_end(
        xr_data, xr_extended_data, simulation_time, number_time_slices
        )
    xr_extended_data = insert_original_data(xr_data,
                                            xr_extended_data,
                                            xr_data_time)

    return xr_extended_data


def initialize_extended_data(xr_data, simulation_time):
    """
    Initialize an extended DataArray or Dataset to match the simulation time.

    Parameters
    ----------
    xr_data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    simulation_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.

    Returns
    -------
    xr.DataArray or xr.Dataset
        The initialized extended DataArray or Dataset.
    """
    if isinstance(xr_data, xr.DataArray):
        xr_extended_data = xr.DataArray(
            np.empty((len(simulation_time), *xr_data.shape[1:])),
            coords=[simulation_time, *list(xr_data.coords.values())[1:]],
            dims=xr_data.dims
        )
    elif isinstance(xr_data, xr.Dataset):
        xr_extended_data = xr.Dataset(
            {var: (data.dims, np.empty((len(simulation_time), *data.shape[1:])))
             for var, data in xr_data.data_vars.items()},
            coords={coord: ([coord], simulation_time) if coord == 'time' else
                    (coord, data.values)
                    for coord, data in xr_data.coords.items()}
        )
    return xr_extended_data


def append_data_to_start(
        xr_data, xr_extended_data, simulation_time, number_time_slices
        ):
    """
    Append data to the start of the extended DataArray or Dataset.

    Parameters
    ----------
    xr_data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    xr_extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    simulation_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.
    number_time_slices : int
        The number of time slices to append at each step.
    """
    for i in range(0, len(simulation_time), number_time_slices):
        if simulation_time[i] >= xr_data.coords['time'][0]:
            break
        if isinstance(xr_data, xr.DataArray):
            xr_extended_data[i:i+number_time_slices] = (
                xr_data.isel(time=slice(0, number_time_slices)).values
            )
        elif isinstance(xr_data, xr.Dataset):
            for var in xr_data.data_vars:
                xr_extended_data[var][i:i+number_time_slices] = (
                    xr_data[var].isel(time=slice(0, number_time_slices)).values
                )
    return xr_extended_data


def append_data_to_end(
        xr_data, xr_extended_data, simulation_time, number_time_slices
        ):
    """
    Append data to the end of the extended DataArray or Dataset.

    Parameters
    ----------
    xr_data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    xr_extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    simulation_time : pd.DatetimeIndex
        The time coordinates for the extended DataArray or Dataset.
    number_time_slices : int
        The number of time slices to append at each step.
    """
    for i in range(len(simulation_time) - number_time_slices, -1,
                   -number_time_slices):
        if simulation_time[i] <= xr_data.coords['time'][-1]:
            break
        if isinstance(xr_data, xr.DataArray):
            xr_extended_data[i:i+number_time_slices] = (
                xr_data.isel(time=slice(-number_time_slices, None)).values
            )
        elif isinstance(xr_data, xr.Dataset):
            for var in xr_data.data_vars:
                xr_extended_data[var][i:i+number_time_slices] = (
                    xr_data[var].isel(time=slice(-number_time_slices, None)
                                      ).values)

    return xr_extended_data


def insert_original_data(xr_data, xr_extended_data, xr_data_time):
    """
    Insert the original data into the extended DataArray or Dataset.

    Parameters
    ----------
    xr_data : xr.DataArray or xr.Dataset
        The original DataArray or Dataset.
    xr_extended_data : xr.DataArray or xr.Dataset
        The extended DataArray or Dataset being built.
    xr_data_time : xr.DataArray
        The time coordinates of the original DataArray or Dataset.
    """
    original_time_index = xr_extended_data.time.to_index().get_indexer(
        xr_data_time.to_index()
    )
    if isinstance(xr_data, xr.DataArray):
        xr_extended_data[original_time_index] = xr_data.values
    elif isinstance(xr_data, xr.Dataset):
        for var in xr_data.data_vars:
            xr_extended_data[var][original_time_index] = xr_data[var].values

    return xr_extended_data