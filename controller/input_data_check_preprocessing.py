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

from controller.check_functions import (
    check_dataset_structure_metadata, check_spatial_coords, check_time_coords)

from controller.preprocessing_functions import (
    extend_xr_data, trim_xr_data, ensure_correct_dimension_order,
    sort_lat_desc_lon_asc_coords
    )

# =============================================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# =============================================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


# =============================================================
# CHECK AND PREPROCESSING MAIN ALGORITHMS
# =============================================================


def check_and_preprocess_input_data(
        datasets, conventions, config
        ):
    """
    Validate and preprocess input datasets based on input conventions.

    Parameters
    ----------
    datasets : dict
        A nested dictionary with sectors as keys and each sector containing
        a dictionary of variables with xarray.Dataset objects as values.
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
    validation_results : dict
        A dictionary containing results of the validation process of the input
        data.
    """
    # Initialize conventions
    reference_names = conventions['reference_names']
    time_variant_vars = conventions['time_variant_vars']
    sector_requirements = conventions['sector_requirements']

    # Initialize logs for storing information about incorrect datasets
    check_logs = initialize_logs()

    datasets = preprocess_input_data_based_on_config(
        datasets, config)
    # Initialize the dictionary for preprocessed datasets
    preprocessed_datasets = {}

    # Validate and process each dataset in the nested dictionary structure
    for sector, variables in datasets.items():
        sector_info = sector_requirements.get(sector, {})
        unit_vars = sector_info.get("unit_vars", [])
        expected_units = sector_info.get("expected_units", [])
        time_freq = sector_info.get("time_freq", None)

        # Create entry for sector in preprocessed_datasets with unit
        # if it doesn't exist
        if sector not in preprocessed_datasets:
            preprocessed_datasets[sector] = \
                {'unit': expected_units[0] if expected_units else None}

        for variable, dataset in variables.items():
            log_id = f"{sector}/{variable}"

            # Set all dataset data to float64
            dataset = dataset.astype('float64')

            # Validate and process general aspects of the dataset
            check_logs = check_dataset_structure_metadata(
                dataset, variable, reference_names, unit_vars, expected_units,
                log_id, check_logs
            )

            # Sort spatial coords: latitude descending, longitude ascending
            dataset = sort_lat_desc_lon_asc_coords(dataset)

            # Validate that spatial coords are same in all datasets
            check_logs = check_spatial_coords(dataset, check_logs)

            # Validate and preprocess time aspects of dataset
            if variable in time_variant_vars:
                dataset, check_logs = check_preprocess_time_variant_input(
                    dataset, check_logs, log_id, time_freq, config
                    )

            # Ensure correct dimension order
            dataset = ensure_correct_dimension_order(dataset)

            # Store the preprocessed dataset in the dictionary
            preprocessed_datasets[sector][variable] = next(
                iter(dataset.data_vars.values())
                )

    check_logs.pop("lat_lon_reference", None)

    return preprocessed_datasets, check_logs

# =============================================================
# CHECK AND PREPROCESSING SUB ALGORITHMS
# =============================================================


def check_preprocess_time_variant_input(
        dataset, logs, log_id, time_freq, config):
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
    start_year = config.start_year
    end_year = config.end_year
    time_extend_mode = config.time_extend_mode
    # Step 1: (Validation) Validate time coverage and resolution and log
    logs = check_time_coords(
        dataset, time_freq, start_year, end_year, log_id, logs)
    # Step 2a: Handle dataset depending on whether it covers the period
    if log_id in logs["missing_time_coverage"] and time_extend_mode:
        # 2a: (Preprocessing) Extend dataset if time_extend_mode is enabled
        dataset = extend_xr_data(dataset, start_year, end_year, time_freq)
        logs["extended_time_period"].append(log_id)
    # Step 2b: (Preprocessing) Trim dataset if it covers the required period
    else:
        dataset = trim_xr_data(dataset, start_year, end_year)

    return dataset, logs


def preprocess_input_data_based_on_config(datasets, config):
    """
    Preprocess the input datasets based on configuration settings.

    Parameters
    ----------
    datasets : dict
        A nested dictionary with sectors as keys, each containing a dictionary
        of variables with xarray.Dataset objects as values.
    config : object
        Configuration object with various flags and parameters controlling
        the preprocessing.

    Returns
    -------
    dict
        The updated dictionary of datasets after preprocessing.
    """
    # 1. Remove irrigation data if deficit irrigation mode is disabled
    if not config.deficit_irrigation_mode:
        datasets['irrigation'].pop('gwd_mask', None)
        datasets['irrigation'].pop('abstraction_irr_part_mask', None)

    # 2. Process irrigation input based on AEI settings
    if config.irrigation_input_based_on_aei:
        datasets['irrigation'].pop('fraction_aai_aei', None)
    else:
        # Extend 'fraction_aai_aei' data if irrigation input is based on AEI
        fraction_aai_aei = datasets['irrigation']['fraction_aai_aei']
        if fraction_aai_aei:
            fraction_aai_aei = extend_xr_data(
                fraction_aai_aei, config.start_year, config.end_year, 'monthly'
                )
            datasets['irrigation']['fraction_aai_aei'] = fraction_aai_aei

    # 3. Process time factor data for irrigation if enabled
    if not config.correct_irrigation_t_aai_mode:
        datasets['irrigation'].pop('time_factor_aai', None)
    else:
        # Extend the 'time_factor_aai'
        time_factor_aai = datasets['irrigation']['time_factor_aai']
        if time_factor_aai:
            time_factor_aai = extend_xr_data(
                time_factor_aai, config.start_year, config.end_year, 'monthly'
                )
            datasets['irrigation']['time_factor_aai'] = time_factor_aai

    return datasets

# =============================================================
# UTILITY FUNCTIONS
# =============================================================


def initialize_logs():
    """Initialize logs for tracking validation issues with xarray datasets."""
    return {
        "too_many_vars": [],  # decisive
        "unknown_vars": [],  # not decisive
        "unit_mismatch": [],  # decisive
        "missing_unit": [],  # decisive
        "lat_lon_consistency": True,  # decisive
        "lat_lon_reference": None,  # only needed for check_spatial_coords
        "missing_time_coverage": [],  # decisive, if time_extend_mode disabled
        "time_resolution_mismatch": [],  # decisive
        "missing_time_coords": [],  # decisive
        "extended_time_period": []  # only information
    }
