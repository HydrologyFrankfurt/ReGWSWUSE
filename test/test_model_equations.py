# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""test model.model_equations.py"""


import unittest
import numpy as np
from model.model_equations import \
    (calc_gwsw_water_use, calc_return_flow_totgwsw, calc_net_abstraction_gwsw)


class TestModelEquations(unittest.TestCase):
    """Unit test class for the model equation functions."""

    def setUp(self):
        """
        Set up the mock data used in all test cases.
        """
        # Create sample data for testing
        self.fraction = \
            np.array([[[0.4], [0.6]]])

        self.consumptive_use_tot = \
            np.array([[[1.0], [np.nan]], [[2.0], [3.0]]])
        self.consumptive_use_gw = \
            np.array([[[0.4], [np.nan]], [[0.8], [1.8]]])
    
        self.consumptive_use_sw = \
            np.array([[[0.6], [np.nan]], [[1.2], [1.2]]])

        self.abstraction_tot = \
            np.array([[[2.0], [np.nan]], [[4.0], [6.0]]])
    
        self.abstraction_gw = \
            np.array([[[0.8], [np.nan]], [[1.6], [3.6]]])

        self.abstraction_sw = \
            np.array([[[1.2], [np.nan]], [[2.4], [2.4]]])

        self.return_flow_tot = \
            np.array([[[1.0], [np.nan]], [[2.0], [3.0]]])

        self.return_flow_gw = \
            np.array([[[0.4], [np.nan]], [[0.8], [1.8]]])

        self.return_flow_sw = \
            np.array([[[0.6], [np.nan]], [[1.2], [1.2]]])

        self.net_abstraction_gw = \
            np.array([[[0.4], [np.nan]], [[0.8], [1.8]]])

        self.net_abstraction_sw = \
            np.array([[[0.6], [np.nan]], [[1.2], [1.2]]])


        self.float_factor = 0.7
        self.mask_1 = \
            np.array([[[1.0], [0.0]]])
        self.mask_2 = \
            np.array([[[1.0], [1.0]]])
        self.deficit_irrigation_location = \
            np.array([[[self.float_factor], [1.0]]])

        self.consumptive_use_deficit = \
            np.array([[[0.7], [np.nan]], [[1.4], [3.0]]])
        
        self.efficiency_sw = np.array([[[0.5], [0.8]]])

        self.enforce_efficiency_gw = np.array([[[0.7], [0.7]]])
        
        self.adjust_efficiency_gw = np.array([[[0.7], [0.8]]])



    def test_calc_gwsw_water_use(self):
        """Test the `calc_gwsw_water_use` function."""
        consumptive_use_gw, consumptive_use_sw = calc_gwsw_water_use(
            self.consumptive_use_tot, self.fraction
            )
        self.assertTrue(np.allclose(consumptive_use_gw,
                                    self.consumptive_use_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))
        self.assertTrue(np.allclose(consumptive_use_sw,
                                    self.consumptive_use_sw,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_calc_return_flow_totgwsw(self):
        """Test the `calc_return_flow_totgwsw` function."""
        return_flow_tot, return_flow_gw, return_flow_sw = \
            calc_return_flow_totgwsw(self.abstraction_tot,
                                     self.consumptive_use_tot,
                                     self.fraction)
        self.assertTrue(np.allclose(return_flow_tot,
                                    self.return_flow_tot,
                                    equal_nan=True, atol=0, rtol=0))
        self.assertTrue(np.allclose(return_flow_gw,
                                    self.return_flow_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))
        self.assertTrue(np.allclose(return_flow_sw,
                                    self.return_flow_sw,
                                    equal_nan=True, atol=0, rtol=1e-9),
                        msg=f"{return_flow_sw}")

    def test_calc_net_abstraction_gwsw(self):
        net_abstraction_gw, net_abstraction_sw = \
            calc_net_abstraction_gwsw(self.abstraction_gw,
                                      self.return_flow_gw,
                                      self.abstraction_sw,
                                      self.return_flow_sw)
        self.assertTrue(np.allclose(net_abstraction_gw,
                                    self.net_abstraction_gw,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{net_abstraction_gw}")
        self.assertTrue(np.allclose(net_abstraction_sw,
                                    self.net_abstraction_sw,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{net_abstraction_sw}")

    def test_dom_man_tp_liv_net_abstraction(self):
        """Test `net_abstraction_sum`."""
        consumptive_use_gw, consumptive_use_sw = \
            calc_gwsw_water_use(self.consumptive_use_tot, self.fraction)

        abstraction_gw, abstraction_sw = \
            calc_gwsw_water_use(self.abstraction_tot, self.fraction)

        return_flow_tot, return_flow_gw, return_flow_sw = \
            calc_return_flow_totgwsw(self.abstraction_tot,
                                     self.consumptive_use_tot,
                                     self.fraction)

        net_abstraction_gw, net_abstraction_sw = \
            calc_net_abstraction_gwsw(abstraction_gw, return_flow_gw,
                                      abstraction_sw, return_flow_sw)

        net_abstraction_tot = net_abstraction_gw + net_abstraction_sw

        self.assertTrue(np.allclose(
            net_abstraction_tot, self.consumptive_use_tot,
            equal_nan=True, atol=0, rtol=0))
    


if __name__ == '__main__':
    unittest.main()
