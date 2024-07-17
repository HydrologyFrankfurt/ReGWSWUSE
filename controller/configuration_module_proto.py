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
modname = (os.path.basename(__file__))
modname = modname.split('.')[0]

# ++++++++++++++++++++++++++++++++++++++++++++++++
# Parsing  Argguments for CLI from cli_args module
# +++++++++++++++++++++++++++++++++++++++++++++++++
args = cli.parse_cli()

# ===============================================================
# Reading in configuration file and handling file related errors)
# ===============================================================


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
        log.config_logger(logging.ERROR, modname, 'Configuration file '
                            'not found', args.debug)
        sys.exit()  # don't run code if cofiguration file does not exist
    else:
        print('Configuration loaded successfully')
    return config_content


# test_filename = ("C:/Users/lniss/Desktop/ReGWSWUSE_LN/source/"
#                  "gwswuse_configuration.json")
config_file = config_handler(args.name)
# config_file = config_handler(test_filename)

# =============================================================================
# Get path for water use and gwswuse static data
# =============================================================================
input_dir = config_file['FilePath']['inputDir']

gwswuse_convention_path = input_dir['gwswuse_convention']

output_dir = config_file['FilePath']['outputDir']

# =============================================================================
# # Initializing Simulation options (bottleneck to run simulation)
# =============================================================================
simulation_options = \
    config_file['RuntimeOptions']['SimulationOption']

time_extend_mode = \
    simulation_options['time_extend_mode']

correct_irr_with_t_aai_mode = \
    simulation_options['correct_irr_simulation_by_t_aai']

efficiency_gw_mode = \
    simulation_options['irrigation_efficiency_gw_mode']

deficit_irrigation_mode = \
    simulation_options['deficit_irrigation_mode']
# =============================================================================
# Initializing parameter setting for:
#  - groundwater irrigation efficiency
#  - deficit irrigation factor
# =============================================================================
params_setting = \
    config_file['RuntimeOptions']['ParameterSetting']

efficiency_gw_threshold = \
    params_setting["efficiency_gw_threshold"]

deficit_irrigation_factor = \
    params_setting["deficit_irrigation_factor"]

# =============================================================================
# # Initializing  simulation period and time step
# =============================================================================
simulation_period = config_file['RuntimeOptions']['SimulationPeriod']

start_year = simulation_period['start']
end_year = simulation_period['end']

# =============================================================================
# Initializing output selection for output data manager
# =============================================================================
output_selection = config_file['OutputSelection']
