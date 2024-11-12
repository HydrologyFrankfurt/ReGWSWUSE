# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:35:56 2024

@author: lniss
"""
import xarray as xr
import numpy as np

# Erstelle Latitude- und Longitude-Koordinaten mit einer Auflösung von 0.5°
latitudes = np.arange(-89.75, 89.75, 0.5)  # von -90° bis +90°
longitudes = np.arange(-179.75, 179.75, 0.5)  # von -180° bis +180°

# Erstelle ein leeres DataArray mit den Koordinaten
lat_lon_reference = xr.DataArray(
    data=np.zeros((len(latitudes), len(longitudes))),
    coords={"latitude": latitudes, "longitude": longitudes},
    dims=["latitude", "longitude"],
    name="lat_lon_reference"
)

test_check_results_1 = {
    "too_many_vars": [],
    "unknown_vars": ["path/to/file1"],
    "unit_mismatch": ["path/to/file3"],
    "missing_unit": [
        "path/to/file1", "path/to/file4", "path/to/file5"],
    "lat_lon_consistency": True,
    "missing_time_coverage": [],
    "time_resolution_mismatch": [],
    "missing_time_coords": [],
    "extended_time_period": ["path/to/file1"]
}

test_check_results_2 = {
    "too_many_vars": [],
    "unknown_vars": [],
    "unit_mismatch": ["path/to/file3"],
    "missing_unit": [],
    "lat_lon_consistency": True,
    "missing_time_coverage": ["path/to/file5"],
    "time_resolution_mismatch": [],
    "missing_time_coords": [],
    "extended_time_period": []
}

test_check_results_2 = {
    "too_many_vars": [],
    "unknown_vars": ["path/to/file5"],
    "unit_mismatch": ["path/to/file3"],
    "missing_unit": [],
    "lat_lon_consistency": True,
    "missing_time_coverage": ["path/to/file5"],
    "time_resolution_mismatch": [],
    "missing_time_coords": [],
    "extended_time_period": []
}


import logging
import sys

# Logger setup
logger = logging.getLogger('controller.input_data_manager')
logging.basicConfig(level=logging.DEBUG)

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
    warning_flag = False

    # Define critical categories and check each
    if ("time_resolution_mismatch" in check_results and
        check_results["time_resolution_mismatch"]):

        formatted_list = \
            ("\n   - " +
             "\n   - ".join(check_results["time_resolution_mismatch"])
             )
        logger.critical(f"time_resolution_mismatch:{formatted_list}")
        critical_error_found = True

    if ("missing_time_coords" in check_results and
        check_results["missing_time_coords"]):
        formatted_list = "\n   - " + "\n   - ".join(check_results["missing_time_coords"])
        logger.critical(f"missing_time_coords:{formatted_list}")
        critical_error_found = True

    # Handle "too_many_vars" as an error that allows fallback processing
    if "too_many_vars" in check_results and check_results["too_many_vars"]:
        formatted_list = "\n   - " + "\n   - ".join(check_results["too_many_vars"])
        logger.error(
            f"too_many_vars: Multiple variables found; only the first variable "
            f"will be used. Please verify if this is correct.\n{formatted_list}"
            )
        critical_error_found = True

    # Special handling for "missing_time_coverage"
    if ("missing_time_coverage" in check_results and
        check_results["missing_time_coverage"]):
        missing_paths = set(check_results["missing_time_coverage"])
        if "extended_time_period" in check_results:
            extended_paths = set(check_results["extended_time_period"])
            unmatched_paths = missing_paths - extended_paths
            if unmatched_paths:
                formatted_unmatched = "\n   - " + "\n   - ".join(unmatched_paths)
                logger.critical(
                    f"missing_time_coverage: Missing time coverage for the "
                    f"following paths:\n{formatted_unmatched}"
                    )
                critical_error_found = True
            else:
                formatted_extended = "\n   - " + "\n   - ".join(extended_paths)
                logger.info(
                    f"missing_time_coverage: Missing time coverage but paths are "
                    f"extended:\n{formatted_extended}"
                    )
        else:
            formatted_list = "\n   - " + "\n   - ".join(check_results["missing_time_coverage"])
            logger.critical(f"missing_time_coverage:{formatted_list}")
            critical_error_found = True

    # Handle individual warning categories
    if "unknown_vars" in check_results and check_results["unknown_vars"]:
        formatted_list = "\n   - " + "\n   - ".join(check_results["unknown_vars"])
        logger.warning(
            f"unknown_vars: The standard_name in the metadata of the "
            f"NetCDF files at the following paths is not listed in the "
            f"reference_names in the input_data_convention JSON file. "
            f"Please verify that these variables are correctly defined:\n{formatted_list}"
            )
        warning_flag = True

    if "unit_mismatch" in check_results and check_results["unit_mismatch"]:
        formatted_list = "\n   - " + "\n   - ".join(check_results["unit_mismatch"])
        logger.warning(
            f"unit_mismatch: The units of variables in the NetCDF files at the "
            f"following paths do not match the expected units specified in the "
            f"input_data_convention JSON file for the given sector. Please verify "
            f"the unit definitions according to sector-specific requirements:\n{formatted_list}"
            )
        warning_flag = True

    if "missing_unit" in check_results and check_results["missing_unit"]:
        formatted_list = "\n   - " + "\n   - ".join(check_results["missing_unit"])
        logger.warning(
            f"missing_unit: Variables in the NetCDF files at the following paths "
            f"are missing unit definitions, which are specified as required for "
            f"the given sector in the input_data_convention JSON file. Please "
            f"verify that all units are correctly assigned:\n{formatted_list}"
            )
        warning_flag = True

    # Check if critical errors were found and exit the program if necessary
    if critical_error_found:
        logger.critical(
            "\nCritical errors were found during input data checks. "
            "Exiting program."
            )
        sys.exit(1)

    # Warn the user if warnings were found and suggest data verification
    if warning_flag:
        logger.warning(
            "Warning: Some input data categories have potential issues "
            "that may affect the simulation. Please review the warnings "
            "above to ensure data consistency."
        )


import logging
import sys

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
    warning_flag = False

    # Handle critical errors
    # Process each category in the check results
    for category, result in check_results.items():
        if isinstance(result, list) and result:  # Only process non-empty lists
            issues_list = "\n   - " + "\n   - ".join(result)
            critical_error_found = True
            if category == "too_many_vars":
                logger.critical(f"Multiple variables found for:{issues_list}")
            elif category == "time_resolution_mismatch":
                logger.critical(f"Time resolution mismatch for:{issues_list}")
            elif category == "missing_time_coords":
                logger.critical("Time coords was expected, but missed for:"
                                f"{issues_list}")
            elif category == "missing_time_coverage":
                # Special handling for "missing_time_coverage"
                if "extended_time_period" in check_results:
                    missing_paths = \
                        set(check_results["missing_time_coverage"])
                    extended_paths = \
                        set(check_results["extended_time_period"])
                    unmatched_paths = missing_paths - extended_paths
                    if not unmatched_paths:
                        extended_list = \
                            "\n   - " + "\n   - ".join(extended_paths)
                        logger.info(
                            "Missing time coverage but paths are extended:\n"
                            f"{extended_list}"
                            )
                else:
                    issues_list = "\n   - " + "\n   - ".join(
                        check_results["missing_time_coverage"]
                    )
                    logger.critical(f"missing_time_coverage:{issues_list}")
                    critical_error_found = True
            # Handle individual warning categories with custom messages
            elif category == "unknown_vars":
                logger.warning(
                    "unknown_vars: The standard_name in the metadata of "
                    "the NetCDF files at the following paths is not in "
                    "reference_names in the input_data_convention JSON. "
                    "Please verify these variables:\n" + issues_list
                    )
                warning_flag = True
            elif category == "unit_mismatch":
                logger.warning(
                    "unit_mismatch: The units in the NetCDF files at the "
                    "following paths do not match the expected units for "
                    "the sector in input_data_convention JSON. Verify "
                    "units per sector requirements:\n" + issues_list
                    )
                warning_flag = True
            elif category == "missing_unit":
                logger.warning(
                    "missing_unit: Variables in the NetCDF files at the "
                    "following paths are missing unit definitions, which "
                    "are required by sector in input_data_convention "
                    "JSON. Verify all units:\n" + issues_list
                    )
                warning_flag = True
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

    # Warn the user if warnings were found and suggest data verification
    if warning_flag:
        logger.warning(
            "Warning: Some input data categories have potential issues "
            "that may affect the simulation. Please review the warnings "
            "above to ensure data consistency.")
    # Check if critical errors were found and exit the program if necessary
    if critical_error_found:
        logger.critical(
            "\nCritical errors were found during input data checks. "
            "Exiting program.")
        sys.exit(1)



check_results_handling(test_check_results_1)

# print("\n\n\n\n")

# check_results_handling(test_check_results_2)

