import unittest
import xarray as xr
import numpy as np
import pandas as pd
from controller.input_data_check_preprocessing import (
    check_and_preprocess_input_data, initialize_logs,
    generate_validation_results)

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
        self.datasets = [(self.sample_dataset, 'irrigation', 'consumptive_use_tot')]
        self.other_lon_datasets = [
            (self.sample_dataset, 'irrigation', 'consumptive_use_tot'),
            (self.other_lon_dataset, 'irrigation', 'fraction_gw_use')]
        self.start_year = 2000
        self.end_year = 2005
        self.time_extend_mode = False


    def test_check_and_preprocess_input_data(self):
        # Test the check and preprocess function with the sample dataset
        preprocessed_datasets, validation_results = check_and_preprocess_input_data(
            self.datasets, self.conventions, self.start_year, self.end_year, self.time_extend_mode
        )

        # Validate the results to ensure there are no errors in the dataset
        self.assertTrue(validation_results['Input data with multiple variables'] == [])
        self.assertTrue(
            validation_results['Input data with incorrect units'] == [],
            f"Validation failed for incorrect units: "
            f"{validation_results['Input data with incorrect units']}"
            f"{preprocessed_datasets['irrigation']['consumptive_use_tot'].units}")
        self.assertTrue(validation_results['Input data with missing units'] == [], f"Validation failed for missing units: {validation_results['Input data with missing units']}")
        self.assertTrue(validation_results['Input data with missing time coordinates'] == [], f"Validation failed for missing time coordinates: {validation_results['Input data with missing time coordinates']}")
        self.assertTrue(validation_results['Input data with incorrect time resolution'] == [], f"Validation failed for incorrect time resolution: {validation_results['Input data with incorrect time resolution']}")
        self.assertTrue(validation_results['Compatibility of lat and lon coords is given'])

        preprocessed_datasets, validation_results = check_and_preprocess_input_data(
            self.other_lon_datasets, self.conventions, self.start_year, self.end_year, self.time_extend_mode
        )
        # Validate the results to ensure there are no errors in the dataset
        self.assertTrue(validation_results['Input data with multiple variables'] == [])
        self.assertTrue(
            validation_results['Input data with incorrect units'] == [],
            f"Validation failed for incorrect units: "
            f"{validation_results['Input data with incorrect units']}"
            f"{preprocessed_datasets['irrigation']['consumptive_use_tot'].units}")
        self.assertTrue(validation_results['Input data with missing units'] == [], f"Validation failed for missing units: {validation_results['Input data with missing units']}")
        self.assertTrue(validation_results['Input data with missing time coordinates'] == [], f"Validation failed for missing time coordinates: {validation_results['Input data with missing time coordinates']}")
        self.assertTrue(validation_results['Input data with incorrect time resolution'] == [], f"Validation failed for incorrect time resolution: {validation_results['Input data with incorrect time resolution']}")
        self.assertFalse(validation_results['Compatibility of lat and lon coords is given'])

    def test_extend_xr_data(self):
        # Test the extension of dataset time coverage
        preprocessed_datasets, validation_results = check_and_preprocess_input_data(
            self.datasets, self.conventions, self.start_year, self.end_year + 2, True
        )

        # Verify that the time coordinate of the dataset has been extended
        extended_time = pd.to_datetime(preprocessed_datasets['irrigation']['consumptive_use_tot'].coords['time'].values)
        self.assertEqual(extended_time[0].year, self.start_year)
        self.assertEqual(extended_time[-1].year, self.end_year + 2)
        
        # Check that the validation results reflect the extension
        self.assertIn('irrigation/consumptive_use_tot', validation_results['Input data with extended time to cover simulation period'])

    def test_trim_xr_data(self):
        # Test the trimming functionality by providing an extended dataset
        extended_times = pd.date_range('1998-01-01', '2007-12-31', freq='YS')
        extended_dataset = xr.Dataset({
            'consumptive_use_tot': (('time', 'lat', 'lon'),
                            np.random.rand(len(extended_times), len(self.latitudes), len(self.longitudes))),
        }, coords={
            'time': extended_times,
            'lat': self.latitudes,
            'lon': self.longitudes,
        })
        datasets = [(extended_dataset, 'irrigation', 'consumptive_use_tot')]

        # Preprocess the dataset to trim it to the desired time range
        preprocessed_datasets, validation_results = check_and_preprocess_input_data(
            datasets, self.conventions, self.start_year, self.end_year, False
        )

        # Verify that the dataset has been trimmed correctly
        trimmed_time = pd.to_datetime(preprocessed_datasets['irrigation']['consumptive_use_tot'].coords['time'].values)
        self.assertEqual(trimmed_time[0].year, self.start_year)
        self.assertEqual(trimmed_time[-1].year, self.end_year)

if __name__ == '__main__':
    unittest.main()
