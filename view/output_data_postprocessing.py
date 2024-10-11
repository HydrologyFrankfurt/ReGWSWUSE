# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""
Functions for results postprocessing for output.
"""

import datetime as dt
import numpy as np
import pandas as pd
import xarray as xr
from termcolor import colored
from colorama import init

from model import time_unit_conversion as tc
from view import gwswuse_var_info as var_info
from misc import watergap_version


init()
# =============================================================================
# FUNCTIONS TO CREATE XR DATATSET FOR OUTPUT IN NETCDF FORMAT
# =============================================================================


# def write_to_xr_dataarray(result_np,
#                           coords,
#                           variable_name,
#                           sector,
#                           start_year):


def write_to_xr_dataarray(result_np, coords, var_name, sector):
    """
    Write the model results contained in a NumPy array to an xarray dataset.

    This function organizes the data with specified coordinates and adds
    metadata relevant to the variable and the sector involved.

    Parameters
    ----------
    result_np : np.ndarray
        The numpy array containing model results for the specified variable.
    coords : dict
        A dictionary of coordinates (latitude, longitude, and for some
        variables also time) used for the xarray dataset. This dictionary sets
        the spatial and temporal dimensions for the data.
    var_name : str
        The name of the variable to be stored in the xarray dataset.
    sector : str
        The sector associated with the variable, used for metadata.

    Returns
    -------
    xr.DataArray
        An xarray dataset with the model results and appropriate metadata.
    """
    special_vars = ['irrigation_efficiency_gw',
                    'irrigation_efficiency_sw',
                    'deficit_irrigation_location']

    if var_name in special_vars:
        # select only 'lat' & 'lon' as coordinates
        coords = {key: coords[key] for key in ['lat', 'lon']}
        result_xr = xr.Dataset(coords=coords)
    else:
        result_xr = xr.Dataset(coords=coords)
        result_xr = result_xr.chunk({'time': 1, 'lat': 360, 'lon': 720})

    variable_metadata = set_variable_metadata_xr(sector, var_name)
    xr_var_name = variable_metadata['standard_name']
    del variable_metadata['standard_name']

    result_xr[xr_var_name] = \
        xr.DataArray(result_np, coords=coords)
    result_xr[xr_var_name].attrs = variable_metadata

    result_xr.attrs = set_global_metadata()

    return result_xr

# =============================================================================
# Functions to get metadata for netcdf data:
    # variable metadata
    # dimensions metadata
    # global metadata
# =============================================================================


def set_variable_metadata_xr(sector, var):
    """
    Retrieve sector-specific metadata for a given variable.

    This function replaces placeholders in the metadata template for the
    specified variable with sector-specific values.

    Parameters
    ----------
    sector : str
        The sector for which to retrieve metadata (e.g., 'irrigation').
    var : str
        The variable for which to retrieve metadata (e.g.,
        'consumptive_use_tot').

    Returns
    -------
    dict
        A dictionary containing the sector-specific metadata for the given
        variable.

    """
    irrigation_specific_vars = ['irrigation_efficiency_gw',
                                'irrigation_efficiency_sw',
                                'deficit_irrigation_location',
                                'fraction_aai_aei',
                                'time_factor_aai']

    if sector == 'irrigation' and var in irrigation_specific_vars:
        return var_info.modelvars[var]
    else:
        return var_info.modelvars[var][sector]


def set_dimension_attributes(xr_array, sector, start_year):
    """
    Set the attributes of the dimensions of an xarray DataArray.

    Parameters
    ----------
    xr_array : xr.DataArray
        The xarray DataArray to set attributes for.
    start_year : str
        The start year value to replace in the attributes.

    Returns
    -------
    xr.DataArray
        The xarray DataArray with updated attributes.
    """
    if sector in ['irrigation', 'total']:
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
        if dim in xr_array.coords:
            # Update the coordinates with the new attributes
            xr_array.coords[dim].attrs.update(attrs)

    return xr_array


def set_global_metadata():
    """
    Set global metadata for output based on watergap_version.

    Returns
    -------
    dictionary
        The dictionary with updated global metadata.
    """
    global_metadata = {
        'title': (
            "WaterGAP"+" "+watergap_version.__version__ + ' model ouptput'
            ),
        'institution': watergap_version.__institution__,
        'contact': "contact@hydrology.uni-frankfurt.de",
        'model_version':  "WaterGAP"+" "+watergap_version.__version__,
        "reference": watergap_version.__reference__,
        'Creation_date':
            dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    return global_metadata


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
# =============================================================================
# Function to calculate and save global annual totals
# =============================================================================


def sum_global_annual_totals(sectors_dict, start_year, end_year):
    """
    Store global annual totals for variables in a dictionary of dataframes.

    Parameters
    ----------
    sectors_dict: dict
        Dictionary with simulation results for every sector singlewise and
        total.
    start_year : int
        The start year of the simulation period.
    end_year : int
        The end year of the simulation period.

    Returns
    -------
    global_annuals_dict: dict
         Dictionary of dataframes, where keys are variable names and values are
         dataframes with global annual totals.
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

    print('\n' + colored(f'Global Totals for year {start_year}', 'cyan'))
    # Iterate over each variable in the list
    for var_name in global_annual_totals_vars:
        # Create an empty dataframe to store annual totals for each sector
        var_df = pd.DataFrame(index=year_range)

        # Iterate over each sector in the sectors_dict
        for sector in sectors_dict.keys():
            # Get the array of values for the current variable and sector
            var_array = getattr(sectors_dict[sector], var_name)

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
        print('\n' + colored(f'{var_name}:', 'yellow'))
        for sector, var_value in var_df.iloc[0, :].items():
            print(f"{sector}: {var_value} km3/year")

        # Add the dataframe for the current variable to the global_annuals_dict
        global_annuals_dict[var_name] = var_df

    return global_annuals_dict
