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
from termcolor import colored
from controller import configuration_module as cm
from controller import input_data_manager as idm

from model.irrigation_simulation import IrrigationSimulator
from model.domestic_simulation import DomesticSimulator
from model.manufacturing_simulation import ManufacturingSimulator
from model.thermal_power_simulation import ThermalPowerSimulator
from model.livestock_simulation import LivestockSimulator
from model.total_sectors_simulation import TotalSectorsSimulator

from view.output_data_manager import output_data_manager


def run_regwswuse():
    """Run the linking module GWSWUSE of WaterGAP."""
    start_time = time.time()
    # Load, check and preprocess input data with input_data_manager
    preprocessed_gwswuse_data, gwswuse_check_results, _, _ = \
        idm.input_data_manager(cm.input_data_path,
                               cm.gwswuse_convention_path,
                               cm.start_year,
                               cm.end_year,
                               cm.time_extend_mode
                               )
    print('GWSWUSE simulation starts ...')
    # Sector-specific simulations
    irr = IrrigationSimulator(preprocessed_gwswuse_data['irrigation'])
    dom = DomesticSimulator(preprocessed_gwswuse_data['domestic'])
    man = ManufacturingSimulator(preprocessed_gwswuse_data['manufacturing'])
    tp = ThermalPowerSimulator(preprocessed_gwswuse_data['thermal_power'])
    liv = LivestockSimulator(preprocessed_gwswuse_data['livestock'])

    # # Summarize sector-specific results for total cross-sector results
    total = TotalSectorsSimulator(irr, dom, man, tp, liv)

    gwswuse_results = {
        'irrigation': irr,
        'domestic': dom,
        'manufacturing': man,
        'thermal_power': tp,
        'livestock': liv,
        'total': total}

    output_data_manager(gwswuse_results, cm.output_selection, cm.output_dir,
                        cm.start_year, cm.end_year)
    end_time = time.time()
    print(f"ReGWSWUSE software runtime: {end_time - start_time} seconds.")
    # return preprocessed_gwswuse_data, gwswuse_check_results
    return gwswuse_check_results, gwswuse_results


if __name__ == "__main__":
    gwswuse_check_results, gwswuse_results = \
        run_regwswuse()
    # preprocessed_gwswuse_data, gwswuse_check_results = \
    #     run_regwswuse()
