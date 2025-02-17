# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""
Run GWSWUSE.
"""

import time
import json
from gwswuse_logger import setup_logger, get_logger
from misc import cli_args
from misc.ascii_image import LOGO
from controller import configuration_module as cm
from controller import input_data_manager as idm
from model.irrigation_simulation import IrrigationSimulator
from model.domestic_simulation import DomesticSimulator
from model.manufacturing_simulation import ManufacturingSimulator
from model.thermal_power_simulation import ThermalPowerSimulator
from model.livestock_simulation import LivestockSimulator
from model.total_sectors_simulation import TotalSectorsSimulator

from view.output_data_manager import output_data_manager

# Parse CLI arguments for config filename (args.name)& debug flag (args.debug)
args = cli_args.parse_cli()
# Call up logging configuration
setup_logger(args.debug)
# Get logger for the main script
logger = get_logger(__name__)


def run_gwswuse():
    """Run the linking module GWSWUSE of WaterGAP."""
    start_time = time.time()
    # gwswuse ascii image
    print(LOGO)

    logger.info("=" * 79)
    logger.info('Starting GWSWUSE software')
    logger.info("=" * 79)
    # =========================================================================
    #                     ====================
    #                        CONFIG HANDLER
    #                     ====================
    # Initialize ConfigHandler with the filename and debug flag
    logger.info("Starting configuration loading, initialization and "
                "validation...")
    config = cm.ConfigHandler(args.name)
    logger.info("Loading, initialization and validation of the configuration "
                "completed.\n")
    logger.debug(
        "SimulationOptions:\n%s",
        json.dumps(config.get("RuntimeOptions.SimulationOption"), indent=4)
        )
    logger.debug(
        "Parameter setting:\n%s \n",
        json.dumps(config.get("RuntimeOptions.ParameterSetting"), indent=4)
        )
    #                     ====================
    #                      INPUT DATA MANAGER
    #                     ====================

    # Load, check and preprocess input data with input_data_manager
    logger.info("Starting input data loading, checking and preprocessing...")
    preprocessed_gwswuse_data, gwswuse_check_results, _, _ = \
        idm.input_data_manager(config)
    logger.info(
        "Loading, checking and preprocessing of input data completed\n")

    #                     ====================
    #                      SIMULATION PROCESS
    #                     ====================
    # Sector-specific simulations
    logger.info("Starting GWSWUSE simulation for period:\n"
                "%s to %s\n", config.start_year, config.end_year
                )

    irr = \
        IrrigationSimulator(preprocessed_gwswuse_data['irrigation'],
                            config)
    logger.info("Irrigation simulation completed\n")
    dom = \
        DomesticSimulator(preprocessed_gwswuse_data['domestic'],
                          config)
    logger.info("Domestic simulation completed\n")
    man = \
        ManufacturingSimulator(preprocessed_gwswuse_data['manufacturing'],
                               config)
    logger.info("Manufacturing simulation completed\n")
    tp = \
        ThermalPowerSimulator(preprocessed_gwswuse_data['thermal_power'],
                              config)
    logger.info("Thermal power simulation completed\n")
    liv = LivestockSimulator(preprocessed_gwswuse_data['livestock'],
                             config)
    logger.info("Livestock simulation completed\n")

    # Summarize sector-specific results for total cross-sector results
    total = TotalSectorsSimulator(irr, dom, man, tp, liv, config)
    logger.info("Aggregation of total cross-sector results completed.\n")

    # Save results in dict for output data manager
    gwswuse_results = {
        'irrigation': irr,
        'domestic': dom,
        'manufacturing': man,
        'thermal_power': tp,
        'livestock': liv,
        'total': total}

    #                     ====================
    #                      RESULTS PROCESSING
    #                     ====================
    logger.info("Starting output data processing...")
    output_xr_data = output_data_manager(
        gwswuse_results, config.output_selection, config.output_dir,
        config.start_year, config.end_year
        )
    logger.info("Output data processing and saving completed.\n")

    # =========================================================================
    end_time = time.time()
    logger.info("=" * 79)
    logger.info("GWSWUSE software run completed")
    logger.info("Total runtime: %s seconds.", end_time - start_time)
    logger.info("=" * 79)

    return gwswuse_check_results, gwswuse_results, output_xr_data


if __name__ == "__main__":
    gwswuse_input_check_results, gwswuse_results_output, gwswuse_xr_data = \
        run_gwswuse()
