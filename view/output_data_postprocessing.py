# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Functions for results postprocessing for output."""

import datetime as dt
import numpy as np
import pandas as pd
import xarray as xr
from termcolor import colored
from colorama import init

from gwswuse_logger import get_logger
from misc import watergap_version
from model import time_unit_conversion as tc
from view import gwswuse_var_info as var_info

init()
logger = get_logger(__name__)
# =============================================================================
# FUNCTIONS TO CREATE XR DATATSET FOR OUTPUT IN NETCDF FORMAT
# =============================================================================


def write_to_xr_dataarray(var_result_np, coords, var_name, sector_name):
    """
    Write the model results contained in a NumPy array to an xarray dataset.

    This function organizes the data into an xarray.Dataset with specified
    spatial and temporal coordinates and adds ISIMIP-conform metadata relevant
    to the variable and the associated sector.

    Parameters
    ----------
    var_result_np : np.ndarray
        The numpy array containing model results for the specified variable.
    coords : dict
        A dictionary specifying the coordinates for the dataset. Expected keys
        are 'lat' and 'lon', and optionally 'time', depending on the variable.
    var_name : str
        The name of the variable to be stored in the xarray dataset.
    sector_name : str
        The sector associated with the variable, used to assign metadata.

    Returns
    -------
    var_result_xr = xr.DataArray
        An xarray dataset with the model results and appropriate metadata.
    """
    special_vars = ['irrigation_efficiency_gw',
                    'irrigation_efficiency_sw',
                    'deficit_irrigation_location']
    try:
        if var_name in special_vars:
            # select only 'lat' & 'lon' as coordinates
            coords = {key: coords[key] for key in ['lat', 'lon']}
            var_result_xr = xr.Dataset(coords=coords)
        else:
            var_result_xr = xr.Dataset(coords=coords)
            var_result_xr = \
                var_result_xr.chunk({'time': 1, 'lat': 360, 'lon': 720})

        variable_metadata = set_variable_metadata_xr(sector_name, var_name)
        xr_var_name = variable_metadata['isimip_name']
        del variable_metadata['isimip_name']

        var_result_xr[xr_var_name] = \
            xr.DataArray(var_result_np, coords=coords)
        var_result_xr[xr_var_name].attrs = variable_metadata

        var_result_xr.attrs = set_global_metadata()

    except ValueError as e:  # Replace Exception with specific error type
        logger.error(
            "Failed to create xarray.DataArray for %s/%s: %s",
            sector_name, var_name, e
        )
    except KeyError as e:  # Add another specific exception, if applicable
        logger.error(
            "Missing key in coordinates or metadata for %s/%s: %s",
            sector_name, var_name, e
        )

    return var_result_xr

# =============================================================================
# Functions to get metadata for netcdf data:
    # variable metadata
    # dimensions metadata
    # global metadata
# =============================================================================


def set_variable_metadata_xr(sector_name, var_name):
    """
    Retrieve sector-specific metadata for a given variable.

    This function replaces placeholders in the metadata template for the
    specified variable with sector-specific values.

    Parameters
    ----------
    sector_name : str
        The sector name for which to retrieve metadata (e.g., 'irrigation').
    var_name : str
        The variable for which to retrieve metadata (e.g.,
        'consumptive_use_tot').

    Returns
    -------
    variable_metadata : dict
        A dictionary containing the sector-specific metadata for the given
        variable.

    """
    irrigation_specific_vars = ['irrigation_efficiency_gw',
                                'irrigation_efficiency_sw',
                                'deficit_irrigation_location',
                                'fraction_aai_aei',
                                'time_factor_aai']

    try:
        if sector_name == 'irrigation' and var_name in irrigation_specific_vars:
            return var_info.modelvars[var_name]
        variable_metadata = var_info.modelvars[var_name][sector_name]
        return variable_metadata

    except KeyError as e:
        logger.error(
            "Metadata for %s/%s not found: %s", sector_name, var_name, e)
        raise


def set_dimension_attributes(data, sector_name, start_year):
    """
    Set the attributes of the dimensions of an xarray DataArray.

    Parameters
    ----------
    data : xr.DataArray
        The xarray DataArray to set attributes for.
    start_year : str
        The start year value to replace in the attributes.

    Returns
    -------
    data : xr.DataArray
        The xarray DataArray with updated attributes.
    """
    if sector_name in ['irrigation', 'total']:
        timestep = 'Months'
    else:
        timestep = 'Years'
    # Create attribute dictionairy for dimensions
    dim_attributes = {
        'time': {
            'standard_name': 'time',
            'long_name': 'time axis',
            'units': '{timestep} since {start_year}-1-1 00:00:00',
            'calendar': '365_day',
            'axis': 'T'
        },
        'lat': {
            'standard_name': 'latitude',
            'long_name': 'latitude',
            'units': 'degrees_north',
            'axis': 'X'
        },
        'lon': {
            'standard_name': 'longitude',
            'long_name': 'longitude',
            'units': 'degrees_east',
            'axis': 'Y'
            }
        }
    # Replace placeholders in the attributes
    for attrs in dim_attributes.values():
        for attr, value in attrs.items():
            if isinstance(value, str):
                attrs[attr] = \
                    value.format(
                        timestep=timestep,
                        start_year=start_year
                        )

    # Set attributes for the dimensions if they exist in the xarray DataArray
    for dim, attrs in dim_attributes.items():
        if dim in data.coords:
            # Update the coordinates with the new attributes
            data.coords[dim].attrs.update(attrs)

    return data


def set_global_metadata():
    """
    Set global metadata for output based on watergap_version.

    Returns
    -------
    global_metadata : dictionary
        The dictionary with updated global metadata.
    """
    try:
        global_metadata = {
            'title': (
                "WaterGAP " + watergap_version.__version__ + " model output"
            ),
            'institution': watergap_version.__institution__,
            'contact': "contact@hydrology.uni-frankfurt.de",
            'model_version':  "WaterGAP " + watergap_version.__version__,
            'reference': watergap_version.__reference__,
            'Creation_date': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except AttributeError:
        logger.error("Error setting global metadata:\n"
                     "missing attribute in watergap_version.")
        raise
    return global_metadata

# =============================================================================
# Function to calculate and save global annual totals
# =============================================================================


def sum_global_annual_totals(gwswuse_results, start_year, end_year):
    """
    Store global annual totals for variables in a dictionary of dataframes.

    Parameters
    ----------
    gwswuse_results : dict
        Dictionary containing results from the GWSWUSE simulation, organized by
        sector names as keys. Each sector contains attributes for variables.
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.

    Returns
    -------
    global_annuals_dict: dict
         Dictionary of dataframes, where keys are variable names and values are
         pandas.DataFrame objects containing global annual totals to be saved.
    """
    # Define the range of years for the simulation period
    year_range = range(start_year, end_year + 1)

    # Initialize an empty dictionary to store global annual totals
    global_annuals_dict = {}

    # List of variables for which to calculate global annual totals
    global_annual_totals_vars = [
        'consumptive_use_tot', 'consumptive_use_gw', 'consumptive_use_sw',
        'abstraction_tot', 'abstraction_gw', 'abstraction_sw',
        'return_flow_tot', 'return_flow_gw', 'return_flow_sw',
        'net_abstraction_gw', 'net_abstraction_sw'
    ]
    # List sectors with monthly time resolution
    monthly_sectors = ['irrigation', 'total']

    # Initialize a string to store the log output
    log_output = colored(f"\nGlobal Totals for year {start_year}\n", 'cyan')

    # Iterate over each variable in the list
    for var_name in global_annual_totals_vars:
        # Create an empty dataframe to store annual totals for each sector
        var_df = pd.DataFrame(index=year_range)
        logger.debug("Calculate global annual totals for %s.", var_name)
        # Iterate over each sector in the gwswuse_results
        for sector in gwswuse_results.keys():
            # Get the array of values for the current variable and sector
            var_array = getattr(gwswuse_results[sector], var_name)

            if sector in monthly_sectors:
                # Convert daily values to yearly values
                var_array = \
                    tc.convert_monthly_to_yearly(var_array)

            # Sum the values across the lat and lon dimensions for annual
            # totals
            annual_totals = np.nansum(var_array, axis=(1, 2))

            # Convert the annual totals from m³/year to km³/year
            annual_totals = annual_totals / 10**9

            # Add the annual totals for the current sector to the dataframe
            var_df[sector] = annual_totals

        # Add the current variable's results to the log output string
        log_output += colored(f"\n{var_name}:\n", 'yellow')
        for sector, var_value in var_df.iloc[0, :].items():
            log_output += f"{sector}: {var_value} km3/year\n"

        # Add the dataframe for the current variable to the global_annuals_dict
        global_annuals_dict[var_name] = var_df

    # Log the entire output at once
    logger.info(log_output)

    return global_annuals_dict


# Functions to get metadata for global annual totals
def create_metadata_global_annual_totals():
    """
    Create general and variable metadata for the global annual totals report.

    Returns
    -------
    tuple
        A tuple containing two dataframes: (metadata_df, variable_metadata_df).
    """
    global_metadata = set_global_metadata()

    # Add report title at the top
    general_metadata = {
        'report title': 'GWSWUSE Global Annual Totals Report',
        **global_metadata  # Merge with global_metadata
    }

    general_metadata_df = \
        pd.DataFrame(general_metadata.items(), columns=['Key', 'Value'])

    unit = 'km3/year'
    variable_metadata = {
        "consumptive_use_tot": {
            "long": "Consumptive total water use",
            "unit": unit
            },
        "consumptive_use_gw": {
            "long": "Consumptive total groundwater use",
            "unit": unit
            },
        "consumptive_use_sw": {
            "long": "Consumptive total surface water use",
            "unit": unit
            },
        "abstraction_tot": {
            "long": "Total water abstraction",
            "unit": unit
            },
        "abstraction_gw": {
            "long": "Water abstraction from groundwater",
            "unit": unit
            },
        "abstraction_sw": {
            "long": "Water abstraction from surface water",
            "unit": unit
            },
        "return_flow_tot": {
            "long": "Total return flows",
            "unit": unit
            },
        "return_flow_gw": {
            "long": "Return flow to groundwater",
            "unit": unit
            },
        "return_flow_sw": {
            "long": "Return flow to surface water",
            "unit": unit
            },
        "net_abstraction_gw": {
            "long": "Net abstractions from groundwater",
            "unit": unit
            },
        "net_abstraction_sw": {
            "long": "Net abstractions from surface water",
            "unit": unit
            }
        }

    variable_metadata_list = []
    for var_name, var_meta in variable_metadata.items():
        var_meta['Variable Name'] = var_name
        variable_metadata_list.append(var_meta)

    variable_metadata_df = pd.DataFrame(variable_metadata_list)

    return general_metadata_df, variable_metadata_df
