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
    (calc_gwsw_water_use, calc_return_flow_totgwsw, calc_net_abstraction_gwsw,
     set_irr_deficit_locations, calc_irr_deficit_consumptive_use_tot,
     calc_irr_consumptive_use_aai, correct_irr_consumptive_use_by_t_aai,
     set_irr_efficiency_gw, calc_irr_abstraction_totgwsw,
     calc_cross_sector_totals, calc_fractions)


class TestModelEquations(unittest.TestCase):
    """Unit test class for the model equation functions."""

    def setUp(self):
        """
        Set up the mock data used in all test cases.
        """
        # Create sample data for testing
        self.fraction = \
            np.array([[[0.4], [0.6]]])
        self.time_fraction = \
            np.array([[[0.4], [0.6]], [[0.4], [0.6]]])
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
        self.irr_abstraction_sw = \
            np.array([[[0.6/0.5], [np.nan]], [[1.2/0.5], [1.2/0.8]]])

        self.enforce_efficiency_gw = np.array([[[0.7], [0.7]]])        
        self.irr_abstraction_gw_enforce = \
            np.array([[[0.4/0.7], [np.nan]], [[0.8/0.7], [1.8/0.7]]])
        self.irr_abstraction_tot_enforce = \
            np.array([[[0.4/0.7 + 0.6/0.5], [np.nan]],
                      [[0.8/0.7 + 1.2/0.5], [1.8/0.7 + 1.2/0.8]]])
        
        self.adjust_efficiency_gw = np.array([[[0.7], [0.8]]])
        self.irr_abstraction_gw_adjust = \
            np.array([[[0.4/0.7], [np.nan]], [[0.8/0.7], [1.8/0.8]]])


    def test_calc_gwsw_water_use(self):
        """Test the `calc_gwsw_water_use` function."""
        exp_consumptive_use_gw = self.consumptive_use_gw
        exp_consumptive_use_sw = self.consumptive_use_sw

        consumptive_use_gw, consumptive_use_sw = calc_gwsw_water_use(
            self.consumptive_use_tot, self.fraction
            )

        self.assertTrue(np.allclose(consumptive_use_gw,
                                    exp_consumptive_use_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))
        self.assertTrue(np.allclose(consumptive_use_sw,
                                    exp_consumptive_use_sw,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_calc_return_flow_totgwsw(self):
        """Test the `calc_return_flow_totgwsw` function."""
        exp_return_flow_tot = self.return_flow_tot
        exp_return_flow_gw = self.return_flow_gw
        exp_return_flow_sw = self.return_flow_sw
        
        
        return_flow_tot, return_flow_gw, return_flow_sw = \
            calc_return_flow_totgwsw(self.abstraction_tot,
                                     self.consumptive_use_tot,
                                     self.fraction)

        self.assertTrue(np.allclose(return_flow_tot,
                                    exp_return_flow_tot,
                                    equal_nan=True, atol=0, rtol=0))
        self.assertTrue(np.allclose(return_flow_gw,
                                    exp_return_flow_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))
        self.assertTrue(np.allclose(return_flow_sw,
                                    exp_return_flow_sw,
                                    equal_nan=True, atol=0, rtol=1e-9),
                        msg=f"{return_flow_sw}")

    def test_calc_net_abstraction_gwsw(self):
        """Test the `calc_net_abstraction_gwsw` function."""
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

    def test_set_irr_deficit_locations(self):
        """Test the `calc_net_abstraction_gwsw` function."""
        exp_deficit_irrigation_location =  self.deficit_irrigation_location

        deficit_irrigation_location = set_irr_deficit_locations(
            self.mask_1, self.mask_2, self.float_factor)

        self.assertTrue(np.allclose(deficit_irrigation_location,
                                    exp_deficit_irrigation_location,
                                    equal_nan=True, atol=0, rtol=1e-9))
        

    def test_calc_irr_deficit_consumptive_use_tot(self):
        """Test the `calc_irr_deficit_consumptive_use_tot` function."""
        exp_consumptive_use_deficit = self.consumptive_use_gw

        consumptive_use_deficit = calc_irr_deficit_consumptive_use_tot(
            self.consumptive_use_tot, self.fraction)

        self.assertTrue(np.allclose(consumptive_use_deficit,
                                    exp_consumptive_use_deficit,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_calc_irr_consumptive_use_aai(self):
        """Test the `calc_irr_consumptive_use_aai` function."""
        exp_consumptive_use_aai = self.consumptive_use_gw

        consumptive_use_aai = calc_irr_consumptive_use_aai(
            self.consumptive_use_tot, self.fraction)

        self.assertTrue(np.allclose(consumptive_use_aai,
                                    exp_consumptive_use_aai,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_correct_irr_consumptive_use_by_t_aai(self):
        """Test the `correct_irr_consumptive_use_by_t_aai` function."""
        exp_consumptive_use_tot = self.consumptive_use_gw

        consumptive_use_tot = correct_irr_consumptive_use_by_t_aai(
            self.consumptive_use_tot, self.time_fraction)

        self.assertTrue(np.allclose(consumptive_use_tot,
                                    exp_consumptive_use_tot,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_set_irr_efficiency_gw(self):
        """Test the `set_irr_efficiency_gw` function."""
        efficiency_sw = self.efficiency_sw
        threshold = self.float_factor

        mode = "enforce"

        exp_enforce_efficiency_gw = self.enforce_efficiency_gw
        
        enforce_efficiency_gw = set_irr_efficiency_gw(
            efficiency_sw, threshold, mode)

        self.assertTrue(np.allclose(enforce_efficiency_gw,
                                    exp_enforce_efficiency_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))

        mode = "adjust"

        exp_adjust_efficiency_gw = self.adjust_efficiency_gw
        
        adjust_efficiency_gw = set_irr_efficiency_gw(
            efficiency_sw, threshold, mode)

        self.assertTrue(np.allclose(adjust_efficiency_gw,
                                    exp_adjust_efficiency_gw,
                                    equal_nan=True, atol=0, rtol=1e-9))

    def test_calc_irr_abstraction_totgwsw(self):
        """Test `calc_irr_abstraction_totgwsw`function."""
        efficiency_sw = self.efficiency_sw
        efficiency_gw = self.enforce_efficiency_gw
        
        
        exp_irr_abstraction_gw_enforce = self.irr_abstraction_gw_enforce
        exp_irr_abstraction_sw = self.irr_abstraction_sw
        exp_irr_abstraction_tot_enforce = self.irr_abstraction_tot_enforce
        irr_abstraction_gw, irr_abstraction_sw, irr_abstraction_tot = \
            calc_irr_abstraction_totgwsw(self.consumptive_use_gw, efficiency_gw,
                                         self.consumptive_use_sw, efficiency_sw)

        self.assertTrue(np.allclose(irr_abstraction_gw,
                                    exp_irr_abstraction_gw_enforce,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{irr_abstraction_gw}")
        self.assertTrue(np.allclose(irr_abstraction_sw,
                                    exp_irr_abstraction_sw,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{irr_abstraction_sw}")
        self.assertTrue(np.allclose(irr_abstraction_tot,
                                    exp_irr_abstraction_tot_enforce,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{irr_abstraction_tot}")

        efficiency_gw = self.adjust_efficiency_gw
        exp_irr_abstraction_gw_adjust = self.irr_abstraction_gw_adjust
        irr_abstraction_gw, _, _ = calc_irr_abstraction_totgwsw(
            self.consumptive_use_gw, efficiency_gw,
            self.consumptive_use_sw, efficiency_sw
            )
        self.assertTrue(np.allclose(irr_abstraction_gw,
                                    exp_irr_abstraction_gw_adjust,
                                    equal_nan=True, atol=0, rtol=0),
                        f"{irr_abstraction_gw}")
        


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
