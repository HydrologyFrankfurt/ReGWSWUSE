import unittest
import xarray as xr
import numpy as np
import pandas as pd
from controller.input_data_check_preprocessing import (
    check_and_preprocess_input_data, initialize_logs)


class Config:
    def __init__(self):
        self.start_year = 2000
        self.end_year = 2005
        self.time_extend_mode = False
        self.deficit_irrigation_mode = True
        self.irrigation_input_based_on_aei = True
        self.correct_irrigation_t_aai_mode = True


class TestValidationPreprocessing(unittest.TestCase):
    def setUp(self):
        # Set up the sample dataset and conventions for testing
        times = pd.date_range('2000-01-01', '2005-12-31', freq='MS')
        self.latitudes = np.arange(-90, 90.5, 0.5)
        self.longitudes = np.arange(-180, 180.5, 0.5)
        self.other_longitudes = np.arange(-180, 180.5, 10)

        # Create a sample dataset with random values for testing
        self.sample_dataset = xr.Dataset({
            'ptotuse': (('time', 'lat', 'lon'),
                        np.random.rand(len(times), len(self.latitudes),
                                       len(self.longitudes))),
        }, coords={
            'time': times,
            'lat': self.latitudes,
            'lon': self.longitudes,
        })

        self.sample_dataset['ptotuse'].attrs['units'] = 'm3/month'

        # Create an invalid dataset with incorrect units
        self.other_lon_dataset = xr.Dataset({
            'pirrfractgwuse': (('lat', 'lon'),
                               np.random.rand(len(self.latitudes),
                                              len(self.other_longitudes))),
        }, coords={
            'lat': self.latitudes,
            'lon': self.other_longitudes,
        })
        # Create a sample dataset with random values for testing
        self.fraction_aai_aei = xr.Dataset({
            'fraction_aai_aei': (('time', 'lat', 'lon'),
                                 np.random.rand(
                                     len(times), len(self.latitudes),
                                     len(self.longitudes))),
        }, coords={
            'time': times,
            'lat': self.latitudes,
            'lon': self.longitudes,
        })
        # Create a sample dataset with random values for testing
        self.time_factor_aai = xr.Dataset({
            'time_factor_aai': (('time', 'lat', 'lon'),
                                np.random.rand(
                                    len(times), len(self.latitudes),
                                    len(self.longitudes))),
        }, coords={
            'time': times,
            'lat': self.latitudes,
            'lon': self.longitudes,
        })

        # Define conventions and sector requirements for testing
        self.conventions = {
            'reference_names': ['ptotuse', 'pirrfractgwuse'],
            'time_variant_vars': ['consumptive_use_tot'],
            'sector_requirements': {
                'irrigation': {
                    'unit_vars': ['consumptive_use_tot'],
                    'expected_units': ['m3/month'],
                    'time_freq': 'monthly'
                }
            }
        }

        # Set up other parameters for testing
        self.datasets = {'irrigation': {
            'consumptive_use_tot': self.sample_dataset,
            'fraction_aai_aei': self.fraction_aai_aei,
            'time_factor_aai': self.time_factor_aai}
            }
        self.other_lon_datasets = {'irrigation': {
            'consumptive_use_tot': self.sample_dataset,
            'fraction_gw_use': self.other_lon_dataset,
            'fraction_aai_aei': self.fraction_aai_aei,
            'time_factor_aai': self.time_factor_aai}
            }
        self.config = Config()
        self.start_year = 2000
        self.end_year = 2005

    def test_check_and_preprocess_input_data(self):
        # Test the check and preprocess function with the sample dataset
        preprocessed_datasets, check_logs = \
            check_and_preprocess_input_data(
                self.datasets, self.conventions, self.config)

        # Validate the results to ensure there are no errors in the dataset
        self.assertTrue(
            check_logs['too_many_vars'] == [])
        self.assertTrue(
            check_logs['unit_mismatch'] == [])
        self.assertTrue(
            check_logs['missing_unit'] == [],
            f"Validation failed for missing units: "
            f"{check_logs['missing_unit']}")
        self.assertTrue(
            check_logs['missing_time_coords'] == [],
            (f"Validation failed for missing time coordinates: "
             f"{check_logs['missing_time_coords']}"))
        self.assertTrue(
            check_logs['time_resolution_mismatch'] == [],
            f"Validation failed for incorrect time resolution: "
            f"{check_logs['time_resolution_mismatch']}")

        self.assertTrue(check_logs['lat_lon_consistency'])

        preprocessed_datasets, check_logs = check_and_preprocess_input_data(
            self.other_lon_datasets, self.conventions, self.config
            )
        # Validate the results to ensure there are no errors in the dataset
        self.assertTrue(check_logs['too_many_vars'] == [])
        self.assertTrue(
            check_logs['unit_mismatch'] == [],
            f"Validation failed for incorrect units: "
            f"{check_logs['unit_mismatch']}")
        self.assertTrue(
            check_logs['missing_unit'] == [],
            f"Validation failed for missing units: "
            f"{check_logs['missing_unit']}")
        self.assertTrue(
            check_logs['missing_time_coords'] == [],
            f"Validation failed for missing time coordinates: "
            f"{check_logs['missing_time_coords']}")
        self.assertTrue(
            check_logs['time_resolution_mismatch'] == [],
            f"Validation failed for incorrect time resolution: "
            f"{check_logs['time_resolution_mismatch']}")
        self.assertFalse(
            check_logs['lat_lon_consistency'])

    def test_extend_xr_data(self):
        extend_config = self.config
        extend_config.end_year += 2
        extend_config.time_extend_mode = True
        # Test the extension of dataset time coverage
        preprocessed_datasets, check_logs = check_and_preprocess_input_data(
            self.datasets, self.conventions, extend_config
        )

        # Verify that the time coordinate of the dataset has been extended
        extended_time = \
            pd.to_datetime(
                preprocessed_datasets['irrigation']['consumptive_use_tot'
                                                    ].coords['time'].values)
        self.assertEqual(extended_time[0].year, extend_config.start_year)
        self.assertEqual(extended_time[-1].year, extend_config.end_year)

        # Check that the validation results reflect the extension
        self.assertIn('irrigation/consumptive_use_tot',
                      check_logs['extended_time_period'])

    def test_trim_xr_data(self):
        # Test the trimming functionality by providing an extended dataset
        extended_times = pd.date_range('1998-01-01', '2007-12-31', freq='YS')
        extended_dataset = xr.Dataset({
            'consumptive_use_tot': (
                ('time', 'lat', 'lon'),
                np.random.rand(len(extended_times),
                               len(self.latitudes),
                               len(self.longitudes))),
        }, coords={
            'time': extended_times,
            'lat': self.latitudes,
            'lon': self.longitudes,
        })
        datasets = {'irrigation': {
            'consumptive_use_tot': extended_dataset,
            'fraction_aai_aei': self.fraction_aai_aei,
            'time_factor_aai': self.time_factor_aai}
            }

        # Preprocess the dataset to trim it to the desired time range
        preprocessed_datasets, check_logs = check_and_preprocess_input_data(
            datasets, self.conventions, self.config)

        # Verify that the dataset has been trimmed correctly
        trimmed_time = \
            pd.to_datetime(
                preprocessed_datasets['irrigation']['consumptive_use_tot'
                                                    ].coords['time'].values)
        self.assertEqual(trimmed_time[0].year, self.config.start_year)
        self.assertEqual(trimmed_time[-1].year, self.config.end_year)


if __name__ == '__main__':
    unittest.main()
