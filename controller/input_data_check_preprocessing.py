# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE input data check & preprocessing module for input_data_manager."""

from gwswuse_logger import get_logger
from controller.check_functions import (
    check_dataset_structure_metadata, check_spatial_coords, check_time_coords)

from controller.preprocessing_functions import (
    extend_xr_data, trim_xr_data, ensure_correct_dimension_order,
    sort_lat_desc_lon_asc_coords
    )

# =============================================================================
# Module name is passed to logger
# =============================================================================
logger = get_logger(__name__)

# =============================================================
# CHECK AND PREPROCESSING MAIN ALGORITHMS
# =============================================================


def check_and_preprocess_input_data(
        datasets_dict, conventions, config
        ):
    """
    Validate and preprocess input datasets based on input conventions.

    Parameters
    ----------
    datasets_dict : dict of dict of xarray.Dataset
        A nested dictionary with sectors as keys, and each sector containing
        a dictionary of variables with loaded xarray.Dataset objects as values.
    conventions : dict
        Dictionary containing conventions and sector requirements, including
        reference names, time-variant variables, and sector-specific details,
        some of which serve as references for the validation process.
    config : ConfigHandler
        Configuration object containing settings such as start_year, end_year,
        time_extend_mode and more for data processing.

    Returns
    -------
    preprocessed_datasets : dict
        Dictionary of preprocessed datasets, organized by sector and variable.
    check_logs : dict
        Dictionary containing the results of the validation process for the
        input data.
    """
    # Initialize conventions
    reference_names = conventions['reference_names']
    time_variant_vars = conventions['time_variant_vars']
    sector_requirements = conventions['sector_requirements']

    # Initialize logs for storing information about incorrect datasets
    check_logs = initialize_check_logs()

    datasets_dict = preprocess_input_data_based_on_config(
        datasets_dict, config)
    # Initialize the dictionary for preprocessed datasets
    preprocessed_datasets = {}

    # Validate and process each dataset in the nested dictionary structure
    for sector, variables in datasets_dict.items():
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
            logger.debug(log_id)
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
        dataset, check_logs, log_id, time_freq, config):
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
    time_freq : str
        The expected time frequency, either 'monthly' for monthly data or
        'yearly' for yearly data.
    log_id : str
        A unique identifier for logging the dataset's validation results.
    check_logs : dict
        A dictionary used for tracking validation results and preprocessing
        steps.
    config : ConfigHandler
        Configuration object containing settings, including `start_year` for
        the start of the required time period, `end_year` for the end year,
        and `time_extend_mode` to enable dataset extension if it does not
        cover the full period.

    Returns
    -------
    dataset : xarray.Dataset
        The preprocessed dataset, either extended or trimmed.
    check_logs : dict
        The updated check_logs reflecting the validation and preprocessing
        results.
    """
    start_year = config.start_year
    end_year = config.end_year
    time_extend_mode = config.time_extend_mode
    # Step 1: (Validation) Validate time coverage and resolution and log
    check_logs = check_time_coords(
        dataset, time_freq, start_year, end_year, log_id, check_logs)
    # Step 2a: Handle dataset depending on whether it covers the period
    if log_id in check_logs["missing_time_coverage"] and time_extend_mode:
        # 2a: (Preprocessing) Extend dataset if time_extend_mode is enabled
        dataset = extend_xr_data(dataset, start_year, end_year, time_freq)
        check_logs["extended_time_period"].append(log_id)
    # Step 2b: (Preprocessing) Trim dataset if it covers the required period
    else:
        dataset = trim_xr_data(dataset, start_year, end_year)

    return dataset, check_logs


def preprocess_input_data_based_on_config(datasets_dict, config):
    """
    Preprocess the input datasets_dict based on configuration settings.

    This function modifies the input datasets according to configuration
    options related to irrigation and time extensions, controlling which
    variables are retained or extended.

    Parameters
    ----------
    datasets_dict : dict
        A nested dictionary with sectors as keys, each containing a dictionary
        of variables with xarray.Dataset objects as values.
    config : object
        Configuration object with flags and parameters for preprocessing,
        including settings like `start_year`,`end_year`,
        `deficit_irrigation_mode`, `irrigation_input_based_on_aei` and
        `correct_irrigation_t_aai_mode`.

    Returns
    -------
    datasets_dict : dict
        The updated dictionary of datasets after preprocessing.
    """
    # 1. Remove irrigation data if deficit irrigation mode is disabled
    if not config.deficit_irrigation_mode:
        datasets_dict['irrigation'].pop('gwd_mask', None)
        datasets_dict['irrigation'].pop('abstraction_irr_part_mask', None)

    # 2. Process irrigation input based on AEI settings
    if not config.irrigation_input_based_on_aei:
        datasets_dict['irrigation'].pop('fraction_aai_aei', None)
    else:
        # Extend 'fraction_aai_aei' data if irrigation input is based on AEI
        fraction_aai_aei = datasets_dict['irrigation']['fraction_aai_aei']
        if fraction_aai_aei:
            fraction_aai_aei = extend_xr_data(
                fraction_aai_aei, config.start_year, config.end_year, 'monthly'
                )
            datasets_dict['irrigation']['fraction_aai_aei'] = fraction_aai_aei

    # 3. Process time factor data for irrigation if enabled
    if not config.correct_irrigation_t_aai_mode:
        datasets_dict['irrigation'].pop('time_factor_aai', None)
    else:
        # Extend the 'time_factor_aai'
        time_factor_aai = datasets_dict['irrigation']['time_factor_aai']
        if time_factor_aai:
            time_factor_aai = extend_xr_data(
                time_factor_aai, config.start_year, config.end_year, 'monthly'
                )
            datasets_dict['irrigation']['time_factor_aai'] = time_factor_aai

    return datasets_dict

# =============================================================
# UTILITY FUNCTIONS
# =============================================================


def initialize_check_logs():
    """
    Initialize logs for tracking validation issues with xarray datasets.

    Returns
    -------
    dict
        A dictionary initialized with keys for various validation checks,
        categorized by issue type. Keys include:

        - "too_many_vars" (list): Logs cases where multiple variables are
          present, though only one was expected (decisive).
        - "unknown_vars" (list): Logs variables that are not recognized
          according to conventions (not decisive).
        - "unit_mismatch" (list): Logs cases where variable units do not
          match expected units (decisive).
        - "missing_unit" (list): Logs variables missing unit definitions
          (not decisive).
        - "lat_lon_consistency" (bool): Tracks whether spatial coordinates
          are consistent across datasets (decisive).
        - "lat_lon_reference" (None): Reference coordinates for spatial
          consistency check, used only within `check_spatial_coords`.
        - "missing_time_coverage" (list): Logs datasets with incomplete time
          coverage; decisive if `time_extend_mode` is disabled.
        - "time_resolution_mismatch" (list): Logs datasets with time
          resolution mismatches (decisive).
        - "missing_time_coords" (list): Logs datasets missing required time
          coordinates (decisive).
        - "extended_time_period" (list): Logs datasets with extended time
          coverage; used for informational purposes only.
    """
    return {
        "too_many_vars": [],  # decisive
        "unknown_vars": [],  # not decisive
        "unit_mismatch": [],  # decisive
        "missing_unit": [],  # not decisive
        "lat_lon_consistency": True,  # decisive
        "lat_lon_reference": None,  # only needed for check_spatial_coords
        "missing_time_coverage": [],  # decisive, if time_extend_mode disabled
        "time_resolution_mismatch": [],  # decisive
        "missing_time_coords": [],  # decisive
        "extended_time_period": []  # only information
    }
