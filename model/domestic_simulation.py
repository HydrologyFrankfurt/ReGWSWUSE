# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
""" GWSWUSE domestic simulation module."""

import os
import xarray as xr
from controller import configuration_module as cm
from model import model_equations as me
from model import time_unit_conversion as tc

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

    def __init__(self, dom_data):
        """
        Initialize the DomesticSimulator with data and run the simulation.

        Parameters
        ----------
        dom_data : dict
            Dictionary containing xarray.DataArrays for various domestic
            variables.
        """
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

        if cm.cell_specific_output['Flag']:
            print("Domestic specific values for "
                  f"lat: {cm.cell_specific_output['coords']['lat']}, "
                  f"lon: {cm.cell_specific_output['coords']['lon']},\n"
                  f"year: {cm.cell_specific_output['coords']['year']}")
            self.time_idx, self.lat_idx, self.lon_idx = \
                tc.get_np_coords_cell_output(dom_data['consumptive_use_tot'],
                                             'domestic',
                                             cm.cell_specific_output)

        # Run the domestic simulation
        self.simulate_domestic()

        # print("Domestic simulation was performed. \n")

    def simulate_domestic(self):
        """Run domestic simulation with provided data and model equations."""
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

        # pylint: disable=consider-using-f-string
        if cm.cell_specific_output['Flag']:
            print('dom_consumptive_use_tot [m3/year]: {}'.format(
                self.consumptive_use_tot[self.time_idx,
                                          self.lat_idx,
                                          self.lon_idx]))

            print('dom_abstraction_tot [m3/year]: {}'.format(
                self.abstraction_tot[self.time_idx,
                                      self.lat_idx,
                                      self.lon_idx]))

            print('dom_fraction_gw_use [-]: {}'.format(
                self.fraction_gw_use[self.lat_idx,
                                      self.lon_idx]))

            print('dom_consumptive_use_gw [m3/year]: {}'.format(
                self.consumptive_use_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('dom_consumptive_use_sw [m3/year]: {}'.format(
                self.consumptive_use_sw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('dom_abstraction_gw [m3/year]: {}'.format(
                self.abstraction_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('dom_abstraction_sw [m3/year]: {}'.format(
                self.abstraction_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('dom_return_flow_tot [m3/year]: {}'.format(
                self.return_flow_tot[self.time_idx,
                                      self.lat_idx,
                                      self.lon_idx]))

            print('dom_fraction_return_gw [-]: {}'.format(
                self.fraction_return_gw))

            print('dom_return_flow_gw [m3/year]: {}'.format(
                self.return_flow_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('dom_return_flow_sw [m3/year]: {}'.format(
                self.return_flow_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('dom_net_abstraction_gw [m3/year]: {}'.format(
                self.net_abstraction_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('dom_net_abstraction_sw [m3/year]: {} \n'.format(
                    self.net_abstraction_sw[self.time_idx,
                                            self.lat_idx,
                                            self.lon_idx]))


# if __name__ == "__main__":
#     from controller import input_data_manager as idm

#     preprocessed_gwswuse_data, _, _, _ = \
#         idm.input_data_manager(cm.input_data_path,
#                                cm.gwswuse_convention_path,
#                                cm.start_year,
#                                cm.end_year,
#                                cm.time_extend_mode
#                                )
#     dom = DomesticSimulator(preprocessed_gwswuse_data['domestic'])
