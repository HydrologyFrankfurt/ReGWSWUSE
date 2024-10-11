# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

""" GWSWUSE thermal power simulation module."""

import xarray as xr
from controller import configuration_module as cm
from model import model_equations as me
from model import time_unit_conversion as tc


class ThermalPowerSimulator:
    """
    Class to handle thermal power water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Array of yearly consumptive use of total water in thermal power sector
        converted to daily values. Originally read as xr.DataArray.
        (input)
    consumptive_use_gw : numpy.ndarray
        Array of consumptive use of groundwater in thermal power sector.
        (calculated)
    consumptive_use_sw : numpy.ndarray
        Array of consumptive use of surface water in thermal power sector.
        (calculated)
    abstraction_tot : numpy.ndarray
        Array of yearly abstraction of total water in thermal power sector
        converted to daily values. Originally read as xr.DataArray.
        (input)
    abstraction_tot : numpy.ndarray
        Array of total water abstraction in thermal power sector.
        (calculated)
    abstraction_gw : numpy.ndarray
        Array of groundwater abstraction in thermal power sector.
        (calculated)
    abstraction_sw : numpy.ndarray
        Array of surface water abstraction in thermal power sector.
        (calculated)
    return_flow_tot : numpy.ndarray
        Array of total return flow of water use in thermal power sector.
        (calculated)
    return_flow_gw : numpy.ndarray
        Array of return flow to groundwater of water use in thermal power
        sector.
        (calculated)
    return_flow_sw : numpy.ndarray
        Array of return flow to surface water of water use in thermal power
        sector.
        (calculated)
    net_abstraction_gw : numpy.ndarray
        Array of net abstraction of groundwater in thermal power sector.
        (calculated)
    net_abstraction_sw : numpy.ndarray
        Array of net abstraction of surface water in thermal power sector.
        (calculated)
    fraction_gw_use : numpy.ndarray or int
        Array of fractions of consumptive use from groundwater in thermal power
        sector or 0 if not provided. Originally read as xr.DataArray.
        (input)
    fraction_return_gw : numpy.ndarray or int
        Array of fractions of return flow to groundwater in thermal power
        sector or 0 if not provided. Originally read as xr.DataArray.
        (input)
    coords : xarray.Coordinates
        Coordinates from the original dataset.
        (input)
    """

    def __init__(self, tp_data):
        """
        Initialize the ThermalPowerSimulator with data and run the simulation.

        Parameters
        ----------
        tp_data : dict
            Dictionary containing xarray.DataArrays for various thermal power
            variables.
        """
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

        if cm.cell_specific_output['Flag']:
            print("Thermal power specific values for "
                  f"lat: {cm.cell_specific_output['coords']['lat']}, "
                  f"lon: {cm.cell_specific_output['coords']['lon']},"
                  f"year: {cm.cell_specific_output['coords']['year']}")
            self.time_idx, self.lat_idx, self.lon_idx = \
                tc.get_np_coords_cell_output(tp_data['consumptive_use_tot'],
                                             'thermal_power',
                                             cm.cell_specific_output)

        # Run the irrigation simulation
        self.simulate_thermal_power()

        # print("Thermal power simulation was performed. \n")

    def simulate_thermal_power(self):
        """Run thermal power simulation with provided data and model equations."""
        if cm.cell_specific_output['Flag']:
            print('tp_cu_tot_m3_year:'
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_wu_tot_m3_year:'
                  f'{self.abstraction_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
        # Convert total consumptive use to m3/day
        self.consumptive_use_tot = \
            tc.convert_yearly_to_daily(self.consumptive_use_tot)

        # Convert total abstraction to m3/day
        self.abstraction_tot = \
            tc.convert_yearly_to_daily(self.abstraction_tot)

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

        if cm.cell_specific_output['Flag']:
            print('tp_cu_tot_m3_day:'
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_wu_tot_m3_day:'
                  f'{self.abstraction_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_f_gw_use:'
                  f'{self.fraction_gw_use}')
            print('tp_cu_gw_m3_day:'
                  f'{self.consumptive_use_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_cu_sw_m3_day:'
                  f'{self.consumptive_use_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_wu_gw_m3_day:'
                  f'{self.abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_wu_sw_m3_day:'
                  f'{self.abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_rf_tot_m3_day:'
                  f'{self.return_flow_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_f_gw_return:'
                  f'{self.fraction_return_gw}')
            print('tp_rf_gw_m3_day:'
                  f'{self.return_flow_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_rf_sw_m3_day:'
                  f'{self.return_flow_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_na_gw_m3_day:'
                  f'{self.net_abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('tp_na_sw_m3_day:'
                  f'{self.net_abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')


if __name__ == "__main__":
    from controller import configuration_module as cm
    from controller import input_data_manager as idm

    preprocessed_gwswuse_data, _, _, _ = \
        input_data_manager(cm.input_data_path,
                           cm.gwswuse_convention_path,
                           cm.start_year,
                           cm.end_year,
                           cm.correct_irr_t_aai_mode,
                           cm.time_extend_mode
                           )

    tp = ThermalPowerSimulator(preprocessed_gwswuse_data['thermal_power'])
