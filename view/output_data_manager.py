# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
""" Output data manager """

import os
import time
import xarray as xr
import pandas as pd
from view import output_data_postprocessing as odp


# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # =============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]

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
    output_sector_sel = \
        [sector_name
         for sector_name, is_enabled in output_selection['Sectors'].items()
         if is_enabled]

    output_vars_sel = [
        f"{var_category}_{var_type}"
        if isinstance(settings, dict) else f"{var_category}"
        for var_category, settings in
        output_selection['GWSWUSE variables'].items()
        for var_type, is_enabled in (settings.items()
        if isinstance(settings, dict) else [(None, settings)])
        if is_enabled]

    wghm_input_flag = output_selection['WGHM_input_run']

    global_annual_total_flag = output_selection['Global_Annual_Totals']

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
    end_time = time.time()
    print(f"NETCDF SAVE runtime: {end_time - start_time} seconds.")
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

    # print(f"\n Excel file '{filename}' has been created with multiple sheets.")

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
    output_sector_sel, output_vars_sel, wghm_input_flag, global_annual_total_flag = \
        initialize_output_selection(output_selection)

    # create global annual totals
    if global_annual_total_flag:
        df_global_annual_totals = \
            odp.sum_global_annual_totals(gwswuse_results, start_year, end_year)

        save_global_annual_totals_to_excel(output_dir, df_global_annual_totals)

    output_xr_data = get_selected_var_results_as_xr(gwswuse_results,
                                                    output_sector_sel,
                                                    output_vars_sel,
                                                    wghm_input_flag)

    save_datasets_to_netcdf(output_dir, output_xr_data)
    print(f"\nOutput data saved to output folder {output_dir}")
    return output_xr_data
