# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE input data check & preprocessing module for input_data_manager."""
import os
import dask
import xarray as xr
import pandas as pd
import numpy as np


# =============================================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# =============================================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def check_dataset_structure_metadata(
        dataset, variable, reference_names, unit_vars, expected_units, log_id,
        logs
        ):
    """
    Validate and log metadata related to the structure of the dataset.

    This function checks whether the dataset contains only one variable,
    verifies the variable's name against the reference names, and checks if the
    variable has the correct units. It logs any discrepancies (e.g., multiple
    variables, unknown variable names, missing or incorrect units).

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset containing variables to validate.
    variable : str
        The specific variable being validated.
    reference_names : list of str
        The expected variable names for validation.
    unit_vars : list of str
        A list of variables that should have units.
    expected_units : str
        The expected units for the variable.
    log_id : str
        A unique identifier for logging the dataset's validation results.
    logs : dict
        A dictionary used for tracking validation results, including issues
        with the variable name or units.

    Returns
    -------
    dict
        The updated logs reflecting any detected issues during validation.
    """
    # Check if only one variable exists in the dataset
    if len(dataset.data_vars) != 1:
        logs.setdefault("multiple_variables", []).append(log_id)

    # Check the first variable in the dataset
    first_var_name, first_data_var = next(iter(dataset.data_vars.items()))

    # Log if the variable name is not in the reference list
    if first_var_name not in reference_names:
        logs.setdefault("unknown_names", []).append(log_id)

    # Log if the variable has incorrect or missing units (if applicable)
    if variable in unit_vars:
        if 'units' in first_data_var.attrs:
            if expected_units and first_data_var.attrs['units'] != expected_units:
                logs.setdefault("incorrect_units", []).append(log_id)
        else:
            logs.setdefault("missing_unit", []).append(log_id)

    return logs


def check_spatial_coords(dataset, logs):
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
    logs : dict
        The updated logs reflecting any detected issues during validation.
    """
    if 'lat' in dataset.coords and 'lon' in dataset.coords:
        lat = dataset.coords['lat'].values
        lon = dataset.coords['lon'].values

        if logs["lat_lon_reference"] is None:
            logs["lat_lon_reference"] = (lat, lon)
        else:
            if not np.array_equal(lat, logs["lat_lon_reference"][0]):
                logs["lat_lon_check_flag"] = False
            if not np.array_equal(lon, logs["lat_lon_reference"][1]):
                logs["lat_lon_check_flag"] = False
    else:
        logs["lat_lon_check_flag"] = False

    return logs


def check_time_coords(dataset, time_freq, start_year, end_year, log_id, logs):
    """
    Validate the time coordinates of a dataset and log issues.

    This function checks the presence of 'time' coordinates in the dataset,
    validates that the dataset's time coverage and resolution match the
    expected frequency and the required simulation period. If issues are found,
    they are logged.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset containing the time coordinates to validate.
    time_freq : str
        The expected time frequency, either 'monthly' or 'annual'.
    start_year : int
        The start year of the required time period.
    end_year : int
        The end year of the required time period.
    log_id : str
        A unique identifier for logging the dataset's validation results.
    logs : dict
        A dictionary used for tracking validation results, including issues
        with time coordinates, resolution, or coverage.

    Returns
    -------
    logs : dict
        The updated logs reflecting any detected issues during time coordinate
        validation.
    """
    if 'time' in dataset.coords:
        time_values = pd.to_datetime(dataset.coords['time'].values)
        time_years = time_values.year

        if time_freq == 'monthly':
            expected_times = pd.date_range(
                start=f'{min(time_years)}-01-01',
                end=f'{max(time_years)}-12-31', freq='MS'
            )
        elif time_freq == 'annual':
            expected_times = pd.date_range(
                start=f'{min(time_years)}-01-01',
                end=f'{max(time_years)}-12-31', freq='YS'
            )

        if not set(expected_times).issubset(set(time_values)):
            logs.setdefault("incorrect_time_resolution", []).append(log_id)

        if min(time_years) > start_year or max(time_years) < end_year:
            logs.setdefault("not_covering_period", []).append(log_id)
    else:
        logs.setdefault("missing_time_coords", []).append(log_id)

    return logs


# =============================================================
# PREPROCESSING FUCNTIONS
# =============================================================
def ensure_correct_dimension_order(xr_data):
    """
    Ensure the dimensions of an xarray object are in the correct order.

    The function automatically checks if the 'time' dimension is present and
    rearranges the dimensions accordingly.

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
# =============================================================
# UTILITY FUNCTIONS
# =============================================================


def initialize_logs():
    """Initialize the logs for tracking issues with datasets."""
    return {
        "multiple_variables": [],  # decisive
        "unknown_names": [],  # not decisive
        "incorrect_units": [],
        "missing_unit": [],
        "lat_lon_check_flag": True,  # decisive
        "lat_lon_reference": None,  # only needed for check_spatial_coords
        "not_covering_period": [],  # decisive, if time_extend_mode disabled
        "incorrect_time_resolution": [],  # decisive
        "missing_time_coords": [],  # decisive
        "time_extended_data": []  # only information
    }


def generate_validation_results(logs):
    """
    Generate the results of checks and logs performed on datasets.

    Parameters
    ----------
    logs : dict
        The dictionary containing log information about various dataset issues.

    Returns
    -------
    dict
        A dictionary summarizing the results of the checks.
    """
    return {
        "Input data with unknown variable names": logs["unknown_names"],
        "Input data with incorrect units": logs["incorrect_units"],
        "Input data with missing units": logs["missing_unit"],
        "Input data with multiple variables": logs["multiple_variables"],
        "Input data which does not cover simulation period":
            logs["not_covering_period"],
        "Input data with incorrect time resolution":
            logs["incorrect_time_resolution"],
        "Input data with missing time coordinates":
            logs["missing_time_coords"],
        "Input data with extended time to cover simulation period":
            logs["time_extended_data"],
        "Compatibility of lat and lon coords is given":
            logs["lat_lon_check_flag"],
    }


def store_preprocessed_dataset(preprocessed_datasets, sector, variable,
                               dataset, expected_unit):
    """Store preprocessed datasets by sector and variable."""
    if sector not in preprocessed_datasets:
        preprocessed_datasets[sector] = {}
        preprocessed_datasets[sector]['unit'] = expected_unit

    # Store the variable in the processed dataset
    preprocessed_datasets[sector][variable] = \
        next(iter(dataset.data_vars.values()))

    return preprocessed_datasets


def check_preprocess_time_variant_input(
        dataset, start_year, end_year, time_freq, time_extend_mode, log_id,
        logs):
    """
    Validate and preprocess time-variant input data for a given period.

    This function performs validation of the time coverage and resolution of
    the input dataset. If the dataset does not cover the required period and
    `time_extend_mode` is enabled, the dataset will be extended. Otherwise,
    the dataset is trimmed to match the required time period.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset containing time-variant data to validate and preprocess.
    start_year : int
        The start year of the required time period.
    end_year : int
        The end year of the required time period.
    time_freq : str
        The expected time frequency (e.g., 'D' for daily, 'M' for monthly).
    time_extend_mode : bool
        Flag to enable extending the dataset if it does not cover the full
        period.
    log_id : str
        A unique identifier for logging the dataset's validation results.
    logs : dict
        A dictionary used for tracking validation results and preprocessing
        steps.

    Returns
    -------
    dataset : xarray.Dataset)
        The preprocessed dataset, either extended or trimmed.
    logs : dict
        The updated logs reflecting the validation and preprocessing results.
    """
    # Step 1: (Validation) Validate time coverage and resolution and log
    logs = check_time_coords(
        dataset, time_freq, start_year, end_year, log_id, logs)
    # Step 2a: Handle dataset depending on whether it covers the period
    if log_id in logs["not_covering_period"] and time_extend_mode:
        # 2a: (Preprocessing) Extend dataset if time_extend_mode is enabled
        dataset = extend_xr_data(dataset, start_year, end_year, time_freq)
        logs["time_extended_data"].append(log_id)
    # Step 2b: (Preprocessing) Trim dataset if it covers the required period
    else:
        dataset = trim_xr_data(dataset, start_year, end_year)

    return dataset, logs


# =============================================================
# CHECK AND PREPROCESSING MAIN ALGORITHM
# =============================================================

def check_and_preprocess_input_data(
        datasets, conventions, start_year, end_year, time_extend_mode
        ):
    """
    Validate and preprocess input datasets based on input conventions.

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
    logs : dict
        A dictionary containing results of validation process of the input
        data.
    """
    # Initialize conventions
    reference_names = conventions['reference_names']
    time_variant_vars = conventions['time_variant_vars']
    sector_requirements = conventions['sector_requirements']

    # Initialize logs for storing information about incorrect datasets
    logs = initialize_logs()

    # Initialize the dictionary for preprocessed datasets
    preprocessed_datasets = {}

    # Validate and process each dataset in the input
    for dataset, sector, variable in datasets:
        log_id = f"{sector}/{variable}"
        # get sector-specific input conventions
        sector_info = sector_requirements.get(sector, {})
        unit_vars = sector_info.get("unit_vars", [])
        expected_units = sector_info.get("expected_units")
        time_freq = sector_info.get("time_freq")

        # Validate and process general aspects of the dataset
        logs = \
            check_dataset_structure_metadata(
                dataset, variable, reference_names, unit_vars, expected_units,
                log_id, logs
                )

        # Sort spatial coords: latitude descending, longitude ascending
        dataset = sort_lat_desc_lon_asc_coords(dataset)
        # Validate that spatial coords are same in all datasets
        logs = \
            check_spatial_coords(dataset, logs)

        if variable in time_variant_vars:
            # Validate and preprocess time aspects of dataset
            dataset, logs = check_preprocess_time_variant_input(
                dataset, start_year, end_year, time_freq, time_extend_mode,
                log_id, logs)

        # Ensure correct dimension order
        dataset = ensure_correct_dimension_order(dataset)
        # Store preprocessed dataset in dictionairy
        preprocessed_datasets = \
            store_preprocessed_dataset(
                preprocessed_datasets, sector, variable, dataset,
                expected_units[0])

    # return preprocessed_datasets, logs
    validation_results = generate_validation_results(logs)

    return preprocessed_datasets, validation_results
