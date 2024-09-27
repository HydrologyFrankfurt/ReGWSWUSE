# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""
Input data manager
"""

import os
import glob
import json
import time
import xarray as xr

from controller.input_data_check_preprocessing_proto import \
    check_and_preprocess_input_data

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = (os.path.basename(__file__))
modname = modname.split('.')[0]


# =============================================================
# LOAD CONVENTION DICT AND INPUT DATA
# =============================================================


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
    with open(convention_path, 'r') as convention_file:
        conventions = json.load(convention_file)
    return conventions


def load_netcdf_files(input_data_folder, sector_requirements):
    """
    Load NetCDF files from a specified folder.

    Parameters
    ----------
    input_data_folder : str
        Path to the folder containing NetCDF files organized by sector
        and variable.

    Returns
    -------
    list of tuple
        List of tuples, each containing an xarray.Dataset, sector, and
        variable.
    """
    datasets = []
    for sector in os.listdir(input_data_folder):
        if sector not in list(sector_requirements.keys()):
            continue
        sector_path = os.path.join(input_data_folder, sector)
        expected_vars = sector_requirements[sector]['expected_vars']
        if os.path.isdir(sector_path):
            for variable in os.listdir(sector_path):
                if variable not in expected_vars:
                    continue
                variable_path = os.path.join(sector_path, variable)
                if os.path.isdir(variable_path):
                    netcdf_files = \
                        glob.glob(os.path.join(variable_path, '*.nc'))
                    if netcdf_files:
                        datasets.append(
                            (xr.open_mfdataset(
                                netcdf_files, combine='by_coords'),
                                sector,
                                variable))
    return datasets

# =============================================================
# INPUT DATA MANAGER MAIN FUNCTION
# =============================================================


def input_data_manager(input_data_folder,
                       convention_path,
                       start_year,
                       end_year,
                       time_extend_mode,
                       correct_irr_with_t_aai_mode):
    """
    Manage input data by loading, checking, and preprocessing it according to
    specified conventions.

    Parameters
    ----------
    input_data_folder : str
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
    4. Returns the preprocessed data, check results, loaded datasets and
       conventions.
    """
    start_time = time.time()
    # load conventions
    conventions = load_conventions(convention_path)
    sector_requirements = conventions['sector_requirements']

    # load input data
    datasets = load_netcdf_files(input_data_folder, sector_requirements)

    # # check and preprocess input_data
    preprocessed_data, check_results = \
        check_and_preprocess_input_data(datasets,
                                        conventions,
                                        start_year,
                                        end_year,
                                        time_extend_mode,
                                        correct_irr_with_t_aai_mode)

    # # handle check results --> log --> sys.exit?
    # check_results_handling()
    end_time = time.time()
    print(f"Input data manager runtime: {end_time - start_time} seconds.")
    return preprocessed_data, check_results, datasets, conventions


if __name__ == "__main__":
    from controller import configuration_module as cm
    INPUT_DATA_FOLDER = 'C:/Users/lniss/Desktop/ReGWSWUSE_LN/input_data/'
    CONVENTION_PATH = \
        'C:/Users/lniss/Desktop/GPT_GWSWUSE/source/gwswuse_convention.json'
    (preprocessed_gwswuse_data,
     gwswuse_check_results,
     input_datasets,
     gwswuse_conventions
     ) = \
        input_data_manager(INPUT_DATA_FOLDER,
                           CONVENTION_PATH,
                           cm.start_year,
                           cm.end_year,
                           cm.time_extend_mode,
                           cm.correct_irr_with_t_aai_mode
                           )
