# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Output data manager."""

import os
import time
import xarray as xr
import pandas as pd
from gwswuse_logger import get_logger
from view import output_data_postprocessing as odp


# ===============================================================
# Module name is passed to logger
# # =============================================================
logger = get_logger(__name__)

# ===============================================================
# OUTPUT DATA MANAGER MAIN FUNCTION
# ===============================================================


def output_data_manager(
        gwswuse_results, output_selection, output_dir, start_year, end_year):
    """
    Manage the output data processing and saving.

    This function processes and saves the output data based on user-defined
    selections. It calculates global annual totals if required, extracts the
    selected variables, and saves them as NetCDF files.

    Parameters
    ----------
    gwswuse_results : dict
        Dictionary containing results from the GWSWUSE simulation, organized by
        sector names as keys. Each sector contains attributes for variables and
        coordinates.
    output_selection : dict
        Dictionary specifying the user's selection of sectors and variables to
        include in the output.
    output_dir : str
        Path to the directory where the output files will be saved.
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.

    Returns
    -------
    output_xr_data : dict
        Dictionary containing the processed xarray.Dataset objects for the
        selected output variables.
    """
    # Initialize output selection
    (output_sector_sel, output_vars_sel, wghm_input_flag,
     global_annual_total_flag) = \
        initialize_output_selection(output_selection)

    # Global annual totals creation
    if global_annual_total_flag:
        logger.debug("Starting calculation of global annual totals.")
        global_annuals_dict = \
            odp.sum_global_annual_totals(gwswuse_results, start_year, end_year)
        # End log for function exit
        logger.debug("Calculation of global annual totals completed.")
        # Save global annual totals in xlsx file with multiple sheets
        save_global_annual_totals_to_excel(output_dir, global_annuals_dict)

    # Prepare and save selected variables as xarray dataarrays
    output_xr_data = get_selected_var_results_as_xr(gwswuse_results,
                                                    output_sector_sel,
                                                    output_vars_sel,
                                                    wghm_input_flag)
    # Save xr data as netcdf files in output_dir
    save_datasets_to_netcdf(output_dir, output_xr_data)

    logger.info("Output data saved in:\n%s", output_dir)

    return output_xr_data
# ===============================================================
# OUTPUT DATA MANAGER SUB FUNCTION
# ===============================================================


# initialize output selection from configuration file for output_data_manager
def initialize_output_selection(output_selection):
    """
    Initialize selection of output data from configuration.

    This function parses the user's output selection configuration to identify
    selected sectors, variables, and additional processing options.

    Parameters
    ----------
    output_selection : dict
        Dictionary specifying the user's selection of sectors and variables
        to include in the output.

    Returns
    -------
    output_sector_sel : list
        List of sector names selected for output.
    output_vars_sel : list
        List of variables selected for output, including variable categories
        and types (formatted as "category_type").
    wghm_input_flag : bool
        Flag indicating whether variables that serve as input for the
        WaterGAP Global Hydrology Model (WGHM) should be saved as NetCDF
        files.
    global_annual_total_flag : bool
        Flag indicating whether to calculate and save global annual totals.

    """
    logger.debug("Initialize output selection.")
    output_sector_sel = \
        [sector_name
         for sector_name, is_enabled in output_selection['Sectors'].items()
         if is_enabled]

    output_vars_sel = []
    for var_category, settings in output_selection['GWSWUSE variables'
                                                   ].items():
        if isinstance(settings, dict):  # When settings is a dictionary
            for var_type, is_enabled in settings.items():
                if is_enabled:  # Only include enabled settings
                    output_vars_sel.append(f"{var_category}_{var_type}")
        else:  # When settings is not a dictionary (e.g., boolean)
            if settings:  # Only include if enabled
                output_vars_sel.append(f"{var_category}")

    wghm_input_flag = output_selection['WGHM_input_run']

    global_annual_total_flag = output_selection['Global_Annual_Totals']

    logger.debug("Specific-selected output sectors: %s", output_sector_sel)
    logger.debug("Specific-selected output variables: %s", output_vars_sel)
    logger.debug("WGHM input flag: %s", wghm_input_flag)
    logger.debug("Global annual total flag: %s", global_annual_total_flag)

    return (output_sector_sel, output_vars_sel,
            wghm_input_flag, global_annual_total_flag)


def get_selected_var_results_as_xr(gwswuse_results,
                                   output_sector_sel,
                                   output_vars_sel,
                                   wghm_input_flag,
                                   ):
    """
    Get selected variable results as xarray datasets.

    Parameters
    ----------
    gwswuse_results : dict
        Dictionary containing results from the GWSWUSE simulation, organized by
        sector names as keys. Each sector contains attributes for variables and
        coordinates.
    output_sector_sel : list
        List of sector names selected for output.
    output_vars_sel : list
        List of variables selected for output, including variable categories
        and types (formatted as "category_type").
    wghm_input_flag : bool
        Flag indicating whether variables that serve as input for the
        WaterGAP Global Hydrology Model (WGHM) should be saved as NetCDF
        files.

    Returns
    -------
    output_xr_data : dict
        Dictionary of xarray.DataArray objects for the selected variables and
        WGHM input variables, organized by variable names as keys.
    """
    # first get xr data for netcdf output
    output_xr_data = {}
    for sector_name in output_sector_sel:
        sector_obj = gwswuse_results[sector_name]
        for var_name in output_vars_sel:
            var_result_np = getattr(sector_obj, var_name, None)
            if var_result_np is not None:
                var_xr_result = \
                    odp.write_to_xr_dataarray(var_result_np,
                                              sector_obj.coords,
                                              var_name,
                                              sector_name)
                var_name = sector_name + '_' + var_name
                output_xr_data[var_name] = var_xr_result
                logger.debug(
                    "xr.DataArray with metadata created successfully for: "
                    "%s_%s", sector_name, var_name)

    # second get xr data for wghm input
    if wghm_input_flag:
        wghm_input_variables = [('irrigation', 'consumptive_use_sw'),
                                ('irrigation', 'abstraction_sw'),
                                ('total', 'net_abstraction_gw'),
                                ('total', 'net_abstraction_sw')]

        for wghm_var in wghm_input_variables:
            sector_name = wghm_var[0]
            var_name = wghm_var[1]
            output_var_name = sector_name + '_' + var_name
            # check if wghm input variables are not selected for output
            # then write wghm input variables here to xr_data
            if output_var_name not in output_xr_data:
                sector_obj = gwswuse_results[sector_name]
                var_result_np = getattr(sector_obj, var_name, None)
                output_xr_data[output_var_name] = \
                    odp.write_to_xr_dataarray(var_result_np,
                                              sector_obj.coords,
                                              var_name,
                                              sector_name)
                logger.debug(
                    "xr.DataArray with metadata created successfully for: "
                    "%s_%s", sector_name, var_name)

    return output_xr_data
# ===============================================================
# SAVING FUNCTIONS FOR OUTPUT DATA
# ===============================================================


def save_datasets_to_netcdf(output_dir, output_xr_data):
    """
    Save xr.Datasets from a dictionary to NetCDF files.

    Parameters
    ----------
    output_dir : str
        The path to the directory where the NetCDF files will be saved.
    output_xr_data : dict
        A dictionary where the values are xarray.Dataset objects and the keys
        are used for naming the files.
    """
    # Create the directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    start_time = time.time()
    saved_files = []  # List to store the file paths
    for key, dataset in output_xr_data.items():
        if isinstance(dataset, xr.Dataset):
            file_path = os.path.join(output_dir, f"{key}.nc")
            encoding = \
                {var: {'zlib': True, 'complevel': 5}
                 for var in dataset.data_vars}
            dataset.to_netcdf(file_path, format='NETCDF4', encoding=encoding)
            saved_files.append(file_path)
            logger.debug("Saved NetCDF file: %s.nc", key)
    logger.info("Total NetCDF files created: %s", len(output_xr_data))
    logger.debug("NetCDF saving runtime: %s seconds", time.time() - start_time)


def save_global_annual_totals_to_excel(output_dir, global_annuals_dict):
    """
    Save global annual totals to .xlsx file with metadata in separate sheets.

    Parameters
    ----------
    output_dir : str
        The directory where the Excel file will be saved.
    global_annuals_dict: dict
         Dictionary of dataframes, where keys are variable names and values are
         pandas.DataFrame objects containing global annual totals to be saved.
    """
    # Create metadata and variable metadata dataframes
    general_metadata_df, variable_metadata_df = \
        odp.create_metadata_global_annual_totals()
    filename = os.path.join(output_dir, 'global_annual_totals.xlsx')
    # Write to Excel file
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Save metadata
        general_metadata_df.to_excel(writer,
                                     sheet_name='General Metadata',
                                     header=False,
                                     index=False)

        # Save variable metadata
        variable_metadata_df.to_excel(writer,
                                      sheet_name='Variable Metadata',
                                      index=False)

        # Save each dataframe in separate sheets
        for variable_name, df in global_annuals_dict.items():
            df.to_excel(writer, sheet_name=variable_name)
    logger.debug(
        "Global annual totals are saved in global_annual_totals.xlsx.")
