# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

""" GWSWUSE total sectors simulation module."""

import os

from controller import configuration_module as cm
from model import model_equations as me

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # =============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]


class TotalSectorsSimulator():
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Sum sector-specific volume per time variables across all sectors.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Array of consumptive of total water summed across all sectors.
        (calculated)
    consumptive_use_gw : numpy.ndarray
        Array of consumptive use of groundwater summed across all sectors.
        (calculated)
    consumptive_use_sw : numpy.ndarray
        Array of consumptive use of surface water summed across all sectors.
        (calculated)
    abstraction_tot : numpy.ndarray
        Array of abstraction of total water summed across all sectors.
        (calculated)
    abstraction_gw : numpy.ndarray
       Array of abstraction of groundwater summed across all sectors.
        (calculated)
    abstraction_sw : numpy.ndarray
        Array of abstraction of surface water summed across all sectors.
        (calculated)
    return_flow_tot : numpy.ndarray
        Array of total return flow of water use across all sectors.
        (calculated)
    return_flow_gw : numpy.ndarray
        Array of return flow to groundwater of water use across all sectors.
        (calculated)
    return_flow_sw : numpy.ndarray
        Array of return flow to surface water of water use across all sectors.
        (calculated)
    net_abstraction_gw : numpy.ndarray
        Array of net abstraction of groundwater summed across all sectors.
        (calculated)
    net_abstraction_sw : numpy.ndarray
        Array of net abstraction of surface water summed across all sectors.
        (calculated)
    fraction_gw_use : None
        Array of fraction of groundwater use across all sectors calculated as
        quotient of consumptive_use_gw across all sectors and
        consumptive_use_tot across all sectors.
        (Calculated)
    fraction_return_to_gw : None
        Placeholder for the fraction of return flow to groundwater.
        (input)
    coords : xarray.Coordinates
        Coordinates from the original dataset of the irrigation sector.
        (input)
    """

    def __init__(self, irr, dom, man, tp, liv):
        """
        Initialize the TotalSectorsSimulator with data from all sectors.

        Parameters
        ----------
        irr : SectorData
            Irrigation sector data.
        dom : SectorData
            Domestic sector data.
        man : SectorData
            Manufacturing sector data.
        tp : SectorData
            Thermal power sector data.
        liv : SectorData
            Livestock sector data.
        """
        # Sum total consumptive use across all sectors
        self.consumptive_use_tot = \
            me.calculate_cross_sector_totals(irr.consumptive_use_tot,
                                             dom.consumptive_use_tot,
                                             man.consumptive_use_tot,
                                             tp.consumptive_use_tot,
                                             liv.consumptive_use_tot)
        # Sum consumptive use of groundwater across all sectors
        self.consumptive_use_gw = \
            me.calculate_cross_sector_totals(irr.consumptive_use_gw,
                                             dom.consumptive_use_gw,
                                             man.consumptive_use_gw,
                                             tp.consumptive_use_gw,
                                             liv.consumptive_use_gw)
        # Sum consumptive use of surface water across all sectors
        self.consumptive_use_sw = \
            me.calculate_cross_sector_totals(irr.consumptive_use_sw,
                                             dom.consumptive_use_sw,
                                             man.consumptive_use_sw,
                                             tp.consumptive_use_sw,
                                             liv.consumptive_use_sw)
        # Sum total abstraction of water across all sectors
        self.abstraction_tot = \
            me.calculate_cross_sector_totals(irr.abstraction_tot,
                                             dom.abstraction_tot,
                                             man.abstraction_tot,
                                             tp.abstraction_tot,
                                             liv.abstraction_tot)
        # Sum abstraction of groundwater across all sectors
        self.abstraction_gw = \
            me.calculate_cross_sector_totals(irr.abstraction_gw,
                                             dom.abstraction_gw,
                                             man.abstraction_gw,
                                             tp.abstraction_gw,
                                             liv.abstraction_gw)
        # Sum abstraction of surface water across all sectors
        self.abstraction_sw = \
            me.calculate_cross_sector_totals(irr.abstraction_sw,
                                             dom.abstraction_sw,
                                             man.abstraction_sw,
                                             tp.abstraction_sw,
                                             liv.abstraction_sw)
        # Sum total return flow across all sectors
        self.return_flow_tot = \
            me.calculate_cross_sector_totals(irr.return_flow_tot,
                                             dom.return_flow_tot,
                                             man.return_flow_tot,
                                             tp.return_flow_tot,
                                             liv.return_flow_tot)
        # Sum return flow to groundwater across all sectors
        self.return_flow_gw = \
            me.calculate_cross_sector_totals(irr.return_flow_gw,
                                             dom.return_flow_gw,
                                             man.return_flow_gw,
                                             tp.return_flow_gw,
                                             liv.return_flow_gw)
        # Sum return flow to surface water across all sectors
        self.return_flow_sw = \
            me.calculate_cross_sector_totals(irr.return_flow_sw,
                                             dom.return_flow_sw,
                                             man.return_flow_sw,
                                             tp.return_flow_sw,
                                             liv.return_flow_sw)
        # Sum net abstraction of groundwater across all sectors
        self.net_abstraction_gw = \
            me.calculate_cross_sector_totals(irr.net_abstraction_gw,
                                             dom.net_abstraction_gw,
                                             man.net_abstraction_gw,
                                             tp.net_abstraction_gw,
                                             liv.net_abstraction_gw)
        # Sum net abstraction of surface water across all sectors
        self.net_abstraction_sw = \
            me.calculate_cross_sector_totals(irr.net_abstraction_sw,
                                             dom.net_abstraction_sw,
                                             man.net_abstraction_sw,
                                             tp.net_abstraction_sw,
                                             liv.net_abstraction_sw)

        # Calc fractions of groundwater use across all sectors
        self.fraction_gw_use, self.fraction_return_gw = \
            me.calculate_fractions(self.consumptive_use_gw,
                                   self.consumptive_use_tot,
                                   self.return_flow_gw,
                                   self.return_flow_tot)
        # Store coords for generating netcdf-output
        self.coords = irr.coords
        if cm.cell_specific_output['Flag']:
            print("Total specific values for lat: {lat}, lon: {lon}, "
                  "year: {year}, month: {month}".format(
                      lat=cm.cell_specific_output['coords']['lat'],
                      lon=cm.cell_specific_output['coords']['lon'],
                      year=cm.cell_specific_output['coords']['year'],
                      month=cm.cell_specific_output['coords']['month']
                  ))
            self.time_idx = irr.time_idx
            self.lat_idx = irr.lat_idx
            self.lon_idx = irr.lon_idx

            print('total_consumptive_use_tot [m3/month]: {}'.format(
                self.consumptive_use_tot[self.time_idx,
                                         self.lat_idx,
                                         self.lon_idx]))

            print('total_consumptive_use_gw [m3/month]: {}'.format(
                self.consumptive_use_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('total_consumptive_use_sw [m3/month]: {}'.format(
                self.consumptive_use_sw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('total_abstraction_tot [m3/month]: {}'.format(
                self.abstraction_tot[self.time_idx,
                                     self.lat_idx,
                                     self.lon_idx]))

            print('total_abstraction_gw [m3/month]: {}'.format(
                self.abstraction_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('total_abstraction_sw [m3/month]: {}'.format(
                self.abstraction_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('total_rf_tot [m3/month]: {}'.format(
                self.return_flow_tot[self.time_idx,
                                     self.lat_idx,
                                     self.lon_idx]))

            print('total_rf_gw [m3/month]: {}'.format(
                self.return_flow_gw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('total_rf_sw [m3/month]: {}'.format(
                self.return_flow_sw[self.time_idx,
                                    self.lat_idx,
                                    self.lon_idx]))

            print('total_net_abstraction_gw [m3/month]: {}'.format(
                self.net_abstraction_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('total_net_abstraction_sw [m3/month]: {}'.format(
                self.net_abstraction_sw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))

            print('total_fraction_gw_use [-]: {}'.format(
                self.fraction_gw_use[self.time_idx,
                                     self.lat_idx,
                                     self.lon_idx]))

            print('total_fraction_return_gw [-]: {} \n'.format(
                self.fraction_return_gw[self.time_idx,
                                        self.lat_idx,
                                        self.lon_idx]))
