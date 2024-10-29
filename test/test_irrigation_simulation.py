# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Test GWSWUSE irrigation simulation module."""


import unittest
import numpy as np
import xarray as xr
from model import model_equations as me
from misc import cell_simulation_printer as csp
from model.irrigation_simulation import IrrigationSimulator
from unittest.mock import patch, MagicMock


class TestIrrigationSimulator(unittest.TestCase):
    """Test for IrrigationSimulator to check initialization and calculations."""

    def setUp(self):
        """Set up mock data and configuration for testing."""
        # Mock data simulating xarray DataArray input
        self.use = \
            xr.DataArray(np.array([[[1.0], [np.nan]], [[2.0], [3.0]]]))
        # self.irr_data = {
        #     'consumptive_use_tot': xr.DataArray(np.array([[[1.0], [np.nan]], [[2.0], [3.0]]])),
        #     'fraction_gw_use': xr.DataArray(np.array([[0.4], [0.6]])),
        #     'fraction_return_gw': xr.DataArray(np.array([[0.1], [0.2]])),
        #     'gwd_mask': xr.DataArray(np.array([[1], [0]])),
        #     'abstraction_irr_part_mask': xr.DataArray(np.array([[1], [1]])),
        #     'fraction_aai_aei': xr.DataArray(np.array([[0.4], [0.6]])),
        #     'time_factor_aai': xr.DataArray(np.array([[0.4], [0.6]])),
        #     'irrigation_efficiency_sw': xr.DataArray(np.array([[0.7], [0.8]])),
        #     'unit': 'm3/month'
        #     }
        self.irr_data = {
            'consumptive_use_tot': xr.DataArray(np.array([[[1.0], [np.nan]], [[2.0], [3.0]]]), dims=['x', 'y', 'z']),
            'fraction_gw_use': xr.DataArray(np.array([[[0.4], [0.5]]]), dims=['x', 'y', 'z']),
            'fraction_return_gw': xr.DataArray(np.array([[[0.1], [0.2]]]), dims=['x', 'y', 'z']),
            'gwd_mask': xr.DataArray(np.array([[[1], [0]]]), dims=['x', 'y', 'z']),
            'abstraction_irr_part_mask': xr.DataArray(np.array([[[1], [1]]]), dims=['x', 'y', 'z']),
            'fraction_aai_aei': xr.DataArray(np.array([[[0.4], [0.5]], [[0.6], [0.7]]]), dims=['x', 'y', 'z']),
            'time_factor_aai': xr.DataArray(np.array([[[0.4], [0.5]], [[0.6], [0.7]]]), dims=['x', 'y', 'z']),
            'irrigation_efficiency_sw': xr.DataArray(np.array([[0.7], [0.8]]), dims=['y', 'z']),
            'unit': 'm3/month'
            }    

        # Mock configuration object
        self.mock_config = MagicMock()
        # Setting all required configuration parameters
        self.mock_config.cell_specific_output = {'flag': False,
                                                 "coords": {
                                                     "lat": 30.75,
                                                     "lon": 30.75,
                                                     "year": 1901,
                                                     "month": 5}}
        self.mock_config.irrigation_input_based_on_aei = False
        self.mock_config.correct_irrigation_t_aai_mode = False
        self.mock_config.deficit_irrigation_factor = 0.7
        self.mock_config.deficit_irrigation_mode = True
        self.mock_config.irrigation_efficiency_gw_mode = 'adjust'
        self.mock_config.irrigation_efficiency_gw_threshold = 0.7

    def tearDown(self):
        """Stop all patches after each test."""
        patch.stopall()

    @patch('builtins.print')
    def test_simulation_initialization(self, mock_print):
        """Test that IrrigationSimulator initializes and runs correctly."""
        # Instantiate the IrrigationSimulator
        simulator = IrrigationSimulator(self.irr_data, self.mock_config)

        # Assertions to check if attributes are correctly initialized
        self.assertIsInstance(simulator.consumptive_use_tot, np.ndarray)
        self.assertEqual(simulator.unit, 'm3/month')
        self.assertEqual(simulator.csp_flag, False)
        self.assertEqual(simulator.deficit_irrigation_factor, 0.7)
        self.assertEqual(simulator.irrigation_input_based_on_aei, False)
        self.assertEqual(simulator.correct_irrigation_t_aai_mode, False)
        self.assertEqual(simulator.deficit_irrigation_mode, True)
        self.assertTrue(hasattr(simulator, 'fraction_gw_use'))

    # def test_net_abstraction_sum(self):
    #     """Test that sum of net abstractions equals total consumptive use."""
    #     # Instantiate the IrrigationSimulator
    #     simulator_new = IrrigationSimulator(self.irr_data, self.mock_config)

    #     # Sum of net abstraction groundwater and surface water
    #     net_abstraction_tot = \
    #         simulator_new.net_abstraction_gw + simulator_new.net_abstraction_sw
    #     print(simulator_new.net_abstraction_gw)
    #     # Verify that the sum of net abstractions equals total consumptive use
    #     np.testing.assert_allclose(
    #         net_abstraction_tot, simulator_new.consumptive_use_tot, rtol=1e-3,
    #         err_msg=("The sum of net abstractions does not match total "
    #                  "consumptive use.\n"
    #                  f"{net_abstraction_tot}\n"
    #                  f"cu_gw{simulator_new.consumptive_use_gw.shape}\n"
    #                  f"cu_sw{simulator_new.consumptive_use_sw}\n"
    #                  f"wu_gw{simulator_new.abstraction_gw.shape}\n"
    #                  f"wu_sw{simulator_new.abstraction_sw.shape}\n"
    #                  f"effsw{simulator_new.irrigation_efficiency_sw}\n"
    #                  f"effgw{simulator_new.irrigation_efficiency_gw}\n"
    #                  f"rfgw{simulator_new.return_flow_gw.shape}\n"
    #                  f"rfsw{simulator_new.return_flow_sw.shape}\n"
    #                  f"fraction{simulator_new.fraction_gw_use.shape}\n"
    #                  f"mask{simulator_new.deficit_irrigation_location.shape}\n"
    #                  ))
        

if __name__ == '__main__':
    unittest.main()
