# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""GWSWUSE logging module."""

import os
import logging
import logging.config


def setup_logger(debug=False):
    """
    Set up logging configuration for the application.

    This function configures the logging settings for the application,
    including formatters, handlers, and log levels. The configuration
    includes both console output and file logging with a rotating file
    handler.

    The log levels are set as follows:
    - Console: INFO and above (default) or DEBUG if specified
    - File: DEBUG and above (detailed information is saved to a file)

    Parameters
    ----------
    debug : bool, optional
        If True, sets the console log level to DEBUG instead of INFO.
    """
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Define different formats for different log levels
            if record.levelno in (logging.DEBUG, logging.WARNING,
                                  logging.ERROR, logging.CRITICAL):
                self._style._fmt = '%(levelname)s - %(message)s'
            else:
                self._style._fmt = '%(message)s'
            return super().format(record)
    # Ensure the logs directory exists
    os.makedirs('./logs', exist_ok=True)
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'custom': {
                # Use the custom formatter for stream handler
                '()': CustomFormatter,
                # Default format (used for INFO level)
                'format': '%(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                # Set to DEBUG if debug is True
                'level': 'DEBUG' if debug else 'INFO',
                'formatter': 'custom',
                'stream': 'ext://sys.stdout',  # Output to console (stdout)
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',  # DEBUG and above will be saved to file
                'formatter': 'detailed',
                'filename': './logs/gwswuse.log',
                'maxBytes': 5242880,  # 5 MB per log file
                'backupCount': 2,  # Keep up to 2 backup log files
                'mode': 'a',  # Append to the existing log file
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
    }

    # Apply the logging configuration
    logging.config.dictConfig(logging_config)


def get_logger(name):
    """
    Retrieve a configured logger by name.

    This function returns a logger with the specified name. The logger
    follows the configuration defined in `setup_logger`, ensuring that
    all logging follows a consistent format and destination.

    Parameters
    ----------
    name : str
        The name of the logger to be retrieved.

    Returns
    -------
    logging.Logger
        The configured logger instance.
    """
    return logging.getLogger(name)

# Example usage:
# setup_logger(debug=True)
# logger = get_logger(__name__)
# logger.info("This is an informational message.")
