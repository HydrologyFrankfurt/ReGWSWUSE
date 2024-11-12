# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Input data manager."""

import sys
import os
import glob
import json
import xarray as xr
from gwswuse_logger import get_logger
from controller.input_data_check_preprocessing import \
    check_and_preprocess_input_data

# =============================================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# =============================================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]

logger = get_logger(__name__)

# =============================================================================
# LOAD CONVENTION DICT AND INPUT DATA
# =============================================================================


def load_conventions(convention_path):
    """
    Load conventions from a JSON file.

    Parameters
    ----------
    convention_path : str
        Path to the JSON file containing the conventions.

    Returns
    -------
    dict
        Dictionary of conventions loaded from the JSON file.
    """
    try:
        with open(convention_path, encoding="utf-8") as convention_file:
            conventions = json.load(convention_file)
    except FileNotFoundError:
        logger.critical("Input data convention file not found.")  # Logging
        sys.exit()

    return conventions


def load_netcdf_files(input_data_path, sector_requirements):
    """
    Load NetCDF files by sector and variable into a nested dictionary.

    Parameters
    ----------
    input_data_path : str
        Path to the folder containing NetCDF files organized by sector
        and variable.
    sector_requirements : dict
        Dictionary containing expected sectors and variables.

    Returns
    -------
    dict
        A nested dictionary with sectors as keys, and each sector containing
        a dictionary of variables with xarray.Dataset objects as values.
    """
    datasets = {}
    # Loop through each sector in the input directory
    for sector in os.listdir(input_data_path):
        # Skip sectors not in the requirements dictionary
        if sector not in sector_requirements:
            continue
        sector_path = os.path.join(input_data_path, sector)
        expected_vars = sector_requirements[sector]['expected_vars']

        # Check if the sector path is a directory
        if os.path.isdir(sector_path):
            datasets[sector] = {}  # Initialize a dictionary for the sector

            # Loop through each variable in the sector directory
            for variable in os.listdir(sector_path):
                # Skip variables not in the expected list for the sector
                if variable not in expected_vars:
                    continue
                variable_path = os.path.join(sector_path, variable)

                # Check if the variable path is a directory
                if os.path.isdir(variable_path):
                    # Get a list of all .nc files in the variable directory
                    netcdf_files = \
                        glob.glob(os.path.join(variable_path, '*.nc'))

                    # If .nc files are found, load them as an xarray Dataset
                    if netcdf_files:
                        dataset = xr.open_mfdataset(
                            netcdf_files, combine='by_coords'
                        )
                        datasets[sector][variable] = dataset
                        # Log a debug message for successful file loading
                        logger.debug(
                            f".nc-files loaded for '{sector}/{variable}'."
                        )

    return datasets

# =============================================================================
# HANDLING FUNCTION FOR INPUT DATA CHECK RESULTS
# =============================================================================


def check_results_handling(check_results):
    """
    Handle input data check results by logging and aborting if necessary.

    Parameters
    ----------
    check_results : dict
        Dictionary containing the results of dataset checks, categorized by
        issue type.
    """
    critical_error_found = False

    # Handle critical errors
    # Process each category in the check results
    for category, result in check_results.items():
        if isinstance(result, list) and result:  # Only process non-empty lists
            issues_list = "\n   - " + "\n   - ".join(result)
            if category == "too_many_vars":
                logger.critical(f"Multiple variables found:{issues_list}")
                critical_error_found = True
            elif category == "time_resolution_mismatch":
                logger.critical(f"Time resolution mismatch:{issues_list}")
                critical_error_found = True
            elif category == "missing_time_coords":
                logger.critical("Time coordinates missing:"
                                f"{issues_list}")
                critical_error_found = True
            elif category == "missing_time_coverage":
                missing_paths = \
                    set(check_results["missing_time_coverage"])
                extended_paths = \
                    set(check_results["extended_time_period"])
                unmatched_paths = missing_paths - extended_paths
                if not unmatched_paths:
                    extended_list = \
                        "\n   - " + "\n   - ".join(extended_paths)
                    logger.info(
                        "Time coverage missing but data are extended:\n"
                        f"{extended_list}"
                        )
                else:
                    logger.critical(f"Time coverage missing for:{issues_list}")
                    critical_error_found = True
            # Handle individual warning categories with custom messages
            elif category == "unit_mismatch":
                logger.error(
                    "Unit mismatch:\n Units in these files do not match "
                    "expected units for the sector as per "
                    "input_data_convention.json.\n Please verify:"
                    f"{issues_list}"
                    )
            elif category == "unknown_vars":
                logger.warning(
                    "Unknown variables:\n The following variables are not in "
                    "reference_names as specified in input_data_convention"
                    f".json.\n Please verify:{issues_list}"
                    )
            elif category == "missing_unit":
                logger.warning(
                    "Missing units:\n The following variables lack unit "
                    "definitions required by sector as per "
                    "input_data_convention.json.\n Please verify:"
                    f"{issues_list}"
                    )
        elif isinstance(result, bool):
            # Handle lat/lon consistency check
            if category == "lat_lon_consistency":
                if not result:
                    logger.critical(
                        "Spatial coordinates are not equal for all input data"
                        )
                    critical_error_found = True
                else:
                    logger.debug(f"{category}: {result}")

        elif isinstance(result, list) and not result:
            # Empty lists are only informational
            logger.debug(f"{category}: No issues detected")

    # Check if critical errors were found and exit the program if necessary
    if critical_error_found:
        logger.critical(
            "Critical errors were found during input data checks. "
            "Exiting program.")
        sys.exit(1)

# =============================================================================
# INPUT DATA MANAGER MAIN FUNCTION
# =============================================================================


def input_data_manager(config):
    """
    Manage the loading, checking and pre-processing of input data.

    Parameters
    ----------
    input_data_path : str
        Path to the folder containing the input NetCDF files.
    convention_path : str
        Path to the file containing conventions and sector requirements.
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
    datasets : dict
        A dictionary of loaded NetCDF datasets.
    conventions : dict
        The loaded conventions and sector requirements.
    preprocessed_data : xr.DataArray or xr.Dataset
        The preprocessed data.
    check_results : dict
        Results of the checks performed on the input data.

    Notes
    -----
    This function performs the following steps:
    1. Loads conventions from the specified path.
    2. Loads input data from the specified folder according to sector
       requirements.
    3. Checks and preprocesses the input data.
    4. Handle the results of input data checks.
    """
    # Confirm paths for input data and conventions
    logger.debug("Using input data path: %s", config.input_data_path)
    logger.debug("Loading conventions from: %s", config.convention_path)

    # load conventions
    logger.debug("Loading input data conventions...")
    conventions = load_conventions(config.convention_path)
    sector_requirements = conventions['sector_requirements']
    logger.debug("Input data conventions loaded successfully.")

    # load input data
    logger.debug("Loading input data from NetCDF files...")
    datasets_dict = \
        load_netcdf_files(config.input_data_path, sector_requirements)
    logger.debug("Input data loading completed.")

    # check and preprocess input_data
    logger.debug("Starting input data check and preprocessing...")
    preprocessed_data, check_logs = check_and_preprocess_input_data(
        datasets_dict, conventions, config
        )

    check_results_handling(check_logs)
    logger.debug("Input data check and preprocessing completed.\n")

    return preprocessed_data, check_logs, datasets_dict, conventions
