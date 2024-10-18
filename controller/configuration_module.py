# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

"""Configuartion parser function."""

import json
import logging
import os
import sys
import watergap_logger as log
from misc import cli_args as cli

# ===============================================================
# Get module name and remove the .py extension
# Module name is passed to logger
# # ===============================================================
modname = os.path.basename(__file__)
modname = modname.split('.')[0]

# ++++++++++++++++++++++++++++++++++++++++++++++++
# Parsing  Argguments for CLI from cli_args module
# +++++++++++++++++++++++++++++++++++++++++++++++++
args = cli.parse_cli()


class ConfigError(Exception):
    """User-defined exception for configuration errors."""


class ConfigHandler:
    """Class to load, validate and initialize configuration file."""

    # Make sure that the instance can only be instantiated once
    _instance = None

    def __new__(cls, config_filename='gwswuse_config.json', debug=False):
        """Singleton implementation to ensure that only one instance exists."""
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
            cls._instance.debug = debug
            cls._instance._load_config(config_filename)
            cls._instance._initialize_config()
            cls._instance._validate_config()
        return cls._instance

    def _load_config(self, config_filename):
        """Load the configuration from a file and initialize & validate it.

        Parameters
        ----------
        filename : str
            configuration filename

        Returns
        -------
        config_content : dict
            return content of the configuation file.

        """
        self.config_filename = config_filename
        self.config_data = {}

        try:
            with open(self.config_filename, encoding="utf-8") as filename:
                self.config_data = json.load(filename)
        except FileNotFoundError:
            print('Configuration not found')
            log.config_logger(logging.ERROR, modname,
                              'Configuration file not found',
                              self.debug)
            sys.exit()  # don't run code if cofiguration file does not exist
        except json.JSONDecodeError as json_error:
            # Log error for invalid JSON format
            log.config_logger(logging.ERROR, modname,
                              f'Error decoding JSON configuration file: '
                              f'{filename} - {str(json_error)}',
                              self.debug)
        else:
            print('\n' + 'Configuration loaded successfully' + '\n')

    def _initialize_config(self):
        """Initialize configuration parameters in attributes of the class."""
        # =====================================================================
        # Initialize FilePath
        # ===================
        input_dir = self.get("FilePath.inputDir")

        self.input_data_path = input_dir.get("input_data")
        self.convention_path = input_dir.get("gwswuse_convention")

        self.output_dir = self.get("FilePath.outputDir")

        # =====================================================================
        # =========================
        # SimulationPeriod
        simulation_period = self.get("RuntimeOptions.SimulationPeriod")

        self.start_year = simulation_period.get("start")
        self.end_year = simulation_period.get("end")

        # SimulationOptions
        simulation_options = self.get("RuntimeOptions.SimulationOption")

        self.deficit_irrigation_mode = \
            simulation_options.get("deficit_irrigation_mode")
        self.irrigation_efficiency_gw_mode = \
            simulation_options.get("irrigation_efficiency_gw_mode")
        self.irrigation_input_based_on_aei = \
            simulation_options.get("irrigation_input_based_on_aei")
        self.correct_irrigation_t_aai_mode = \
            simulation_options.get("correct_irr_simulation_by_t_aai")
        self.time_extend_mode = \
            simulation_options.get("time_extend_mode")  # bool

        # ParameterSetting
        params_setting = self.get("RuntimeOptions.ParameterSetting")

        self.deficit_irrigation_factor = \
            params_setting.get("deficit_irrigation_factor")
        self.efficiency_gw_threshold = \
            params_setting.get("efficiency_gw_threshold")

        # CellSpecificOutput
        self.cell_specific_output = \
            self.get("RuntimeOptions.CellSpecificOutput")
        # =====================================================================
        # Initialize OutputSelection
        # ==========================
        self.output_selection = self.get("OutputSelection")

        print('\n' + 'Configuration initialized successfully' + '\n')

    def _validate_config(self):
        """Validate configuration directly after loading and initializing."""
        self._validate_paths()
        self._validate_simulation_period()
        self._validate_simulation_options()
        self._validate_params_setting()
        self._validate_cell_specific_output()
        self._validate_output_selection()

        print('\n' + 'Configuration validated successfully' + '\n')

    def _validate_paths(self):
        """Validate file paths."""
        # Validate FilePath
        if (not isinstance(self.input_data_path, str) or
            not self.input_data_path.endswith("/")):
            raise ConfigError("Invalid 'input_data' path: must be a string "
                              "ending with '/'")
        if (not isinstance(self.convention_path, str) or
            not self.convention_path.endswith(".json")):
            raise ConfigError("Invalid 'convention' path: must be a "
                              "string ending with '.json'")
        if (not isinstance(self.output_dir, str) or
            not self.output_dir.endswith("/")):
            raise ConfigError("Invalid 'outputDir' path: must be a string "
                              "ending with '/'")

    def _validate_simulation_period(self):
        """Validate simulation period."""
        # SimulationPeriod
        if (not isinstance(self.start_year, int) or
            not isinstance(self.end_year, int)):
            raise ConfigError("'start' and 'end' years must be integers")
        if self.start_year >= self.end_year:
            raise ConfigError("'start' year must be smaller than 'end' year")

    def _validate_simulation_options(self):
        """Validate simulation options."""
        # SimulationOptions
        if not isinstance(self.deficit_irrigation_mode, bool):
            raise ConfigError("'deficit_irrigation_mode' must be a boolean")

        if not isinstance(self.irrigation_efficiency_gw_mode, str) or \
           self.irrigation_efficiency_gw_mode not in ["enforce", "adjust"]:
            raise ConfigError("'irrigation_efficiency_gw_mode' must be "
                              "'enforce' or 'adjust'")

        if not isinstance(self.irrigation_input_based_on_aei, bool):
            raise ConfigError("'irrigation_input_based_on_aei' must be a "
                              "boolean")

        if not isinstance(self.correct_irrigation_t_aai_mode, bool):
            raise ConfigError("'correct_irr_simulation_by_t_aai' must be a "
                              "boolean")

        if not isinstance(self.time_extend_mode, bool):
            raise ConfigError("'time_extend_mode' must be a boolean")

    def _validate_params_setting(self):
        """Validate parameter settings."""
        # ParameterSetting
        if not isinstance(self.deficit_irrigation_factor, (int, float)) or \
           not 0 <= self.deficit_irrigation_factor <= 1:
            raise ConfigError("'deficit_irrigation_factor' must be a float "
                              "between 0 and 1")
        if not isinstance(self.efficiency_gw_threshold, (int, float)) or \
           not 0 <= self.efficiency_gw_threshold <= 1:
            raise ConfigError("'efficiency_gw_threshold' must be a float "
                              "between 0 and 1")

    def _validate_cell_specific_output(self):
        """Validate runtime options."""
        # CellSpecificOutput
        if not isinstance(self.cell_specific_output, dict):
            raise ConfigError("'CellSpecificOutput' must be a dictionary")

        flag = self.cell_specific_output.get("Flag")
        if not isinstance(flag, bool):
            raise ConfigError("'Flag' in 'CellSpecificOutput' must be a "
                              "boolean")

        coords = self.cell_specific_output.get("coords")
        if not isinstance(coords, dict):
            raise ConfigError("'coords' in 'CellSpecificOutput' must be a "
                              "dictionary")

        lat = coords.get("lat")
        lon = coords.get("lon")
        year = coords.get("year")
        month = coords.get("month")

        if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
            raise ConfigError("'lat' must be a float between -90 and 90")

        if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
            raise ConfigError("'lon' must be a float between -180 and 180")

        if not isinstance(year, int):
            raise ConfigError("'year' in 'CellSpecificOutput.coords' must be "
                              "an integer")
        if not self.start_year <= year <= self.end_year:
            raise ConfigError("'year' in 'CellSpecificOutput.coords' must be "
                              f"between {self.start_year} and {self.end_year}")

        if not isinstance(month, int) or not 1 <= month <= 12:
            raise ConfigError("'month' in 'CellSpecificOutput.coords' must be "
                              "an integer between 1 and 12")

    def _validate_output_selection(self):
        """Validate output selection"""
        # Validate OutputSelection
        def validate_output_selection_recursively(selection):
            if isinstance(selection, dict):
                for _, value in selection.items():
                    validate_output_selection_recursively(value)
            elif not isinstance(selection, bool):
                raise ConfigError(f"Value '{selection}' in 'OutputSelection' "
                                  "must be a boolean")

        validate_output_selection_recursively(self.output_selection)

    def get(self, *keys, default=None):
        """Get configuration values using their keys with dot notation."""
        results = []
        for key in keys:
            keys_split = key.split(".")
            value = self.config_data
            try:
                for k in keys_split:
                    value = value[k]
                results.append(value)
            except KeyError:
                results.append(default)
        return results if len(results) > 1 else results[0]

    def set(self, key, value):
        """Set a nested configuration value with dot notation."""
        keys = key.split(".")
        data = self.config_data
        try:
            for k in keys[:-1]:
                data = data[k]
            data[keys[-1]] = value
        except KeyError as exc:
            raise ConfigError(f"Key {key} not found in the configuration") \
                from exc

    def reload(self):
        """Reload the configuration from the file."""
        self._load_config(self.config_filename)
        self._initialize_config()
        self._validate_config()


if __name__ == '__main__':
    CONFIG_TEST = \
        './gwswuse_config.json'
    config = ConfigHandler(CONFIG_TEST)
