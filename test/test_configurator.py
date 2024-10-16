# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 10:21:06 2024

@author: lniss
"""

import json
import logging
import os
import sys

import watergap_logger as log
from misc import cli_args as cli

modname = os.path.basename(__file__)
modname = modname.split('.')[0]

args = cli.parse_cli()

def config_handler(filename):
    """
    Handle all configuration file.

    Parameters
    ----------
    filename : str
        configuration filename

    Returns
    -------
    config_content : dict
        return content of the configuation file.

    """
    
    try:
        with open(filename) as config:
            config_content = json.load(config)
    except FileNotFoundError:
        print('Configuration not found')
        # log.config_logger(logging.ERROR, modname,
        #                   'Configuration file not found',
        #                   args.debug)
        sys.exit()  # don't run code if cofiguration file does not exist
    except json.JSONDecodeError as json_error:
        # Log error for invalid JSON format
        log.config_logger(logging.ERROR, modname,
                          f'Error decoding JSON configuration file: '
                          f'{filename} - {str(json_error)}',
                          args.debug)
        return None
    else:
        print('\n' + 'Configuration loaded successfully' + '\n')

    return config_content

import unittest
from unittest.mock import patch

class TestConfigHandler(unittest.TestCase):
    
    def setUp(self):
            """
            Set up the file paths for the tests.
            """
            self.valid_config_filename = "./test_data/valid_config.json"
            self.invalid_config_filename = "./test_data/invalid_config.json"  # In line 9 in file is missing a bracket
            self.non_existent_filename = "./test_data/non_existent_file.json"  # Non-existent file

    @patch('builtins.print')  # Mock the print function to suppress output during tests
    def test_config_handler_valid_file(self, mock_print):
        """
        Test that the config handler loads a valid JSON configuration file and returns a dictionary.
        """
        config = config_handler(self.valid_config_filename)
        # Check if the file is successfully loaded and returns a dictionary
        self.assertIsInstance(config, dict)

    @patch('builtins.print')  # Mock the print function to suppress output during tests
    def test_config_handler_file_not_found(self, mock_print):
        """
        Test that the config handler raises SystemExit when the file is not found.
        """
        # Use a non-existent file to trigger the FileNotFoundError
        with self.assertRaises(SystemExit):  # Expect SystemExit when the file is not found
            config_handler(self.non_existent_filename)

    @patch('builtins.print')  # Mock the print function to suppress output during tests
    def test_config_handler_invalid_json(self, mock_print):
        """
        Test that the config handler returns None when the configuration file contains invalid JSON.
        """
        config = config_handler(self.invalid_config_filename)
        # Should return None if the JSON is invalid
        self.assertIsNone(config)

if __name__ == '__main__':
    unittest.main()