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


def output_data_manager(gwswuse_results,
                        output_selection,
                        output_dir,
                        start_year,
                        end_year):
    """
    Manage the output data process.

    Parameters
    ----------
    gwswuse_results : dict
        The results from the groundwater and surface water use simulation.
    output_selection : dict
        The user-defined selection of outputs to be processed.
    output_dir : str
        The directory where the output files will be saved.
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.
    """
    # initialize output selection
    (output_sector_sel, output_vars_sel, wghm_input_flag,
     global_annual_total_flag) = \
        initialize_output_selection(output_selection)

    # Global annual totals creation
    if global_annual_total_flag:
        logger.debug("Starting calculation of global annual totals.")
        df_global_annual_totals = \
            odp.sum_global_annual_totals(gwswuse_results, start_year, end_year)
        # End log for function exit
        logger.debug("Calculation of global annual totals completed.")

        save_global_annual_totals_to_excel(output_dir, df_global_annual_totals)

    # Prepare and save selected variables as NetCDF files
    output_xr_data = get_selected_var_results_as_xr(gwswuse_results,
                                                    output_sector_sel,
                                                    output_vars_sel,
                                                    wghm_input_flag)
    save_datasets_to_netcdf(output_dir, output_xr_data)

    logger.info(f"Output data saved in:\n{output_dir}")

    return output_xr_data
# ===============================================================
# OUTPUT DATA MANAGER SUB FUNCTION
# ===============================================================


# initialize output selection from configuration file for output_data_manager
def initialize_output_selection(output_selection):
    """
    Initialize selection of output data from configuration.

    Parameters
    ----------
    output_selection : dict
        The user-defined selection of outputs to be processed.

    Returns
    -------
    output_sector_sel : list
        List of selected sectors.
    output_vars_sel : list
        List of selected variables.
    wghm_input_flag : bool
        Flag indicating whether dict with wghm input variables in xr.DataArray
        format should be kept in memory.
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

    logger.debug(f"Specific-selected output sectors: {output_sector_sel}")
    logger.debug(f"Specific-selected output variables: {output_vars_sel}")
    logger.debug(f"WGHM input flag: {wghm_input_flag}")
    logger.debug(f"Global annual total flag: {global_annual_total_flag}")

    return (output_sector_sel, output_vars_sel,
            wghm_input_flag, global_annual_total_flag)


def get_selected_var_results_as_xr(results_dict,
                                   output_sector_sel,
                                   output_vars_sel,
                                   wghm_input_flag,
                                   ):
    """
    Get selected variable results as xarray datasets.

    Parameters
    ----------
    results_dict : dict
        Dictionary containing the results in numpy from the simulation.
    output_sector_sel : list
        List of selected sectors.
    output_vars_sel : list
        List of selected variables.
    wghm_input_flag : bool
        Flag indicating whether dict with wghm input variables in xr.DataArray
        format should be kept in memory.

    Returns
    -------
    output_xr_data : dict
        Dictionary of xarray datasets for selected variables.
    """
    # first get xr data for netcdf output
    output_xr_data = {}
    for sector_name in output_sector_sel:
        sector_obj = results_dict[sector_name]
        for var_name in output_vars_sel:
            var_np_result = getattr(sector_obj, var_name, None)
            if var_np_result is not None:
                var_xr_result = \
                    odp.write_to_xr_dataarray(var_np_result,
                                              sector_obj.coords,
                                              var_name,
                                              sector_name)
                var_name = sector_name + '_' + var_name
                output_xr_data[var_name] = var_xr_result
                logger.debug(
                    f"xr.DataArray with metadata created successfully for: "
                    f"{sector_name}_{var_name}.")

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
                sector_obj = results_dict[sector_name]
                var_np_result = getattr(sector_obj, var_name, None)
                output_xr_data[output_var_name] = \
                    odp.write_to_xr_dataarray(var_np_result,
                                              sector_obj.coords,
                                              var_name,
                                              sector_name)
                logger.debug(
                    f"xr.DataArray with metadata created successfully for: "
                    f"{sector_name}_{var_name}.")

    return output_xr_data
# ===============================================================
# SAVING FUNCTIONS FOR OUTPUT DATA
# ===============================================================


def save_datasets_to_netcdf(output_dir, output_xr_data):
    """
    Save xr.Datasets from dictionary to NetCDF files.

    Parameters
    ----------
    output_dir: str
        The path to the directory where the NetCDF files
        will be saved.
    output_xr_data: dict
        A dictionary where the values are xarray.Dataset
        objects and the keys are used for naming the files.

    Returns
    -------
    list
        A list of paths to the created NetCDF files.
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
            logger.debug(f"Saved NetCDF file: {key}.nc")
    logger.info(f"Total NetCDF files created: {len(saved_files)}")
    logger.debug(f"NetCDF saving runtime: {time.time() - start_time} seconds")

    return saved_files


def save_global_annual_totals_to_excel(output_dir, var_dict):
    """
    Save global annual totals to .xlsx file with metadata in separate sheets.

    Parameters
    ----------
    var_dict: dict
        Dictionary of dataframes, where keys are variable names and values
        are dataframes to be saved.
    file_name: str
        The name of the Excel file to save.
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
        for variable_name, df in var_dict.items():
            df.to_excel(writer, sheet_name=variable_name)
    logger.debug(
        "Global annual totals are saved in global_annual_totals.xlsx.")
