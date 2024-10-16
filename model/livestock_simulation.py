# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

""" GWSWUSE livestock simulation module."""

import time
import xarray as xr
from controller import configuration_module as cm
from model import model_equations as me
from model import time_unit_conversion as tc


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

    def __init__(self, liv_data):
        """
        Initialize the LivestockSimulator with data and run the simulation.

        Parameters
        ----------
        liv_data : dict
            Dictionary containing xarray.DataArrays for various livestock
            variables.
        """
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

        if cm.cell_specific_output['Flag']:
            print("Livestock specific values for "
                  f"lat: {cm.cell_specific_output['coords']['lat']}, "
                  f"lon: {cm.cell_specific_output['coords']['lon']},"
                  f"year: {cm.cell_specific_output['coords']['year']}")
            self.time_idx, self.lat_idx, self.lon_idx = \
                tc.get_np_coords_cell_output(liv_data['consumptive_use_tot'],
                                             'livestock',
                                             cm.cell_specific_output)

        # Run the irrigation simulation
        self.simulate_livestock()

        print("Livestock simulation was performed. \n")

    def simulate_livestock(self):
        """
        Run the livestock simulation with provided data and model equations.
        """
        if cm.cell_specific_output['Flag']:
            print('liv_cu_tot_m3_year:'
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_wu_tot_m3_year:'
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
            print('liv_cu_tot_m3_day:'
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_wu_tot_m3_day:'
                  f'{self.abstraction_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_f_gw_use:'
                  f'{self.fraction_gw_use}')
            print('liv_cu_gw_m3_day:'
                  f'{self.consumptive_use_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_cu_sw_m3_day:'
                  f'{self.consumptive_use_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_wu_gw_m3_day:'
                  f'{self.abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_wu_sw_m3_day:'
                  f'{self.abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_rf_tot_m3_day:'
                  f'{self.return_flow_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_f_gw_return:'
                  f'{self.fraction_return_gw}')
            print('liv_rf_gw_m3_day:'
                  f'{self.return_flow_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_rf_sw_m3_day:'
                  f'{self.return_flow_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_na_gw_m3_day:'
                  f'{self.net_abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_na_sw_m3_day:'
                  f'{self.net_abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('liv_na_tot_m3_day:'
                  f'{self.net_abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx] + self.net_abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}\n')



if __name__ == "__main__":
    from controller import configuration_module as cm
    from controller import input_data_manager as idm

    preprocessed_gwswuse_data, _, _, _ = \
        idm.input_data_manager(cm.input_data_path,
                               cm.gwswuse_convention_path,
                               cm.start_year,
                               cm.end_year,
                               cm.time_extend_mode,
                               cm.correct_irr_with_t_aai_mode
                               )
    liv = LivestockSimulator(preprocessed_gwswuse_data['livestock'])