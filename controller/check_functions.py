# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE check functions for input_data_check_preprocessing."""

import pandas as pd
import numpy as np
from gwswuse_logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# CHECK FUNCTIONS
# =============================================================================
def check_dataset_structure_metadata(
        dataset, variable, reference_names, unit_vars, expected_units, log_id,
        check_logs
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
    check_logs : dict
        A dictionary used for tracking validation results, including issues
        with the variable name or units.

    Returns
    -------
    check_logs : dict
        The updated check_logs reflecting any detected issues during validation
        of variable numbers, variable name and unit.
    """
    # Check if only one variable exists in the dataset
    if len(dataset.data_vars) != 1:
        check_logs.setdefault("too_many_vars", []).append(log_id)

    # Check the first variable in the dataset
    first_var_name, first_data_var = next(iter(dataset.data_vars.items()))

    # Log if the variable name is not in the reference list
    if first_var_name not in reference_names:
        check_logs.setdefault("unknown_vars", []).append(log_id)

    # Log if the variable has incorrect or missing units (if applicable)
    if variable in unit_vars:
        if 'units' in first_data_var.attrs:
            if expected_units and first_data_var.attrs['units'] not in \
                expected_units:
                check_logs.setdefault("unit_mismatch", []).append(log_id)
        else:
            check_logs.setdefault("missing_unit", []).append(log_id)

    return check_logs


def check_spatial_coords(dataset, check_logs):
    """
    Check if the dataset's latitude and longitude coords match a reference.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset containing latitude ('lat') and longitude ('lon')
        coordinates to be checked.
    check_logs : dict
        A dictionary used for tracking validation results. It contains:
        - "lat_lon_reference": tuple of numpy.ndarray or None
            The reference latitude and longitude coordinates to compare
            against.
        - "lat_lon_check_flag": bool
            A flag indicating if latitude and longitude coordinates are
            consistent across datasets.

    Returns
    -------
    check_logs : dict
        The updated check_logs reflecting any detected issues with latitude and
        longitude consistency.
    """
    if 'lat' in dataset.coords and 'lon' in dataset.coords:
        lat = dataset.coords['lat'].values
        lon = dataset.coords['lon'].values

        if check_logs["lat_lon_reference"] is None:
            check_logs["lat_lon_reference"] = (lat, lon)
        else:
            if not np.array_equal(lat, check_logs["lat_lon_reference"][0]):
                check_logs["lat_lon_consistency"] = False
            if not np.array_equal(lon, check_logs["lat_lon_reference"][1]):
                check_logs["lat_lon_consistency"] = False
    else:
        check_logs["lat_lon_consistency"] = False

    return check_logs


def check_time_coords(
        data, expected_frequency, start_year, end_year, log_id, check_logs):
    """
    Validate the time coordinates of a dataset and log issues.

    This function checks the presence of 'time' coordinates in the dataset,
    validates that the dataset's time coverage and resolution match the
    expected frequency and the required simulation period. If issues are found,
    they are logged.

    Parameters
    ----------
    data : xarray.Dataset or xarray.DataArray
        The dataset or data array containing the time coordinates to validate.
    expected_frequency : str
        The expected time frequency, either 'monthly' or 'annual'.
    start_year : int
        The start year of the required time period.
    end_year : int
        The end year of the required time period.
    log_id : str
        A unique identifier for logging the dataset's validation results.
    check_logs : dict
        A dictionary used for tracking validation results, including issues
        with time coordinates, resolution, or coverage.

    Returns
    -------
    check_logs : dict
        The updated check_logs reflecting any detected issues during time
        coordinate validation.
    """
    if 'time' in data.coords:
        # Extract time values from coords
        data_time_points = pd.to_datetime(data.coords['time'].values)
        data_years = data_time_points.year

        if expected_frequency == 'monthly':
            time_freq_code = 'MS'
        elif expected_frequency in ['annual', 'yearly']:
            time_freq_code = 'YS'
        else:
            # Log an error if expected_frequency is invalid
            logger.error(
                f"Invalid expected_frequency '{expected_frequency}' provided "
                "from input_data_convention.json."
                "Must be either 'monthly' or 'annual'."
            )
            raise ValueError(
                "expected_frequency must be either 'monthly' or 'annual'"
            )

        # Generate expected time points for data time range
        # and expected frequency
        expected_time_points = pd.date_range(
            start=f'{min(data_years)}-01-01',
            end=f'{max(data_years)}-12-31', freq=time_freq_code
            )
        # Verify that the data´s time points cover all expected time points
        if not set(expected_time_points).issubset(set(data_time_points)):
            check_logs.setdefault("time_resolution_mismatch", []
                                  ).append(log_id)
        # Check if the data's time range fully covers required start_year to
        # end_year
        if min(data_years) > start_year or max(data_years) < end_year:
            check_logs.setdefault("missing_time_coverage", []).append(log_id)
    else:
        # Log missing time coordinates if 'time' is not in data's coordinates
        check_logs.setdefault("missing_time_coords", []).append(log_id)

    return check_logs
