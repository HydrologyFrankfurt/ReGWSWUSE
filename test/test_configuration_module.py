# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Test controller.configuration_module"""

import unittest
from unittest.mock import patch, mock_open
import logging
from controller.configuration_module import ConfigHandler, logger


class TestConfigHandler(unittest.TestCase):
    """Unit test class for testing the ConfigHandler class."""

    def setUp(self):
        """Set up the file paths for the test configuration files."""
        # Path to valid configuration
        self.valid_config_filename = "./test/test_data/valid_config.json"
        # Validation failed data
        self.invalid_config_filename = "./test/test_data/invalid_config.json"
        # Non-existent configuration file
        self.non_existent_filename = "./test/test_data/non_existent_file.json"
        # json_decode_error_filename
        self.decode_error_filename = \
            "./test/test_data/decode_error_config.json"

    def tearDown(self):
        """Reset the singleton instance after each test."""
        ConfigHandler._instance = None  # Reset the singleton instance

    # =========================================================================
    @patch('builtins.print')  # Suppress print statements during tests
    # Mock logger to suppress logging output during tests
    @patch('gwswuse_logger.get_logger')
    def test_singleton_instance(self, mock_logger, mock_print):
        """Test that ConfigHandler behaves as a `singleton`."""
        # Create the first instance of ConfigHandler with a valid config file
        config1 = ConfigHandler(self.valid_config_filename)

        # Create a second instance of ConfigHandler with the same config file
        config2 = ConfigHandler(self.valid_config_filename)

        # Ensure that both config1 and config2 point to the same instance
        self.assertIs(config1, config2, "ConfigHandler is not a singleton")

    # =========================================================================
    @patch('builtins.print')
    @patch('gwswuse_logger.get_logger')
    def test_load_valid_config(self, mock_logger, mock_print):
        """Test that the config loads and initializes correctly."""
        config = ConfigHandler(self.valid_config_filename)
        # Check if config loaded expected values
        self.assertEqual(config.input_data_path, "./input_data/")
        self.assertEqual(config.output_dir, "./output_data/")
        self.assertEqual(config.start_year, 1901)
        self.assertEqual(config.end_year, 1905)

    # =========================================================================
    # Simulate missing file
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('gwswuse_logger.get_logger')
    def test_config_file_not_found(self, mock_logger, mock_open):
        """Test that the system exits when `config file is not found`."""
        with self.assertRaises(SystemExit):
            ConfigHandler(self.non_existent_filename)

    # =========================================================================
    # Mock logger to suppress logging output during tests
    @patch('controller.configuration_module.logger')
    def test_invalid_config_data(self, mock_logger):
        """Test that invalid config logs an error and triggers sys.exit."""
        # Expect SystemExit since sys.exit() is called on validation failure
        with self.assertRaises(SystemExit) as cm:
            ConfigHandler(self.invalid_config_filename)  # Load invalid config

        # Verify that the exit code is 1
        self.assertEqual(cm.exception.code, 1)

        # Ensure the logger's `error` method was called to log the failure
        mock_logger.error.assert_called()

        # Check for the specific error message in the logged output
        logged_message = mock_logger.error.call_args[0][0]
        self.assertIn(
            'Configuration validation failed. Please check the errors above.',
            logged_message
        )
    # =========================================================================

    @patch('controller.configuration_module.logger')  # Mock logger
    @patch('builtins.open', new_callable=mock_open, read_data='{invalid_json}')
    def test_json_decode_error(self, mock_open, mock_logger):
        """Test that ConfigHandler handles JSONDecodeError for invalid JSON."""

        # Expect a SystemExit due to sys.exit() on JSONDecodeError
        with self.assertRaises(SystemExit):
            ConfigHandler('path/to/invalid/config.json')  # Trigger error

        # Ensure that the logger's `error` method was called for JSON error
        mock_logger.error.assert_called()

        # Check the specific error message content in the logged output
        logged_message = mock_logger.error.call_args[0][0]
        self.assertIn("Error decoding JSON configuration file", logged_message)

    # =========================================================================
    @patch('builtins.print')
    @patch('gwswuse_logger.get_logger')
    def test_get_config_values(self, mock_logger, mock_print):
        """Test the `get-function` to retrieve nested configuration values."""
        config = ConfigHandler(self.valid_config_filename)
        self.assertEqual(
            config.get("FilePath.inputDir.input_data"), "./input_data/")
        self.assertEqual(
            config.get("RuntimeOptions.SimulationPeriod.start"), 1901)
        self.assertEqual(
            config.get(
                "RuntimeOptions.SimulationOption.deficit_irrigation_mode"),
            True
            )

    # # =======================================================================
    # @patch('builtins.print')
    # @patch('gwswuse_logger.get_logger')
    # def test_set_config_values(self, mock_logger, mock_print):
    #     """Test the `set-function` to update configuration values."""
    #     config = ConfigHandler(self.valid_config_filename)
    #     config.set("RuntimeOptions.SimulationPeriod.end", 2021)
    #     self.assertEqual(
    #         config.get("RuntimeOptions.SimulationPeriod.end"), 2021)

    # =========================================================================
    @patch('builtins.print')
    @patch('gwswuse_logger.get_logger')  # Mock logger to suppress log output
    def test_reload_config(self, mock_logger, mock_print):
        """Test `reload` function in ConfigHandler."""
        config = ConfigHandler(self.valid_config_filename)
        config.end_year = 1910
        config.reload()  # Reload the configuration
        # Verify that the configuration values remain consistent after reload
        self.assertEqual(config.start_year, 1901)
        self.assertEqual(config.end_year, 1905)


if __name__ == '__main__':
    unittest.main()
