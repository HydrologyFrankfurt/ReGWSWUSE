# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""
GWSWUSE input data check & preprocessing module for input_data_manager.
"""
import os
import dask
import xarray as xr
import pandas as pd
import numpy as np

from controller import configuration_module as cm


# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = (os.path.basename(__file__))
modname = modname.split('.')[0]


# =============================================================
# CHECK FUNCTIONS
# =============================================================


def check_variable_metadata(dataset,
                            reference_names, expected_units, unit_vars):
    """
    Check if a dataset's variables have expected names and units.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset to be checked.
    reference_names : list
        List of expected variable names.
    expected_units : str
        The expected units for the variables.
    unit_vars : list
        List of variables that should have units.

    Returns
    -------
    unknown_name : bool
        True if any variable has an unknown name.
    incorrect_unit : bool
        True if any variable has incorrect or missing units.
    """
    unknown_name_flag = False
    incorrect_unit_flag = False

    for var_name, data_var in dataset.data_vars.items():
        if var_name not in reference_names:
            unknown_name_flag = True

        if var_name in unit_vars:
            if 'units' in data_var.attrs:
                if expected_units and data_var.attrs['units'] != expected_units:
                    incorrect_unit_flag = True
            else:
                incorrect_unit_flag = True

    return unknown_name_flag, incorrect_unit_flag


def check_lat_lon_coords(dataset, lat_lon_reference):
    """
    Check if the dataset's lat/lon coordinates match the reference.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset to be checked.
    lat_lon_reference : tuple of numpy.ndarray or None
        The reference lat/lon coordinates to compare against.

    Returns
    -------
    lat_lon_reference : tuple of numpy.ndarray
        Updated reference lat/lon coordinates.
    lat_lon_check_flag : bool
        True if latitude coordinates match the reference.
    """
    lat_lon_check_flag = True

    if 'lat' in dataset.coords and 'lon' in dataset.coords:
        lat = dataset.coords['lat'].values
        lon = dataset.coords['lon'].values

        if lat_lon_reference is None:
            lat_lon_reference = (lat, lon)
        else:
            if not np.array_equal(lat, lat_lon_reference[0]):
                lat_lon_check_flag = False
            if not np.array_equal(lon, lat_lon_reference[1]):
                lat_lon_check_flag = False
    else:
        lat_lon_check_flag = False

    return lat_lon_reference, lat_lon_check_flag


def check_time_coords(dataset, time_freq, start_year, end_year):
    """
    Check if a dataset covers the period and has correct time resolution.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset to be checked.
    time_unit : str
        The time unit of the dataset ('monthly' or 'annual').
    start_year : int
        The start year of the period to be checked.
    end_year : int
        The end year of the period to be checked.

    Returns
    -------
    not_covering_period_flag : bool
        True if the dataset does not cover the specified period.
    incorrect_resolution_flag : bool
        True if the dataset has incorrect time resolution.
    """
    not_covering_period_flag = False
    incorrect_resolution_flag = False

    if 'time' in dataset.coords:
        time_values = pd.to_datetime(dataset.coords['time'].values)
        time_years = time_values.year

        if time_freq == 'monthly':
            expected_times = pd.date_range(
                start=f'{min(time_years)}-01-01', end=f'{max(time_years)}-12-31', freq='MS'
            )
        elif time_freq == 'annual':
            expected_times = pd.date_range(
                start=f'{min(time_years)}-01-01', end=f'{max(time_years)}-12-31', freq='YS'
            )

        if not set(expected_times).issubset(set(time_values)):
            incorrect_resolution_flag = True

        if min(time_years) > start_year or max(time_years) < end_year:
            not_covering_period_flag = True
    else:
        not_covering_period_flag = True

    return not_covering_period_flag, incorrect_resolution_flag


def check_t_aai_mode_compatibility(end_year,
                                   time_extend_mode, irr_consumptive_use_tot):
    """
    Check the compatibility of t_aai_mode with end_year and irr_cu_tot.

    This function checks whether the correction mode `correct_with_t_aai_mode`
    can be used based on the `end_year` and the availability of required input
    data. The correction mode is only compatible if the `end_year` is 2016 or
    later and the time period of the input data for `irr_consumptive_use_tot`
    extends to at least 2016, given that `time_extend_mode` is False.

    Parameters
    ----------
        Flag indicating if the correction with t_aai_mode is enabled.
    end_year : int
        The end year for the data processing.
    time_extend_mode : bool
        Flag indicating if the data is extended to include years before the
        start year and after the end year.
    irr_consumptive_use_tot : xarray.DataArray or xarray.Dataset
        Irrigation-specific consumptive use from total water resources.

    Returns
    -------
        The potentially updated flag indicating if the correction with
        t_aai_mode is enabled.
    t_aai_correction_mode_compatibility_flag : bool
        Flag indicating if the `correct_with_t_aai_mode` is compatible with the
        given `end_year` and input data.
    """
    t_aai_correction_mode_compatibility_flag = True

    if cm.correct_irr_t_aai_mode:
        if end_year < 2016:
            cm.correct_irr_t_aai_mode = False
            t_aai_correction_mode_compatibility_flag = False
            print('The configuration correct_with_t_aai_mode can´t be used for'
                  ' a simulation period that ends before 2016.')
        elif (irr_consumptive_use_tot.time[-1].values <
              np.datetime64('2016-01-01') and not time_extend_mode):
            cm.correct_irr_t_aai_mode = False
            t_aai_correction_mode_compatibility_flag = False
            print('Available time period of input data for '
                  'irr.consumptive_use_tot is not compatible with '
                  'correct_with_t_aai_mode')

    return (cm.correct_irr_t_aai_mode,
            t_aai_correction_mode_compatibility_flag)


# =============================================================
# PREPROCESSING FUNCTION
# =============================================================
def ensure_correct_dimension_order(xr_data):
    """
    Ensure the dimensions of an xarray object are in the correct order.

    The function automatically checks if the 'time' dimension is present
    and rearranges the dimensions accordingly.

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
        sorted_lat_desc = xr_data.sortby('lat', ascending=False)
        sorted_lat_desc_lon_asc = sorted_lat_desc.sortby('lon', ascending=True)

    return sorted_lat_desc_lon_asc


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

    append_data_to_start(
        xr_data, xr_extended_data, simulation_time, number_time_slices
    )
    append_data_to_end(
        xr_data, xr_extended_data, simulation_time, number_time_slices
    )
    insert_original_data(xr_data, xr_extended_data, xr_data_time)

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
            {var: (data.dims, np.empty((len(simulation_time), *data.shape[1:]))
                   )
             for var, data in xr_data.data_vars.items()},
            coords={coord: ([coord], simulation_time) if coord == 'time' else
                    (coord, data.values)
                    for coord, data in xr_data.coords.items()}
        )
    return xr_extended_data


def append_data_to_start(xr_data, xr_extended_data, simulation_time,
                         number_time_slices):
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


def append_data_to_end(xr_data, xr_extended_data, simulation_time,
                       number_time_slices):
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

# =============================================================
# UTILITY FUNCTIONS
# =============================================================


def get_dataset_by_sector_and_variable(datasets, target_sector,
                                       target_variable):
    """
    Extract the dataset for given sector and variable from a list of tuples.

    Parameters
    ----------
    datasets : list of tuples
        A list containing tuples of (dataset, sector, variable).
    target_sector : str
        The sector to filter by.
    target_variable : str
        The variable to filter by.

    Returns
    -------
    dataset
        The dataset that matches the specified sector and variable.
    """
    for dataset, sector, variable in datasets:
        if sector == target_sector and variable == target_variable:
            return dataset
    return None

# =============================================================
# CHECK AND PREPROCESSING ALGORITHM
# =============================================================

def check_and_preprocess_input_data(datasets,
                                    conventions,
                                    start_year,
                                    end_year,
                                    time_extend_mode):
    """
    Check and preprocess algorithm of input datasets.

    Parameters
    ----------
    datasets : list of tuples
        A list containing tuples of (dataset, sector, variable).
    conventions : dict
        A dictionary containing conventions and sector requirements.
    start_year : int
        The start year for the data processing.
    end_year : int
        The end year for the data processing.
    time_extend_mode : bool
        If True, the data is extended to include years before the start year
        and after the end year. If False, the data is trimmed to the specified
        date range.

    Returns
    -------
    preprocessed_datasets : dict
        A dictionary of preprocessed datasets by sector and variable.
    check_results : dict
        A dictionary containing results of the checks performed on the input
        data.

    Notes
    -----
    This function performs the following steps:
    1. Initializes conventions and check flags.
    2. Checks compatibility of `t_aai_mode` with the end year and input data.
    3. Checks if dataset variable names are in reference variable names and
       units of unit variables.
    4. Logs datasets that do not pass the checks for variable names and units.
    5. Sorts spatial coordinates in each dataset.
    6. Checks whether spatial coordinates in every dataset are the same
       (necessary for model simulation).
    7. Checks only time-variant variable datasets for correct time resolution
       and if the dataset covers the simulation period.
    8. Extends not-covering-period datasets with original data of the first
       and last year, if the time resolution of the data is correct.
    9. Trims datasets to the specified period if they cover the simulation
       period.
    10. Adds preprocessed datasets to the results dictionary.
    11. Creates and returns a dictionary of check results.
    """
    # initialize conventions
    reference_names = conventions['reference_names']
    time_variant_vars = conventions['time_variant_vars']
    sector_requirements = conventions['sector_requirements']

    # initialize flag and reference for lat lon check
    lat_lon_check_flag = True
    lat_lon_reference = None
    # initialize flag for compatibility check of t_aai
    t_aai_correction_mode_compatibility_flag = True
    # initialize list for logging data that does not pass the checks
    list_unknown_names_data = []
    list_incorrect_units_data = []
    list_not_covering_period_data = []
    list_incorrect_resolution_data = []

    # initialize dict for processed_datasets
    preprocessed_datasets = {}
    if cm.correct_irr_t_aai_mode:
        (cm.correct_irr_t_aai_mode,
         t_aai_correction_mode_compatibility_flag) = \
            check_t_aai_mode_compatibility(
                end_year,
                time_extend_mode,
                get_dataset_by_sector_and_variable(datasets,
                                                   'irrigation',
                                                   'consumptive_use_tot')
                )

    for dataset, sector, variable in datasets:

        # get input_subfolder_path for dataset for logging
        folder_path = sector + '/' + variable
        # =====================================================================
        # get sector-specific input conventions
        sector_info = sector_requirements.get(sector, {})
        expected_units = sector_info.get("expected_units")
        unit_vars = sector_info.get("unit_vars", [])
        time_freq = sector_info.get("time_freq")
        # =====================================================================
        # check variable name and unit in dataset
        unknown_name_flag, incorrect_unit_flag = \
            check_variable_metadata(dataset,
                                    reference_names, expected_units, unit_vars)

        # list datasets with not expected variable name and incorrect unit
        if unknown_name_flag:
            list_unknown_names_data.append(folder_path)
        if incorrect_unit_flag:
            list_unknown_names_data.append(folder_path)
        # =====================================================================
        # preprocessing and checking the spatial coordinates
        dataset = sort_lat_desc_lon_asc_coords(dataset)

        lat_lon_reference, lat_lon_check_flag = \
            check_lat_lon_coords(dataset, lat_lon_reference)
        # =====================================================================
        # check if dataset covers the period and has correct time resolution.

        # trim dataset to simulation period if it exceeds the period

        # extend dataset if time_extend_mode is true and
        # it does not cover the period but time resolution is correct
        if variable in time_variant_vars:
            not_covering_period_flag, incorrect_resolution_flag = \
                check_time_coords(dataset,
                                  time_freq, start_year, end_year)
            # list dataset with incorrect time resolution
            if incorrect_resolution_flag:
                list_incorrect_resolution_data.append(folder_path)

            if not_covering_period_flag:
                if incorrect_resolution_flag:
                    if variable == 'time_factor_aai':
                        if cm.correct_irr_t_aai_mode:
                            dataset = \
                                extend_xr_data(dataset, start_year, end_year,
                                               time_freq)
                            not_covering_period_flag = False
                        else:
                            not_covering_period_flag = False
                    elif time_extend_mode:
                        dataset = extend_xr_data(dataset, start_year, end_year,
                                                 time_freq)
                        not_covering_period_flag = False
            else:
                dataset = trim_xr_data(dataset, start_year, end_year)
        # list not_covering_period_datasets for logging
            if not_covering_period_flag:
                list_not_covering_period_data.append(folder_path)
        # =====================================================================
        # ensure correct dimension order
        dataset = ensure_correct_dimension_order(dataset)
        # =====================================================================
        if sector not in preprocessed_datasets:
            preprocessed_datasets[sector] = {}
        preprocessed_datasets[sector][variable] = \
            next(iter(dataset.data_vars.values()))  # from xr.ds to xr.array
    check_results = \
        {"Input data with unknown variable names": list_unknown_names_data,
         "Input data with incorrect units": list_incorrect_units_data,
         "Input data which not covers simulation period": (
             list_not_covering_period_data),
         "Input data with incorrect time resolution": (
             list_incorrect_resolution_data),
         "Compatibility of lat and lon coords is given": lat_lon_check_flag,
         "Compatibility of correct_irr_t_aai_mode is given": (
             t_aai_correction_mode_compatibility_flag)
         }

    return preprocessed_datasets, check_results
# def check_and_preprocess_input_data(datasets,
#                                     conventions,
#                                     start_year,
#                                     end_year,
#                                     time_extend_mode,
#                                     correct_irr_t_aai_mode):
#     """
#     Check and preprocess algorithm of input datasets.

#     Parameters
#     ----------
#     datasets : list of tuples
#         A list containing tuples of (dataset, sector, variable).
#     conventions : dict
#         A dictionary containing conventions and sector requirements.
#     start_year : int
#         The start year for the data processing.
#     end_year : int
#         The end year for the data processing.
#     time_extend_mode : bool
#         If True, the data is extended to include years before the start year
#         and after the end year. If False, the data is trimmed to the specified
#         date range.

#     Returns
#     -------
#     preprocessed_datasets : dict
#         A dictionary of preprocessed datasets by sector and variable.
#     check_results : dict
#         A dictionary containing results of the checks performed on the input
#         data.

#     Notes
#     -----
#     This function performs the following steps:
#     1. Initializes conventions and check flags.
#     2. Checks compatibility of `t_aai_mode` with the end year and input data.
#     3. Checks if dataset variable names are in reference variable names and
#        units of unit variables.
#     4. Logs datasets that do not pass the checks for variable names and units.
#     5. Sorts spatial coordinates in each dataset.
#     6. Checks whether spatial coordinates in every dataset are the same
#        (necessary for model simulation).
#     7. Checks only time-variant variable datasets for correct time resolution
#        and if the dataset covers the simulation period.
#     8. Extends not-covering-period datasets with original data of the first
#        and last year, if the time resolution of the data is correct.
#     9. Trims datasets to the specified period if they cover the simulation
#        period.
#     10. Adds preprocessed datasets to the results dictionary.
#     11. Creates and returns a dictionary of check results.
#     """
#     # initialize conventions
#     reference_names = conventions['reference_names']
#     time_variant_vars = conventions['time_variant_vars']
#     sector_requirements = conventions['sector_requirements']

#     # initialize flag and reference for lat lon check
#     lat_lon_check_flag = True
#     lat_lon_reference = None
#     # initialize flag for compatibility check of t_aai
#     t_aai_correction_mode_compatibility_flag = True
#     # initialize list for logging data that does not pass the checks
#     list_unknown_names_data = []
#     list_incorrect_units_data = []
#     list_not_covering_period_data = []
#     list_incorrect_resolution_data = []

#     # initialize dict for processed_datasets
#     preprocessed_datasets = {}

#     if correct_irr_t_aai_mode:
#         (correct_irr_t_aai_mode,
#          t_aai_correction_mode_compatibility_flag) = \
#             check_t_aai_mode_compatibility(
#                 correct_irr_t_aai_mode,
#                 end_year,
#                 time_extend_mode,
#                 get_dataset_by_sector_and_variable(datasets,
#                                                    'irrigation',
#                                                    'consumptive_use_tot')
#                 )
#     for dataset, sector, variable in datasets:
#         if variable == "time_factor_aai":
            
#             continue
#         # print(sector + '/' + variable)
#         folder_path = sector + '/' + variable

#         sector_info = sector_requirements.get(sector, {})
#         expected_units = sector_info.get("expected_units")
#         unit_vars = sector_info.get("unit_vars", [])
#         time_freq = sector_info.get("time_freq")

#         # check if dataset's variables have expected names and units
#         unknown_name_flag, incorrect_unit_flag = \
#             check_variable_metadata(dataset,
#                                     reference_names, expected_units, unit_vars)

#         # list if checks not passed
#         if unknown_name_flag:
#             list_unknown_names_data.append(folder_path)
#         if incorrect_unit_flag:
#             list_unknown_names_data.append(folder_path)

#         # preprocess with regard to spatial coords
#         dataset = sort_lat_desc_lon_asc_coords(dataset)
#         # check if 'lat' & 'lon' coords match the coords of rest input data
#         lat_lon_reference, lat_lon_check_flag = \
#             check_lat_lon_coords(dataset, lat_lon_reference)

#         # check if dataset covers the period and has correct time resolution.
#         if variable in time_variant_vars:
#             not_covering_period_flag, incorrect_resolution_flag = \
#                 check_time_coords(dataset,
#                                   time_freq, start_year, end_year)

#             if incorrect_resolution_flag:
#                 if not variable == 'time_factor_aai':
#                     list_incorrect_resolution_data.append(folder_path)

#             if not_covering_period_flag:
#                 # list_not_covering_period_data.append(folder_path)
#                 # preprocess xr_data with regard to the time dimension
#                 if time_extend_mode and not incorrect_resolution_flag:
#                     dataset = \
#                         extend_xr_data(dataset, start_year, end_year,
#                                        time_freq)
#                 if variable == 'time_factor_aai' and correct_irr_t_aai_mode:
#                     extend_xr_data(dataset, start_year, end_year,
#                                    time_freq)
#                 else:
#                     list_not_covering_period_data.append(folder_path)
#             else:
#                 dataset = trim_xr_data(dataset, start_year, end_year)

#         if sector not in preprocessed_datasets:
#             preprocessed_datasets[sector] = {}
#         preprocessed_datasets[sector][variable] = \
#             next(iter(dataset.data_vars.values()))  # dataset.to_array()

#     check_results = \
#         {"unknown_names_data": list_unknown_names_data,
#          "incorrect_units_data": list_incorrect_units_data,
#          "not_covering_period_data": list_not_covering_period_data,
#          "incorrect_resolution_data": list_incorrect_resolution_data,
#          "compatibility of lat and lon coords": lat_lon_check_flag,
#          "compatibility of correct_irr_t_aai_mode": (
#              t_aai_correction_mode_compatibility_flag)
#          }

#     return preprocessed_datasets, check_results
