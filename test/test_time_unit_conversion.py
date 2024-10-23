# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""test model.time_unit_conversion.py"""


import unittest
import numpy as np
from model.time_unit_conversion import \
    convert_yearly_to_monthly, convert_monthly_to_yearly, expand_array_size


class TestUnitConversion(unittest.TestCase):
    """Unit test class for the time unit conversion functions."""

    def setUp(self):
        """
        Set up the mock data used in all test cases.

        self.annual_data:
            - Shape: (2, 2, 1) representing 2 years of data, 2 latitude points,
              and 1 longitude point.
            - Contains both valid numeric values and NaN values.

        self.monthly_data:
            - Shape: (24, 2, 1) representing 24 months (2 years * 12 months),
              2 latitude points, and 1 longitude point.
            - Contains valid monthly data and NaN values in the same structure
              as the annual data.

        self.expand_data:
            - Shape: (24, 2, 1) after expanding the yearly data into a monthly
              format.
        """
        # years : 2
        # lat-size:2
        # lon-size: 1
        # Create sample data for testing
        self.annual_data = np.array([[[365.0], [np.nan]], [[np.nan], [730.0]]])

        self.monthly_data = np.array(
            [[[31.0], [np.nan]], [[28.0], [np.nan]], [[31.0], [np.nan]],
             [[30.0], [np.nan]], [[31.0], [np.nan]], [[30.0], [np.nan]],
             [[31.0], [np.nan]], [[31.0], [np.nan]], [[30.0], [np.nan]],
             [[31.0], [np.nan]], [[30.0], [np.nan]], [[31.0], [np.nan]],
             [[np.nan], [62.0]], [[np.nan], [56.0]], [[np.nan], [62.0]],
             [[np.nan], [60.0]], [[np.nan], [62.0]], [[np.nan], [60.0]],
             [[np.nan], [62.0]], [[np.nan], [62.0]], [[np.nan], [60.0]],
             [[np.nan], [62.0]], [[np.nan], [60.0]], [[np.nan], [62.0]]])

        self.expand_data = np.array(
            [[[365.0], [np.nan]], [[365.0], [np.nan]], [[365.0], [np.nan]],
             [[365.0], [np.nan]], [[365.0], [np.nan]], [[365.0], [np.nan]],
             [[365.0], [np.nan]], [[365.0], [np.nan]], [[365.0], [np.nan]],
             [[365.0], [np.nan]], [[365.0], [np.nan]], [[365.0], [np.nan]],
             [[np.nan], [730.0]], [[np.nan], [730.0]], [[np.nan], [730.0]],
             [[np.nan], [730.0]], [[np.nan], [730.0]], [[np.nan], [730.0]],
             [[np.nan], [730.0]], [[np.nan], [730.0]], [[np.nan], [730.0]],
             [[np.nan], [730.0]], [[np.nan], [730.0]], [[np.nan], [730.0]]])

    def test_convert_yearly_to_monthly(self):
        """
        Test the `convert_yearly_to_monthly` function.

        Verifies the shape of the output and checks that the converted values
        match the expected monthly data. Uses `np.allclose` to compare arrays,
        allowing for tolerance and NaN equality.
        """
        result = convert_yearly_to_monthly(self.annual_data)
        expected_shape = (24, 2, 1)  # 2 years * 12 months, 2 lat, 1 lon
        self.assertEqual(result.shape, expected_shape)
        self.assertTrue(np.allclose(result, self.monthly_data, equal_nan=True,
                                    atol=0, rtol=0))

    def test_convert_monthly_to_yearly(self):
        """
        Test the `convert_monthly_to_yearly` function.

        Verifies the shape of the output and checks that the conversion from
        monthly back to yearly values is correct. Uses `np.allclose` for
        comparison with tolerance and NaN equality.
        """
        result = convert_monthly_to_yearly(self.monthly_data)
        expected_shape = (2, 2, 1)  # 2 years, 2 lat, 1 lon
        self.assertEqual(result.shape, expected_shape)
        self.assertTrue(np.allclose(result, self.annual_data, equal_nan=True,
                                    atol=0, rtol=0))

    def test_convert(self):
        """Test `convert_monthly_to_yearly(convert_yearly_to_monthly)`."""
        annual_data = convert_monthly_to_yearly(
            convert_yearly_to_monthly(self.annual_data)
            )
        annual_data_expected_shape = (2, 2, 1)
        self.assertEqual(annual_data.shape, annual_data_expected_shape)

        self.assertTrue(np.allclose(annual_data, self.annual_data,
                                    equal_nan=True, atol=0, rtol=0)
                        )

        monthly_data = convert_yearly_to_monthly(
            convert_monthly_to_yearly(self.monthly_data)
            )
        monthly_data_expected_shape = (24, 2, 1)
        self.assertEqual(monthly_data.shape, monthly_data_expected_shape)

        self.assertTrue(np.allclose(monthly_data, self.monthly_data,
                                    equal_nan=True, atol=0, rtol=0)
                        )

    def test_expand_array_size(self):
        """
        Test the `expand_array_size` function.

        Verifies that the expansion of annual data to monthly resolution is
        correct and that the expanded array matches the expected expanded data.
        """

        result = expand_array_size(self.annual_data)
        expected_shape = (24, 2, 1)
        self.assertEqual(result.shape, expected_shape)
        self.assertTrue(np.allclose(result, self.expand_data, equal_nan=True,
                                    atol=0, rtol=0))


if __name__ == '__main__':
    unittest.main()
