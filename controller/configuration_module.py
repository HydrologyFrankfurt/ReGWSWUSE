# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Configuartion handling module."""

import json
import os
import sys
from datetime import datetime
from gwswuse_logger import get_logger

# ===============================================================
# Set up the logger for the entire configuration module
# ===============================================================

logger = get_logger(__name__)


class ConfigHandler:
    """Class to load, validate and initialize configuration file."""

    # Make sure that the instance can only be instantiated once
    _instance = None

    def __new__(cls, config_filename='gwswuse_config.json'):
        """Singleton implementation to ensure that only one instance exists."""
        # Check if an instance already exists
        if cls._instance is None:
            # Create the instance if it doesn't exist
            cls._instance = super(ConfigHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_filename='gwswuse_config.json'):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            # Load the configuration file
            self._load_config(config_filename)
            # Initialize configuration (custom logic should go here)
            self._initialize_config()
            # Initialize errors_found as an instance variable
            self.errors_found = False
            # Validate the configuration
            self._validate_config()
            # Save configuration in output data folder
            self.save_config()

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
            # Attempt to open and load the JSON configuration file
            with open(self.config_filename, encoding="utf-8") as filename:
                self.config_data = json.load(filename)
        except FileNotFoundError:
            # Handle the case where the config file does not exist
            logger.error(
                'Configuration file not found: %s', self.config_filename
                )
            sys.exit()  # don't run code if cofiguration file does not exist
        except json.JSONDecodeError as json_error:
            # Handle invalid JSON format
            logger.error(
                "Error decoding JSON configuration file: %s - %s",
                filename, str(json_error)
                )
            sys.exit()
        else:
            # If no exceptions occurred, configuration was loaded successfully
            logger.debug('Configuration loaded successfully')

    def _initialize_config(self):
        """Initialize configuration parameters in attributes of the class."""
        # =====================================================================
        # Initialize FilePath
        # =====================================================================
        # Retrieve input directory settings
        input_dir = self.get("FilePath.inputDir")
        self.input_data_path = input_dir.get("input_data")
        self.convention_path = input_dir.get("gwswuse_convention")

        # Retrieve output directory settings
        self.output_dir = self.get("FilePath.outputDir")

        # =====================================================================
        # Initialize SimulationPeriod
        # =====================================================================
        # Retrieve simulation period settings (start and end year)
        simulation_period = self.get("RuntimeOptions.SimulationPeriod")
        self.start_year = simulation_period.get("start")
        self.end_year = simulation_period.get("end")
        logger.debug(
            "Simulation period from %s to %s", self.start_year, self.end_year
            )
        # =====================================================================
        # Initialize SimulationOptions
        # =====================================================================
        # Retrieve various simulation options
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

        # =====================================================================
        # Initialize ParameterSetting
        # =====================================================================
        # Retrieve parameter settings for deficit irrigation and efficiency_gw
        params_setting = self.get("RuntimeOptions.ParameterSetting")
        self.deficit_irrigation_factor = \
            params_setting.get("deficit_irrigation_factor")
        self.efficiency_gw_threshold = \
            params_setting.get("efficiency_gw_threshold")

        # =====================================================================
        # Initialize CellSpecificOutput
        # =====================================================================
        # Retrieve cell-specific output settings
        self.cell_specific_output = \
            self.get("RuntimeOptions.CellSpecificOutput")

        # =====================================================================
        # Initialize OutputSelection
        # =====================================================================
        # Retrieve output selection settings
        self.output_selection = self.get("OutputSelection")

        logger.debug('Configuration initialized successfully' + '\n')

    def _validate_config(self):
        """Validate configuration directly after loading and initializing."""
        # Set errors_found to True if any error is logged in validations
        self._validate_paths()
        self._validate_simulation_period()
        self._validate_simulation_options()
        self._validate_params_setting()
        self._validate_cell_specific_output()
        self._validate_output_selection()
        # Check if any errors were found

        if self.errors_found:
            logger.error(
                "Configuration validation failed. Please check the errors "
                "above.")
            sys.exit(1)
        else:
            logger.debug("Configuration validated successfully\n")

    def _validate_paths(self):
        """Validate file paths."""
        # Ensure 'input_data_path' is an existing directory
        if not os.path.isdir(self.input_data_path):
            logger.error(
                "Invalid 'input_data_path': must be a valid directory path"
                )
            self.errors_found = True
        # Ensure 'convention_path' is an existing .json file
        if not (os.path.isfile(self.convention_path)
                and self.convention_path.endswith('.json')
                ):
            logger.error(
                "Invalid 'convention_path': must be an existing .json file"
                )
            self.errors_found = True
        # Ensure 'output_dir' is an existing directory
        if not os.path.isdir(self.output_dir):
            logger.error(
                "Invalid 'output_dir': must be a valid directory path"
                )
            self.errors_found = True

    def _validate_simulation_period(self):
        """Validate simulation period."""
        # Check that 'start_year' and 'end_year' are integers
        if (not isinstance(self.start_year, int) or
            not isinstance(self.end_year, int)):

            logger.error("'start' and 'end' years must be integers")
            self.errors_found = True
        # Ensure 'start_year' is smaller than 'end_year'
        if self.start_year >= self.end_year:
            logger.error("'start' year must be smaller than 'end' year")
            self.errors_found = True

    def _validate_simulation_options(self):
        """Validate simulation options."""
        # Check if 'deficit_irrigation_mode' is a boolean
        if not isinstance(self.deficit_irrigation_mode, bool):
            logger.error("'deficit_irrigation_mode' must be a boolean")
            self.errors_found = True
        # Check if 'irrigation_efficiency_gw_mode' is 'enforce' or 'adjust'
        if (not isinstance(self.irrigation_efficiency_gw_mode, str)
            or
            self.irrigation_efficiency_gw_mode not in ["enforce", "adjust"]):
            logger.error(
                "'irrigation_efficiency_gw_mode' must be 'enforce' or 'adjust'"
                )
            self.errors_found = True
        # Check if 'irrigation_input_based_on_aei' is a boolean
        if not isinstance(self.irrigation_input_based_on_aei, bool):
            logger.error(
                "'irrigation_input_based_on_aei' must be a boolean"
                )
            self.errors_found = True
        # Check if 'correct_irrigation_t_aai_mode' is a boolean
        if not isinstance(self.correct_irrigation_t_aai_mode, bool):
            logger.error(
                "'correct_irrirgation_t_aai_mode' must be a boolean"
                )
            self.errors_found = True
        # Check if 'correct_irrigation_t_aai_mode is applicable
        if self.correct_irrigation_t_aai_mode and self.end_year < 2016:
            logger.error(
                "'correct_irrigation_t_aai_mode' can´t be used for simulation "
                "period before 2016."
                )
            self.errors_found = True
        # Check if 'time_extend_mode' is a boolean
        if not isinstance(self.time_extend_mode, bool):
            logger.error("'time_extend_mode' must be a boolean")
            self.errors_found = True
        if self.time_extend_mode and self.end_year > 2050:
            logger.warning(
                "'time_extend_mode' is enabled with an 'end_year' after 2050."
                )

    def _validate_params_setting(self):
        """Validate parameter settings."""
        # Ensure 'deficit_irrigation_factor' is a float between 0 and 1
        if not isinstance(self.deficit_irrigation_factor, (int, float)) or \
           not 0 <= self.deficit_irrigation_factor <= 1:
            logger.error(
                "'deficit_irrigation_factor' must be a float between 0 and 1"
                )
            self.errors_found = True
        # Ensure 'deficit_irrigation_factor' is a float between 0 and 1
        if not isinstance(self.efficiency_gw_threshold, (int, float)) or \
           not 0 <= self.efficiency_gw_threshold <= 1:
            logger.error(
                "'efficiency_gw_threshold' must be a float between 0 and 1"
                )
            self.errors_found = True

    def _validate_cell_specific_output(self):
        """Validate runtime options."""
        # Ensure 'CellSpecificOutput' is a dictionary
        if not isinstance(self.cell_specific_output, dict):
            logger.error("'CellSpecificOutput' must be a dictionary")
            self.errors_found = True
        # Ensure 'CellSpecificOutput' is a dictionary
        flag = self.cell_specific_output.get("flag")
        if not isinstance(flag, bool):
            logger.error(
                "'flag' in 'CellSpecificOutput' must be a boolean"
                )
            self.errors_found = True
        # Only validate 'coords' if 'flag' is True
        if flag:
            coords = self.cell_specific_output.get("coords")
            if not isinstance(coords, dict):
                logger.critical(
                    "'coords' in 'CellSpecificOutput' must be a dictionary")
                self.errors_found = True
                return

            lat = coords.get("lat")
            lon = coords.get("lon")
            year = coords.get("year")
            month = coords.get("month")

            # Check if 'lat' and 'lon' are within valid ranges
            if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
                logger.error("'lat' must be a float between -90 and 90")
                self.errors_found = True
            if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
                logger.error("'lon' must be a float between -180 and 180")
                self.errors_found = True

            # Check if 'year' is integer and within the simulation period
            if not isinstance(year, int):
                logger.error(
                    "'year' in 'CellSpecificOutput.coords' must be an integer"
                    )
                self.errors_found = True

            elif not self.start_year <= year <= self.end_year:
                logger.error(
                    "'year' in 'CellSpecificOutput.coords' must be between "
                    "'SimulationPeriod.start' and 'SimulationPeriod.end'"
                    )
                self.errors_found = True

            # Check if 'month' is a valid integer
            if not isinstance(month, int) or not 1 <= month <= 12:
                logger.error(
                    "'month' in 'CellSpecificOutput.coords' must be an "
                    "integer between 1 and 12"
                    )
                self.errors_found = True

    def _validate_output_selection(self):
        """Validate output selection."""
        # Recursively validate that all values in 'OutputSelection' are bools
        def validate_output_selection_recursively(selection):
            if isinstance(selection, dict):
                for _, value in selection.items():
                    validate_output_selection_recursively(value)
            elif not isinstance(selection, bool):
                logger.error(
                    "Value '%s' in 'OutputSelection' must be a boolean",
                    selection
                    )

        validate_output_selection_recursively(self.output_selection)

    def get(self, *keys, default=None):
        """Get configuration values using their keys with dot notation."""
        results = []
        for key in keys:
            keys_split = key.split(".")
            value = self.config_data
            try:
                # Traverse the dictionary using the split keys
                for k in keys_split:
                    value = value[k]
                results.append(value)
            except KeyError:
                # Append default if key is not found
                results.append(default)
        # Append default if key is not found
        return results if len(results) > 1 else results[0]

    def reload(self):
        """Reload the configuration from the file."""
        self._load_config(self.config_filename)
        self._initialize_config()
        self._validate_config()

    def save_config(self):
        """Save configuration in output_path json file."""
        current_date = datetime.now().strftime("%Y_%m_%d")
        config_output_name = \
            os.path.join(self.output_dir, "config_" + current_date + ".json")
        try:
            with open(config_output_name, "w", encoding="utf-8") as json_file:
                json.dump(self.config_data, json_file, indent=4)

        except IOError as e:
            logger.error("Failed to save configuration to %s: %s",
                         config_output_name, str(e))
