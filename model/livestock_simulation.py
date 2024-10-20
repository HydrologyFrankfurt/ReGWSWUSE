# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE livestock simulation module."""

import os
import xarray as xr
from model import model_equations as me
from model import time_unit_conversion as tc

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # =============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


class LivestockSimulator:
    """
    Class to handle livestock water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Array of yearly consumptive use of total water in livestock sector
        converted to daily values. Originally read as xr.DataArray.
        (input)
    consumptive_use_gw : numpy.ndarray
        Array of consumptive use of groundwater in livestock sector.
        (calculated)
    consumptive_use_sw : numpy.ndarray
        Array of consumptive use of surface water in livestock sector.
        (calculated)
    abstraction_tot : numpy.ndarray
        Array of yearly abstraction of total water in livestock sector
        converted to daily values. Defaults to consumptive_use_tot if not
        provided. Originally read as xr.DataArray.
        (input)
    abstraction_tot : numpy.ndarray
        Array of total water abstraction in livestock sector.
        (calculated)
    abstraction_gw : numpy.ndarray
        Array of groundwater abstraction in livestock sector.
        (calculated)
    abstraction_sw : numpy.ndarray
        Array of surface water abstraction in livestock sector.
        (calculated)
    return_flow_tot : numpy.ndarray
        Array of total return flow of water use in livestock sector.
        (calculated)
    return_flow_gw : numpy.ndarray
        Array of return flow to groundwater of water use in livestock sector.
        (calculated)
    return_flow_sw : numpy.ndarray
        Array of return flow to surface water of water use in livestock sector.
        (calculated)
    net_abstraction_gw : numpy.ndarray
        Array of net abstraction of groundwater in livestock sector.
        (calculated)
    net_abstraction_sw : numpy.ndarray
        Array of net abstraction of surface water in livestock sector.
        (calculated)
    fraction_gw_use : numpy.ndarray or int
        Array of fractions of consumptive use from groundwater in livestock
        sector or 0 if not provided. Originally read as xr.DataArray.
        (input)
    fraction_return_gw : numpy.ndarray or int
        Array of fractions of return flow to groundwater in livestock sector or
        0 if not provided. Originally read as xr.DataArray.
        (input)
    coords : xarray.Coordinates
        Coordinates from the original dataset.
        (input)
    """

    def __init__(self, liv_data, config):
        """
        Initialize the LivestockSimulator with data and run the simulation.

        Parameters
        ----------
        liv_data : dict
            Dictionary containing xarray.DataArrays for various livestock
            variables.
        """
        # Initialize relevant configuration settings
        self.cso_flag = config.cell_specific_output['flag']

        # Set total consumptive use input [m3/year]
        self.consumptive_use_tot = liv_data['consumptive_use_tot'].values

        # Set total abstraction input [m3/year]
        self.abstraction_tot = \
            (liv_data['abstraction_tot'].values
             if 'abstraction_tot' in liv_data and
             isinstance(liv_data['abstraction_tot'], xr.DataArray)
             else self.consumptive_use_tot)

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (liv_data['fraction_gw_use'].values
             if 'fraction_gw_use' in liv_data and
             isinstance(liv_data['fraction_gw_use'], xr.DataArray)
             else 0)
        # Set fraction of groundwater return, default to 0 if not provided
        self.fraction_return_gw = \
            (liv_data['fraction_return_gw'].values
             if 'fraction_return_gw' in liv_data and
             isinstance(liv_data['fraction_return_gw'], xr.DataArray)
             else 0)
        # Store the coordinates for later use
        self.coords = liv_data['consumptive_use_tot'].coords

        if self.cso_flag:
            print("Livestock specific values for "
                  f"lat: {config.cell_specific_output['coords']['lat']}, "
                  f"lon: {config.cell_specific_output['coords']['lon']},"
                  f"year: {config.cell_specific_output['coords']['year']}")
            self.time_idx, self.lat_idx, self.lon_idx = \
                tc.get_np_coords_cell_output(liv_data['consumptive_use_tot'],
                                             'livestock',
                                             config.cell_specific_output)

        # Run the irrigation simulation
        self.simulate_livestock()

        # print("Livestock simulation was performed. \n")

    def simulate_livestock(self):
        """Run livestock simulation with provided data and model equations."""
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

        if self.cso_flag:
            print('liv_consumptive_use_tot [m3/year]: {}'.format(
                self.consumptive_use_tot[self.time_idx,
                                         self.lat_idx,
                                         self.lon_idx]))

            print('liv_abstraction_tot [m3/year]: {}'.format(
                self.abstraction_tot[self.time_idx,
                                     self.lat_idx,
                                     self.lon_idx]))

            print('liv_fraction_gw_use [-]: {}'.format(
                self.fraction_gw_use))

            print('liv_consumptive_use_gw [m3/year]: {}'.format(
                self.consumptive_use_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('liv_consumptive_use_sw [m3/year]: {}'.format(
                self.consumptive_use_sw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('liv_abstraction_gw [m3/year]: {}'.format(
                self.abstraction_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('liv_abstraction_sw [m3/year]: {}'.format(
                self.abstraction_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('liv_return_flow_tot [m3/year]: {}'.format(
                self.return_flow_tot[self.time_idx,
                                     self.lat_idx,
                                     self.lon_idx]))

            print('liv_fraction_return_gw [-]: {}'.format(
                self.fraction_return_gw))

            print('liv_return_flow_gw [m3/year]: {}'.format(
                self.return_flow_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('liv_return_flow_sw [m3/year]: {}'.format(
                self.return_flow_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('liv_net_abstraction_gw [m3/year]: {}'.format(
                self.net_abstraction_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('liv_net_abstraction_sw [m3/year]: {}'.format(
                    self.net_abstraction_sw[self.time_idx,
                                            self.lat_idx,
                                            self.lon_idx]))
            print()
