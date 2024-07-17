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
        start_time = time.time()
        # Convert total consumptive use to daily values
        self.consumptive_use_tot = \
            tc.convert_monthly_to_daily(irr_data['consumptive_use_tot'].values)

        # Set fraction of groundwater use, default to 0 if not provided
        self.fraction_gw_use = \
            (irr_data['fraction_gw_use'].values
             if 'fraction_return_gw' in irr_data and
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

        # Run the irrigation simulation
        self.simulate_irrigation()

        end_time = time.time()
        print(f"Irrigation simulation runtime: {end_time - start_time} "
              "seconds.")

    def simulate_irrigation(self):
        """
        Run the irrigation simulation with provided data and model equations.
        """
        print("Running irrigation simulation...")

        # Calc deficit total consumptive use in irrigation
        self.consumptive_use_tot = \
            me.calc_irr_deficit_consumptive_use_tot(
                self.consumptive_use_tot,
                self.deficit_irrigation_location,
                cm.deficit_irrigation_mode
                )

        # Correct total consumptive use by time dev for area actually irrigated
        self.consumptive_use_tot = \
            me.calc_irr_consumptive_use_correct_by_t_aai(
                self.consumptive_use_tot,
                self.time_factor_aai,
                cm.correct_irr_with_t_aai_mode
                )

        # Calc consumptive use from groundwater and surface water
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

        # Calc net abstractions from groundwater and surface water
        self.net_abstraction_gw, self.net_abstraction_sw = \
            me.calc_net_abstraction_gwsw(self.abstraction_gw,
                                         self.return_flow_gw,
                                         self.abstraction_sw,
                                         self.return_flow_sw)


if __name__ == "__main__":
    # from controller import configuration_module as cm
    from controller import input_data_manager_new as idm

    preprocessed_gwswuse_data, _, _, _ = \
        idm.input_data_manager(cm.input_path,
                               cm.gwswuse_convention_path,
                               cm.start_year,
                               cm.end_year,
                               cm.time_extend_mode,
                               cm.correct_irr_with_t_aai_mode
                               )
    irr = IrrigationSimulator(preprocessed_gwswuse_data['irrigation'])
