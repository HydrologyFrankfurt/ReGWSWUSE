# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE irrigation simulation module."""

import xarray as xr
from gwswuse_logger import get_logger
from model import model_equations as me
from model import utils as ut

logger = get_logger(__name__)


class IrrigationSimulator:
    """
    Class to handle irrigation water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Irrigation-specific consumptive use of total water resources.
        Originally read as xr.DataArray. (input)
    consumptive_use_gw : numpy.ndarray
        Irrigation-specific consumptive use of groundwater. (calculated)
    consumptive_use_sw : numpy.ndarray
        Irrigation-specific consumptive water use of surface waters.
        (calculated)
    abstraction_tot : numpy.ndarray
        Irrigation-specific abstraction of total water resources. (calculated)
    abstraction_gw : numpy.ndarray
        Irrigation-specific abstraction of groundwater. (calculated)
    abstraction_sw : numpy.ndarray
        Irrigation-specific abstraction of surface waters. (calculated)
    return_flow_tot : numpy.ndarray
        Irrigation-specific total return flow, calculated as the difference
        between abstraction and consumptive use of total water resources.
        (calculated)
    return_flow_gw : numpy.ndarray
        Irrigation-specific return flows into groundwater. (calculated)
    return_flow_sw : numpy.ndarray
        Irrigation-specific return flows into surface waters. (calculated)
    net_abstraction_gw : numpy.ndarray
        Irrigation-specific net abstraction of groundwater. (calculated)
    net_abstraction_sw : numpy.ndarray
        Irrigation-specific net abstraction of surface waters. (calculated)
    fraction_gw_use : numpy.ndarray or int
        Irrigation-specific relative fraction of groundwater use. Originally
        provided as xr.DataArray or set to 0. (input)
    fraction_return_gw : numpy.ndarray or int
        Irrigation-specific relative fraction of return flow to groundwater.
        Originally provided as xr.DataArray or set to 0. (input)
    gwd_mask : numpy.ndarray
        Grid mask for groundwater depletion larger than 5mm. (input)
    abstraction_irr_part_mask : numpy.ndarray
        Grid mask for the relative part of total water withdrawals by the
        irrigation sector larger than 5%.(input)
    deficit_irrigation_location : numpy.ndarray
        Grid representing deficit irrigation conditions, where cells meeting
        criteria have the specified deficit irrigation factor. (calculated)
    fraction_aai_aei : numpy.ndarray
        Fraction of areas actually irrigated to areas eqipped for irrgation on
        country level. (input)
    time_factor_aai : numpy.ndarray
        Temporal development factor of national areas actually irrigated for
        years 2016 till 2020 to reference year 2015. (input)
    irrigation_efficiency_sw : numpy.ndarray
        Irrigation efficiency for surface water abstraction infrastructure.
        (input)
    irrigation_efficiency_gw : numpy.ndarray
        Irrigation efficiency for groundwater abstraction infrastructure.
        (calculated)
    coords : xarray.Coordinates
        Coordinates of the original dataset for irrigation-specific consumptive
        use of total water resources. (input)
    """

    def __init__(self, irr_data, config):
        """
        Initialize the IrrigationSimulator with data and run the simulation.

        Parameters
        ----------
        irr_data : dict
            Dictionary containing xarray.DataArrays for various irrigation
            variables.
        """
        self.sector_name = 'irrigation'
        # Initialize configuration settings
        self.csp_flag = config.cell_specific_output['flag']

        self.irrigation_input_based_on_aei = \
            config.irrigation_input_based_on_aei
        self.correct_irrigation_t_aai_mode = \
            config.correct_irrigation_t_aai_mode
        self.deficit_irrigation_factor = config.deficit_irrigation_factor
        self.deficit_irrigation_mode = config.deficit_irrigation_mode
        self.efficiency_gw_mode = config.irrigation_efficiency_gw_mode
        self.efficiency_gw_threshold = config.efficiency_gw_threshold

        # Set unit
        self.unit = irr_data['unit']

        # Set total consumptive use input [m3/month]
        self.consumptive_use_tot = irr_data['consumptive_use_tot'].values

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (irr_data['fraction_gw_use'].values
             if 'fraction_gw_use' in irr_data and
             isinstance(irr_data['fraction_gw_use'], xr.DataArray)
             else 0)
        if isinstance(self.fraction_gw_use, int) and self.fraction_gw_use == 0:
            logger.info(
                "fraction_gw_use for %s is set to 0 by default. Differs from "
                "WaterGAP 2.2e", self.sector_name
                )
        # Set fraction of groundwater return, default to 0 if not provided
        self.fraction_return_gw = \
            (irr_data['fraction_return_gw'].values
             if 'fraction_return_gw' in irr_data and
             isinstance(irr_data['fraction_return_gw'], xr.DataArray)
             else 0)
        if (isinstance(self.fraction_return_gw, int) and
            self.fraction_return_gw == 0):
            logger.info(
                "fraction_return_gw for %s is set to 0 by default. Differs "
                "from WaterGAP 2.2e", self.sector_name
                )

        if self.deficit_irrigation_mode:
            # Set groundwater depletion mask
            self.gwd_mask = irr_data['gwd_mask'].values

            # Set abstraction irrigation part mask
            self.abstraction_irr_part_mask = \
                irr_data['abstraction_irr_part_mask'].values

            # Determine deficit irrigation locations
            self.deficit_irrigation_location = me.set_irr_deficit_locations(
                self.gwd_mask, self.abstraction_irr_part_mask,
                self.deficit_irrigation_factor)

        if self.irrigation_input_based_on_aei:
            # Set fraction_aai_aei
            self.fraction_aai_aei = irr_data['fraction_aai_aei'].values

        if self.correct_irrigation_t_aai_mode:
            # Set time factor
            self.time_factor_aai = irr_data['time_factor_aai'].values

        # Set surface water efficiency
        self.irrigation_efficiency_sw = \
            irr_data['irrigation_efficiency_sw'].values

        # Determine groundwater efficiency based on surface water efficiency
        self.irrigation_efficiency_gw = \
            me.set_irr_efficiency_gw(self.irrigation_efficiency_sw,
                                     self.efficiency_gw_threshold,
                                     self.efficiency_gw_mode)

        # Store the coordinates for transfer back to xr.DataArray
        self.coords = irr_data['consumptive_use_tot'].coords

        # print headline for cell simulation prints
        ut.print_cell_output_headline(
            self.sector_name, config.cell_specific_output, self.csp_flag
            )
        # get idx for coords for cell specific output
        self.coords_idx = ut.get_np_coords_cell_idx(
            irr_data['consumptive_use_tot'], 'irrigation',
            config.cell_specific_output, self.csp_flag
            )
        # Run the irrigation simulation
        self.simulate_irrigation()

        ut.test_net_abstraction_tot(self.consumptive_use_tot,
                                    self.net_abstraction_gw,
                                    self.net_abstraction_sw,
                                    self.sector_name
                                    )

    def simulate_irrigation(self):
        """Run irrigation simulation with provided data and model equations."""
        ut.print_cell_value(
            self.consumptive_use_tot, 'consumptive_use_tot', self.coords_idx,
            self.unit, self.csp_flag
            )

        # Calc total consumptive use in irrigation for area actually irrigated
        if self.irrigation_input_based_on_aei:
            self.consumptive_use_tot = \
                me.calc_irr_consumptive_use_aai(
                    self.consumptive_use_tot,
                    self.fraction_aai_aei
                    )
            ut.print_cell_value(
                self.fraction_aai_aei, 'fraction_aai_aei', self.coords_idx,
                flag=self.csp_flag
                )
            ut.print_cell_value(
                self.consumptive_use_tot, 'consumptive_use_tot corrected by '
                'fraction_aai_aei', self.coords_idx, self.unit, self.csp_flag
                )

        if self.deficit_irrigation_mode:
            # Calc deficit total consumptive use in irrigation
            self.consumptive_use_tot = \
                me.calc_irr_deficit_consumptive_use_tot(
                    self.consumptive_use_tot,
                    self.deficit_irrigation_location
                    )
            ut.print_cell_value(
                self.gwd_mask, 'gwd_mask', self.coords_idx, 'bool',
                self.csp_flag
                )
            ut.print_cell_value(
                self.abstraction_irr_part_mask, 'abstraction_irr_part_mask',
                self.coords_idx, 'bool', self.csp_flag
                )
            ut.print_cell_value(
                self.deficit_irrigation_location,
                'deficit_irrigation_location_factor',
                self.coords_idx, flag=self.csp_flag
                )
            ut.print_cell_value(
                self.consumptive_use_tot, 'consumptive_use_tot_deficit',
                self.coords_idx, self.unit, self.csp_flag
                )

        # Correct total consumptive use by time dev for area actually irrigated
        if self.correct_irrigation_t_aai_mode:
            self.consumptive_use_tot = \
                me.correct_irr_consumptive_use_by_t_aai(
                    self.consumptive_use_tot, self.time_factor_aai
                    )
            ut.print_cell_value(
                self.time_factor_aai, 'time_factor_aai', self.coords_idx,
                flag=self.csp_flag
                )
            ut.print_cell_value(
                self.consumptive_use_tot,
                'consumptive_use_tot corrected by time_factor_aai',
                self.coords_idx, self.unit, self.csp_flag
                )

        # Calc consumptive use of groundwater and surface water
        self.consumptive_use_gw, self.consumptive_use_sw = \
            me.calc_gwsw_water_use(
                self.consumptive_use_tot,
                self.fraction_gw_use
                )

        # Calc total and split abstractions for groundwater and surface water
        self.abstraction_gw, self.abstraction_sw, self.abstraction_tot = \
            me.calc_irr_abstraction_totgwsw(self.consumptive_use_gw,
                                            self.irrigation_efficiency_gw,
                                            self.consumptive_use_sw,
                                            self.irrigation_efficiency_sw)

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
            self.fraction_gw_use, 'fraction_gw_use', self.coords_idx,
            flag=self.csp_flag
            )
        ut.print_cell_value(
            self.consumptive_use_gw, 'consumptive_use_gw', self.coords_idx,
            self.unit, self.csp_flag)
        ut.print_cell_value(
            self.consumptive_use_sw, 'consumptive_use_sw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.irrigation_efficiency_gw, 'irrigation_efficiency_gw',
            self.coords_idx, flag=self.csp_flag
            )
        ut.print_cell_value(
            self.abstraction_gw, 'abstraction_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.irrigation_efficiency_sw, 'irrigation_efficiency_sw',
            self.coords_idx, flag=self.csp_flag)
        ut.print_cell_value(
            self.abstraction_sw, 'abstraction_sw', self.coords_idx, self.unit,
            self.csp_flag)
        ut.print_cell_value(
            self.abstraction_tot, 'abstraction_tot', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.return_flow_tot, 'return_flow_tot', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.fraction_return_gw, 'fraction_return_gw', self.coords_idx,
            flag=self.csp_flag
            )
        ut.print_cell_value(
            self.return_flow_gw, 'return_flow_gw', self.coords_idx, self.unit,
            self.csp_flag
            )
        ut.print_cell_value(
            self.return_flow_sw, 'return_flow_sw', self.coords_idx, self.unit,
            self.csp_flag
            )
        ut.print_cell_value(
            self.net_abstraction_gw, 'net_abstraction_gw', self.coords_idx,
            self.unit, self.csp_flag
            )
        ut.print_cell_value(
            self.net_abstraction_sw, 'net_abstraction_sw', self.coords_idx,
            self.unit, self.csp_flag
            )
