# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================

"""Arguments for command line interface (CLI)."""

# =============================================================================
# This module is used by Configuration handler and Input handler.
# =============================================================================


import argparse


def parse_cli():
    """
    Parse command line arguments.

    Returns
    -------
    args : argparse.Namespace
        Parsed command line arguments.
    """
    parser = \
        argparse.ArgumentParser(
            description="Parse configuration file name and debug flag.")

    # optional argument for name of configuration file
    default_path = "./"
    default_version = "gwswuse_wgap_2_2d_1901_1905/"
    default_config = \
        (default_path +
         "gwswuse_config.json")

    parser.add_argument('name', type=str, nargs='?', default=default_config,
                        help=('Name of the configuration file '
                              '(default: default_config.json)'))

    # Optionales Argument für Debug-Modus (True/False)
    parser.add_argument('--debug', action="store_true", default=True,
                        help=(
                            'Enable or disable TraceBack for debugging by '
                            'setting True or False'))
    args = parser.parse_args()
    return args
