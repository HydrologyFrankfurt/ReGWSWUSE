# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

""" GWSWUSE total sectors simulation module."""

import time
from model import model_equations as me


class TotalSectorsSimulator():
    """
    Sum sector-specific volume per time variables.

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
        Placeholder for the fraction of groundwater use.
        (input)
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
        start_time = time.time()

        # Sum total consumptive use across all sectors
        self.consumptive_use_tot = \
            me.sum_volume_per_time_variable(irr.consumptive_use_tot,
                                            dom.consumptive_use_tot,
                                            man.consumptive_use_tot,
                                            tp.consumptive_use_tot,
                                            liv.consumptive_use_tot)
        # Sum consumptive use of groundwater across all sectors
        self.consumptive_use_gw = \
            me.sum_volume_per_time_variable(irr.consumptive_use_gw,
                                            dom.consumptive_use_gw,
                                            man.consumptive_use_gw,
                                            tp.consumptive_use_gw,
                                            liv.consumptive_use_gw)
        # Sum consumptive use of surface water across all sectors
        self.consumptive_use_sw = \
            me.sum_volume_per_time_variable(irr.consumptive_use_sw,
                                            dom.consumptive_use_sw,
                                            man.consumptive_use_sw,
                                            tp.consumptive_use_sw,
                                            liv.consumptive_use_sw)
        # Sum total abstraction of water across all sectors
        self.abstraction_tot = \
            me.sum_volume_per_time_variable(irr.abstraction_tot,
                                            dom.abstraction_tot,
                                            man.abstraction_tot,
                                            tp.abstraction_tot,
                                            liv.abstraction_tot)
        # Sum abstraction of groundwater across all sectors
        self.abstraction_gw = \
            me.sum_volume_per_time_variable(irr.abstraction_gw,
                                            dom.abstraction_gw,
                                            man.abstraction_gw,
                                            tp.abstraction_gw,
                                            liv.abstraction_gw)
        # Sum abstraction of surface water across all sectors
        self.abstraction_sw = \
            me.sum_volume_per_time_variable(irr.abstraction_sw,
                                            dom.abstraction_sw,
                                            man.abstraction_sw,
                                            tp.abstraction_sw,
                                            liv.abstraction_sw)
        # Sum total return flow across all sectors
        self.return_flow_tot = \
            me.sum_volume_per_time_variable(irr.return_flow_tot,
                                            dom.return_flow_tot,
                                            man.return_flow_tot,
                                            tp.return_flow_tot,
                                            liv.return_flow_tot)
        # Sum return flow to groundwater across all sectors
        self.return_flow_gw = \
            me.sum_volume_per_time_variable(irr.return_flow_gw,
                                            dom.return_flow_gw,
                                            man.return_flow_gw,
                                            tp.return_flow_gw,
                                            liv.return_flow_gw)
        # Sum return flow to surface water across all sectors
        self.return_flow_sw = \
            me.sum_volume_per_time_variable(irr.return_flow_sw,
                                            dom.return_flow_sw,
                                            man.return_flow_sw,
                                            tp.return_flow_sw,
                                            liv.return_flow_sw)
        # Sum net abstraction of groundwater across all sectors
        self.net_abstraction_gw = \
            me.sum_volume_per_time_variable(irr.net_abstraction_gw,
                                            dom.net_abstraction_gw,
                                            man.net_abstraction_gw,
                                            tp.net_abstraction_gw,
                                            liv.net_abstraction_gw)
        # Sum net abstraction of surface water across all sectors
        self.net_abstraction_sw = \
            me.sum_volume_per_time_variable(irr.net_abstraction_sw,
                                            dom.net_abstraction_sw,
                                            man.net_abstraction_sw,
                                            tp.net_abstraction_sw,
                                            liv.net_abstraction_sw)
        # Calc fractions of groundwater use across all sectors
        self.fraction_gw_use = \
            self.consumptive_use_gw/self.consumptive_use_tot
        # Calc fractions of total return flow to groundwater across all sectors
        self.fraction_return_to_gw = \
            self.return_flow_gw / self.return_flow_tot
        # Store coords for generating netcdf-output
        self.coords = irr.coords

        end_time = time.time()  # Endzeit messen
        print(f"Sectors summarizer runtime: {end_time - start_time} seconds.")
