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
# INPUT DATA MANAGER MAIN FUNCTION
# =============================================================================


def input_data_manager(config):
    """
    Manage loading, checking and pre-processing of input data from a config.

    Parameters
    ----------
    config : ConfigHandler
        Singleton instance of ConfigHandler with configuration settings:
        - input_data_path (str):
            Path to the folder containing NetCDF files.
        - convention_path (str):
            Path to file with conventions and sector
          requirements.
        Additional settings are used within check_and_preprocess_input_data for
        check and preprocess input data.

    Returns
    -------
    preprocessed_data : dict
        A nested dictionary with sectors as keys, and each sector containing
        a dictionary of variables with checked & preprocessed xarray.Dataset
        objects as values.
    check_logs : dict
        Dictionary containing the results of the validation process for the
        input data.
    datasets_dict : dict of dict of xarray.Dataset
        A nested dictionary with sectors as keys, and each sector containing
        a dictionary of variables with loaded xarray.Dataset objects as values.
    conventions : dict
        Loaded conventions and sector requirements.

    Notes
    -----
    This function performs the following steps:
    1. Loads conventions from the specified path.
    2. Loads input data from the specified folder according to sector
       requirements.
    3. Checks and preprocesses the input data, using additional settings from
       config.
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
    conventions : dict
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
    datasets_dict : dict of dict of xarray.Dataset
        A nested dictionary with sectors as keys, and each sector containing
        a dictionary of variables with xarray.Dataset objects as values.
    """
    datasets_dict = {}
    # Loop through each sector in the input directory
    for sector in os.listdir(input_data_path):
        # Skip sectors not in the requirements dictionary
        if sector not in sector_requirements:
            continue
        sector_path = os.path.join(input_data_path, sector)
        expected_vars = sector_requirements[sector]['expected_vars']

        # Check if the sector path is a directory
        if os.path.isdir(sector_path):
            datasets_dict[sector] = {}  # Initialize a dictionary for sector

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
                        datasets_dict[sector][variable] = dataset
                        # Log a debug message for successful file loading
                        logger.debug(
                            f".nc-files loaded for '{sector}/{variable}'."
                        )

    return datasets_dict

# =============================================================================
# HANDLING FUNCTION FOR INPUT DATA CHECK RESULTS
# =============================================================================


def check_results_handling(check_logs):
    """
    Handle input data check results by logging and aborting if necessary.

    Parameters
    ----------
    check_logs : dict
        Dictionary containing the results of the validation process for the
        input data. Each key represents a category of potential data issues,
        with values indicating the check results:

        - "too_many_vars" (list): List of files where multiple variables were
          detected, though only one was expected.
        - "time_resolution_mismatch" (list): List of files with mismatched time
          resolutions, compared to the expected configuration.
        - "missing_time_coords" (list): List of files missing required time
          coordinates.
        - "missing_time_coverage" (list): List of files with incomplete time
          coverage as per configuration.
        - "extended_time_period" (list): List of files with extended time
          coverage, which may compensate for missing time coverage.
        - "unit_mismatch" (list): List of files where units do not match the
          expected sector-specific units.
        - "unknown_vars" (list): List of variables not recognized according to
          reference standards in `input_data_convention.json`.
        - "missing_unit" (list): List of variables lacking unit definitions,
          which are required by sector specifications.
        - "lat_lon_consistency" (bool): Indicates whether spatial coordinates
          are consistent across all input data (True if consistent, False
          otherwise).

    """
    critical_error_found = False

    # Handle critical errors
    # Process each category in the check results
    for category, result in check_logs.items():
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
                    set(check_logs["missing_time_coverage"])
                extended_paths = \
                    set(check_logs["extended_time_period"])
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
            if category == "extended_time_period":
                pass
            else:
                logger.debug(f"{category}: No issues detected")

    # Check if critical errors were found and exit the program if necessary
    if critical_error_found:
        logger.critical(
            "Critical errors were found during input data checks. "
            "Exiting program.")
        sys.exit(1)
