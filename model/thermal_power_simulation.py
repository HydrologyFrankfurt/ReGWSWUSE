# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE thermal power simulation module."""

import xarray as xr
from gwswuse_logger import get_logger
from model import model_equations as me
from model import utils as ut

logger = get_logger(__name__)


class ThermalPowerSimulator:
    """
    Class to handle thermal power water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Thermal power specific consumptive use of total water resources.
        Originally read as xr.DataArray. (input)
    consumptive_use_gw : numpy.ndarray
        Thermal power specific consumptive use of groundwater. (calculated)
    consumptive_use_sw : numpy.ndarray
        Thermal power specific consumptive water use of surface waters.
        (calculated)
    abstraction_tot : numpy.ndarray
        Thermal power specific abstraction of total water resources. Originally
        read as xr.DataArray. (input)
    abstraction_gw : numpy.ndarray
        Thermal power specific abstraction of groundwater. (calculated)
    abstraction_sw : numpy.ndarray
        Thermal power specific abstraction of surface waters. (calculated)
    return_flow_tot : numpy.ndarray
        Thermal power specific total return flow, calculated as the difference
        between abstraction and consumptive use of total water resources.
        (calculated)
    return_flow_gw : numpy.ndarray
        Thermal power specific return flows into groundwater. (calculated)
    return_flow_sw : numpy.ndarray
        Thermal power specific return flows into surface waters. (calculated)
    net_abstraction_gw : numpy.ndarray
        Thermal power specific net abstraction of groundwater. (calculated)
    net_abstraction_sw : numpy.ndarray
        Thermal power specific net abstraction of surface waters. (calculated)
    fraction_gw_use : numpy.ndarray or int
        Thermal power specific relative fraction of groundwater use. Originally
        provided as xr.DataArray or set to 0. (input)
    fraction_return_gw : numpy.ndarray or int
        Thermal power specific relative fraction of return flow to groundwater.
        Originally provided as xr.DataArray or set to 0. (input)
    coords : xarray.Coordinates
        Coordinates of the original dataset for thermal power specific
        consumptive use of total water resources. (input)
    """

    def __init__(self, tp_data, config):
        """
        Initialize the ThermalPowerSimulator with data and run the simulation.

        Parameters
        ----------
        tp_data : dict
            Dictionary containing xarray.DataArrays for various thermal power
            variables.
        """
        self.sector_name = 'thermal power'
        # Initialize relevant configuration settings
        self.csp_flag = config.cell_specific_output['flag']

        # Set unit
        self.unit = tp_data['unit']

        # Set total consumptive use input [m3/year]
        self.consumptive_use_tot = tp_data['consumptive_use_tot'].values

        # Set total abstraction input [m3/year]
        self.abstraction_tot = tp_data['abstraction_tot'].values

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (tp_data['fraction_gw_use'].values
             if 'fraction_gw_use' in tp_data and
             isinstance(tp_data['fraction_gw_use'], xr.DataArray)
             else 0)
        # Set fraction of groundwater return, default to 0 if not provided
        self.fraction_return_gw = \
            (tp_data['fraction_return_gw'].values
             if 'fraction_return_gw' in tp_data and
             isinstance(tp_data['fraction_return_gw'], xr.DataArray)
             else 0)
        # Store the coordinates for later use
        self.coords = tp_data['consumptive_use_tot'].coords
        # print headline for cell simulation prints
        ut.print_cell_output_headline(
            self.sector_name, config.cell_specific_output, self.csp_flag
            )
        # get idx for coords for cell specific output
        self.coords_idx = ut.get_np_coords_cell_idx(
            tp_data['consumptive_use_tot'], 'thermal_power',
            config.cell_specific_output, self.csp_flag
            )

        # Run the irrigation simulation
        self.simulate_thermal_power()

        ut.test_net_abstraction_tot(self.consumptive_use_tot,
                                    self.net_abstraction_gw,
                                    self.net_abstraction_sw,
                                    self.sector_name
                                    )

    def simulate_thermal_power(self):
        """Run thermal power simulation with provided data."""
        # Calc consumptive use of groundwater and surface water
        self.consumptive_use_gw, self.consumptive_use_sw = \
            me.calc_gwsw_water_use(self.consumptive_use_tot,
                                   self.fraction_gw_use)

        # Calc abstraction of groundwater and surface water
        self.abstraction_gw, self.abstraction_sw = \
            me.calc_gwsw_water_use(self.abstraction_tot,
                                   self.fraction_gw_use)

        # Calc and split return flows to groundwater and surface water
        self.return_flow_tot, self.return_flow_gw, self.return_flow_sw = \
            me.calc_return_flow_totgwsw(self.abstraction_tot,
                                        self.consumptive_use_tot,
                                        self.fraction_return_gw)

        # Calc net abstractions of groundwater and surface water
        self.net_abstraction_gw, self.net_abstraction_sw = \
            me.calc_net_abstraction_gwsw(self.abstraction_gw,
                                         self.return_flow_gw,
                                         self.abstraction_sw,
                                         self.return_flow_sw)

        ut.print_cell_value(
            self.consumptive_use_tot, 'tp_consumptive_use_tot',
            self.coords_idx, self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.abstraction_tot, 'tp_abstraction_tot', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.fraction_gw_use, 'tp_fraction_gw_use', self.coords_idx,
            flag=self.csp_flag
            )
        ut.print_cell_value(
            self.consumptive_use_gw, 'tp_consumptive_use_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.consumptive_use_sw, 'tp_consumptive_use_sw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.abstraction_gw, 'tp_abstraction_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.abstraction_sw, 'tp_abstraction_sw', self.coords_idx,
            self.unit, self.csp_flag)
        ut.print_cell_value(
            self.return_flow_tot, 'tp_return_flow_tot', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.fraction_return_gw, 'tp_fraction_return_gw', self.coords_idx,
            flag=self.csp_flag
            )
        ut.print_cell_value(
            self.return_flow_gw, 'tp_return_flow_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.return_flow_sw, 'tp_return_flow_sw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.net_abstraction_gw, 'tp_net_abstraction_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.net_abstraction_sw, 'tp_net_abstraction_sw', self.coords_idx,
            self.unit, self.csp_flag
            )
