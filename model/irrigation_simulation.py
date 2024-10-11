# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

""" GWSWUSE irrigation simulation module."""

import time
import xarray as xr
from controller import configuration_module as cm
from model import model_equations as me
from model import time_unit_conversion as tc


class IrrigationSimulator:
    """
    Class to handle irrigation water use simulations in the GWSWUSE model.

    Attributes
    ----------
    consumptive_use_tot : numpy.ndarray
        Array of monthly consumptive use of total water in irrigation sector
        converted to daily values and adjusted for the simulation. Originally
        read as xr.DataArray.
        (input and adjusted)
    consumptive_use_gw : numpy.ndarray
        Array of consumptive use of groundwater in irrigation sector.
        (calculated)
    consumptive_use_sw : numpy.ndarray
        Array of consumptive use of surface water in irrigation sector.
        (calculated)
    abstraction_tot : numpy.ndarray
        Array of total water abstraction in irrigation sector.
        (calculated)
    abstraction_gw : numpy.ndarray
        Array of groundwater abstraction in irrigation sector.
        (calculated)
    abstraction_sw : numpy.ndarray
        Array of surface water abstraction in irrigation sector.
        (calculated)
    return_flow_tot : numpy.ndarray
        Array of total return flow of water use in irrigation sector.
        (calculated)
    return_flow_gw : numpy.ndarray
        Array of return flow to groundwater of water use in irrigation sector.
        (calculated)
    return_flow_sw : numpy.ndarray
        Array of return flow to surface water of water use in irrigation
        sector.
        (calculated)
    net_abstraction_gw : numpy.ndarray
        Array of net abstraction of groundwater in irrigation sector.
        (calculated)
    net_abstraction_sw : numpy.ndarray
        Array of net abstraction of surface water in irrigation sector.
        (calculated)
    fraction_gw_use : numpy.ndarray or int
        Array of fractions of consumptive use from groundwater in irrigation
        sector or 0 if not provided. Originally read as xr.DataArray.
        (input)
    fraction_return_gw : numpy.ndarray or int
        Array of fractions of return flow to groundwater in irrigation sector
        or 0 if not provided. Originally read as xr.DataArray.
        (input)
    gwd_mask : numpy.ndarray
        Groundwater depletion mask array for the irrigation sector.
        (input)
    abstraction_irr_part_mask : numpy.ndarray
        Abstraction irrigation part mask array for the irrigation sector.
        (input)
    deficit_irrigation_location : numpy.ndarray
        Locations with irrigation deficits for the irrigation sector.
        (calculated)
    fraction_aai_aei : numpy.ndarray
        Yearly country-specific fraction of area actually irrigated (aai) and
        area equipped for irrigation (aei).
        (input)
    time_factor_aai : numpy.ndarray
        Time factor array for the irrigation sector.
        (input)
    irrigation_efficiency_sw : numpy.ndarray
        Array for irrigation efficiency with surface water abstraction
        infrastructure.
        (input)
    irrigation_efficiency_gw : numpy.ndarray
        Array for irrigation efficiency with groundwater abstraction
        infrastructure.
        (calculated)
    coords : xarray.Coordinates
        Coordinates from the original dataset.
        (input)
    """

    def __init__(self, irr_data):
        """
        Initialize the IrrigationSimulator with data and run the simulation.

        Parameters
        ----------
        irr_data : dict
            Dictionary containing xarray.DataArrays for various irrigation
            variables.
        """

        # Set total consumptive use input [m3/month]
        self.consumptive_use_tot = irr_data['consumptive_use_tot'].values

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (irr_data['fraction_gw_use'].values
             if 'fraction_gw_use' in irr_data and
             isinstance(irr_data['fraction_gw_use'], xr.DataArray)
             else 0)
        # Set fraction of groundwater return, default to 0 if not provided
        self.fraction_return_gw = \
            (irr_data['fraction_return_gw'].values
             if 'fraction_return_gw' in irr_data and
             isinstance(irr_data['fraction_return_gw'], xr.DataArray)
             else 0)

        # Set groundwater depletion mask
        self.gwd_mask = irr_data['gwd_mask'].values

        # Set abstraction irrigation part mask
        self.abstraction_irr_part_mask = \
            irr_data['abstraction_irr_part_mask'].values

        # Determine deficit irrigation locations
        self.deficit_irrigation_location = \
            me.set_irr_deficit_locations(self.gwd_mask,
                                         self.abstraction_irr_part_mask,
                                         cm.deficit_irrigation_factor)

        # Set fraction_aai_aei
        self.fraction_aai_aei = irr_data['fraction_aai_aei'].values
        # Set time factor
        self.time_factor_aai = irr_data['time_factor_aai'].values

        # Set surface water efficiency
        self.irrigation_efficiency_sw = \
            irr_data['irrigation_efficiency_sw'].values

        # Determine groundwater efficiency based on surface water efficiency
        self.irrigation_efficiency_gw = \
            me.set_irr_efficiency_gw(self.irrigation_efficiency_sw,
                                     cm.efficiency_gw_threshold,
                                     cm.efficiency_gw_mode)

        # Store the coordinates for transfer back to xr.DataArray
        self.coords = irr_data['consumptive_use_tot'].coords

        if cm.cell_specific_output['Flag']:
            print("'Irrigation-specific values for "
                  f"lat: {cm.cell_specific_output['coords']['lat']}, "
                  f"lon: {cm.cell_specific_output['coords']['lon']},\n"
                  f"year: {cm.cell_specific_output['coords']['year']}, "
                  f"month: {cm.cell_specific_output['coords']['month']}")
            self.time_idx, self.lat_idx, self.lon_idx = \
                tc.get_np_coords_cell_output(irr_data['consumptive_use_tot'],
                                             'irrigation',
                                             cm.cell_specific_output)
        # Run the irrigation simulation
        self.simulate_irrigation()

        print("\nIrrigation simulation was performed. \n ")

    def simulate_irrigation(self):
        """
        Run the irrigation simulation with provided data and model equations.
        """

        if cm.cell_specific_output['Flag']:
            print('irr_cu_tot_m3_month: '
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
        # Convert total consumptive use to m3/day
        self.consumptive_use_tot = \
            tc.convert_monthly_to_daily(self.consumptive_use_tot)
        if cm.cell_specific_output['Flag']:
            print('irr_cu_tot_m3_day: '
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
        # Calc total consumptive use in irrigation for area actually irrigated
        self.consumptive_use_tot = \
            me.calc_irr_consumptive_use_aai(
                self.consumptive_use_tot,
                self.fraction_aai_aei,
                cm.irrigation_input_based_on_aei
                )

        if cm.cell_specific_output['Flag'] and cm.irrigation_input_based_on_aei:
            print('irr_cu_tot_m3_day corrected by fraction_aai_aei: '
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')

        # Calc deficit total consumptive use in irrigation
        self.consumptive_use_tot = \
            me.calc_irr_deficit_consumptive_use_tot(
                self.consumptive_use_tot,
                self.deficit_irrigation_location,
                cm.deficit_irrigation_mode
                )
        if cm.cell_specific_output['Flag'] and cm.deficit_irrigation_mode:
            print('gwd_mask: '
                  f'{self.gwd_mask[self.lat_idx, self.lon_idx]}')
            print('abstraction_irr_part_mask: '
                  f'{self.abstraction_irr_part_mask[self.lat_idx, self.lon_idx]}')
            print('deficit_irrigation_factor: '
                  f'{self.deficit_irrigation_location[self.lat_idx, self.lon_idx]}')
            print('irr_cu_tot_deficit_m3_day: '
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')

        # Correct total consumptive use by time dev for area actually irrigated
        self.consumptive_use_tot = \
            me.correct_irr_consumptive_use_by_t_aai(
                self.consumptive_use_tot,
                self.time_factor_aai,
                cm.correct_irr_t_aai_mode
                )

        if cm.cell_specific_output['Flag'] and cm.correct_irr_t_aai_mode:
            print('t_aai: '
                  f'{self.time_factor_aai[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_cu_tot_m3_day corrected by t_aai: '
                  f'{self.consumptive_use_tot[self.time_idx, self.lat_idx, self.lon_idx]}')

        # Calc consumptive use from groundwater and surface water
        self.consumptive_use_gw, self.consumptive_use_sw = \
            me.calc_gwsw_water_use(
                self.consumptive_use_tot,
                self.fraction_gw_use
                )
        if cm.cell_specific_output['Flag']:
            print('irr_f_gw_use: '
                  f'{self.fraction_gw_use[self.lat_idx, self.lon_idx]}')
            print('irr_cu_gw_m3_day: '
                  f'{self.consumptive_use_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_cu_sw_m3_day: '
                  f'{self.consumptive_use_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
        # Calc total and split abstractions for groundwater and surface water
        self.abstraction_gw, self.abstraction_sw, self.abstraction_tot = \
            me.calc_irr_abstraction_totgwsw(self.consumptive_use_gw,
                                            self.irrigation_efficiency_gw,
                                            self.consumptive_use_sw,
                                            self.irrigation_efficiency_sw)
        if cm.cell_specific_output['Flag']:
            print('irr_eff_gw: '
                  f'{self.irrigation_efficiency_gw[self.lat_idx, self.lon_idx]}')
            print('irr_wu_gw_m3_day: '
                  f'{self.abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_eff_sw: '
                  f'{self.irrigation_efficiency_sw[self.lat_idx, self.lon_idx]}')
            print('irr_wu_sw_m3_day: '
                  f'{self.abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_wu_tot_m3_day: '
                  f'{self.abstraction_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
        # Calc and split return flows to groundwater and surface water
        self.return_flow_tot, self.return_flow_gw, self.return_flow_sw = \
            me.calc_return_flow_totgwsw(self.abstraction_tot,
                                        self.consumptive_use_tot,
                                        self.fraction_return_gw)
        if cm.cell_specific_output['Flag']:
            print('irr_rf_tot_m3_day: '
                  f'{self.return_flow_tot[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_f_gw_return: '
                  f'{self.fraction_return_gw[self.lat_idx, self.lon_idx]}')
            print('irr_rf_gw_m3_day: '
                  f'{self.return_flow_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_rf_sw_m3_day: '
                  f'{self.return_flow_sw[self.time_idx, self.lat_idx, self.lon_idx]}')

        # Calc net abstractions from groundwater and surface water
        self.net_abstraction_gw, self.net_abstraction_sw = \
            me.calc_net_abstraction_gwsw(self.abstraction_gw,
                                         self.return_flow_gw,
                                         self.abstraction_sw,
                                         self.return_flow_sw)
        if cm.cell_specific_output['Flag']:
            print('irr_na_gw_m3_day: '
                  f'{self.net_abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_na_sw_m3_day: '
                  f'{self.net_abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}')
            print('irr_na_tot_m3_day: '
                  f'{self.net_abstraction_gw[self.time_idx, self.lat_idx, self.lon_idx] + self.net_abstraction_sw[self.time_idx, self.lat_idx, self.lon_idx]}\n')


if __name__ == "__main__":
    # from controller import configuration_module as cm
    from controller import input_data_manager as idm

    preprocessed_gwswuse_data, _, _, _ = \
        idm.input_data_manager(cm.input_data_path,
                               cm.gwswuse_convention_path,
                               cm.start_year,
                               cm.end_year,
                               cm.time_extend_mode
                               )
    irr = IrrigationSimulator(preprocessed_gwswuse_data['irrigation'])
