# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE domestic simulation module."""

import os
import xarray as xr
from model import model_equations as me
from misc import cell_specific_output as cso

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # =============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


class DomesticSimulator:
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Class to handle domestic water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Array of yearly consumptive use of total water in domestic sector
        converted to daily values. Originally read as xr.DataArray.
        (input)
    consumptive_use_gw : numpy.ndarray
        Array of consumptive use of groundwater in domestic sector.
        (calculated)
    consumptive_use_sw : numpy.ndarray
        Array of consumptive use of surface water in domestic sector.
        (calculated)
    abstraction_tot : numpy.ndarray
        Array of yearly abstraction of total water in domestic sector converted
        to daily values. Originally read as xr.DataArray.
        (input)
    abstraction_tot : numpy.ndarray
        Array of total water abstraction in domestic sector.
        (calculated)
    abstraction_gw : numpy.ndarray
        Array of groundwater abstraction in domestic sector.
        (calculated)
    abstraction_sw : numpy.ndarray
        Array of surface water abstraction in domestic sector.
        (calculated)
    return_flow_tot : numpy.ndarray
        Array of total return flow of water use in domestic sector.
        (calculated)
    return_flow_gw : numpy.ndarray
        Array of return flow to groundwater of water use in domestic sector.
        (calculated)
    return_flow_sw : numpy.ndarray
        Array of return flow to surface water of water use in domestic sector.
        (calculated)
    net_abstraction_gw : numpy.ndarray
        Array of net abstraction of groundwater in domestic sector.
        (calculated)
    net_abstraction_sw : numpy.ndarray
        Array of net abstraction of surface water in domestic sector.
        (calculated)
    fraction_gw_use : numpy.ndarray or int
        Array of fractions of consumptive use from groundwater in domestic
        sector or 0 if not provided. Originally as xr.DataArray.
        (input)
    fraction_return_gw : numpy.ndarray or int
        Array of fractions of return flow to groundwater in domestic sector or
        0 if not provided. Originally read as xr.DataArray.
        (input)
    coords : xarray.Coordinates
        Coordinates from the original dataset.
        (input)
    """

    def __init__(self, dom_data, config):
        """
        Initialize the DomesticSimulator with data and run the simulation.

        Parameters
        ----------
        dom_data : dict
            Dictionary containing xarray.DataArrays for various domestic
            variables.
        """
        # Initialize relevant configuration settings
        self.cso_flag = config.cell_specific_output['Flag']
        # Set unit
        self.unit = dom_data['unit']
        # Set total consumptive use input [m3/year]
        self.consumptive_use_tot = dom_data['consumptive_use_tot'].values

        # Set total abstraction input [m3/year]
        self.abstraction_tot = dom_data['abstraction_tot'].values

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (dom_data['fraction_gw_use'].values
             if 'fraction_gw_use' in dom_data and
             isinstance(dom_data['fraction_gw_use'], xr.DataArray)
             else 0)
        # Set fraction of groundwater return, default to 0 if not provided
        self.fraction_return_gw = \
            (dom_data['fraction_return_gw'].values
             if 'fraction_return_gw' in dom_data and
             isinstance(dom_data['fraction_return_gw'], xr.DataArray)
             else 0)
        # Store the coordinates for later use
        self.coords = dom_data['consumptive_use_tot'].coords

        if self.cso_flag:
            print("Domestic-specific values for "
                  f"lat: {config.cell_specific_output['coords']['lat']}, "
                  f"lon: {config.cell_specific_output['coords']['lon']},\n"
                  f"year: {config.cell_specific_output['coords']['year']}, "
                  f"month: {config.cell_specific_output['coords']['month']}")
            self.coords_idx = \
                cso.get_np_coords_cell_output(dom_data['consumptive_use_tot'],
                                             'domestic',
                                             config.cell_specific_output)

        # Run the domestic simulation
        self.simulate_domestic()

        # print("Domestic simulation was performed. \n")

    def simulate_domestic(self):
        """Run domestic simulation with provided data."""
        # Calc consumptive use from groundwater and surface water
        self.consumptive_use_gw, self.consumptive_use_sw = \
            me.calc_gwsw_water_use(self.consumptive_use_tot,
                                   self.fraction_gw_use)

        # Calc abstraction from groundwater and surface water
        self.abstraction_gw, self.abstraction_sw = \
            me.calc_gwsw_water_use(self.abstraction_tot,
                                   self.fraction_gw_use)

        # Calc and split return flows to groundwater and surface water
        self.return_flow_tot, self.return_flow_gw, self.return_flow_sw = \
            me.calc_return_flow_totgwsw(self.abstraction_tot,
                                        self.consumptive_use_tot,
                                        self.fraction_return_gw)

        # Calc net abstractions from groundwater and surface water
        self.net_abstraction_gw, self.net_abstraction_sw = \
            me.calc_net_abstraction_gwsw(self.abstraction_gw,
                                         self.return_flow_gw,
                                         self.abstraction_sw,
                                         self.return_flow_sw)

        cso.print_cell_value(self.consumptive_use_tot, 'consumptive_use_tot',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.abstraction_tot, 'abstraction_tot',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.fraction_gw_use, 'fraction_gw_use',
                  self.coords_idx, flag=self.cso_flag)
        cso.print_cell_value(self.consumptive_use_gw, 'consumptive_use_gw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.consumptive_use_sw, 'consumptive_use_sw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.abstraction_gw, 'abstraction_gw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.abstraction_sw, 'abstraction_sw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.return_flow_tot, 'return_flow_tot',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.fraction_return_gw, 'fraction_return_gw',
                  self.coords_idx, flag=self.cso_flag)
        cso.print_cell_value(self.return_flow_gw, 'return_flow_gw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.return_flow_sw, 'return_flow_sw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.net_abstraction_gw, 'net_abstraction_gw',
                  self.coords_idx, self.unit, self.cso_flag)
        cso.print_cell_value(self.net_abstraction_sw, 'net_abstraction_sw',
                  self.coords_idx, self.unit, self.cso_flag)
        print()


if __name__ == "__main__":
    from misc import cli_args
    from controller import config_module as cm
    from controller import input_data_manager as idm

    args = cli_args.parse_cli()
    FILENAME = "C:/Users/lniss/Desktop/ReGWSWUSE_LN/source//gwswuse_config.json"

    config_test = cm.ConfigHandler(FILENAME)

    preprocessed_gwswuse_data, _, _, _ = \
        idm.input_data_manager(config_test)
    dom = DomesticSimulator(preprocessed_gwswuse_data['domestic'], config_test)
