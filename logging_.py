import logging
import logging.config
from datetime import datetime
from pathlib import Path


def setup_logging(
        log_level_file="DEBUG",
        log_level_console="INFO",
        log_file=None,
        log_dir="logs",
        app_name="app"
):
    """
    Configure application-wide logging.

    Args:
        log_level_file (str): Logging level for file output
        log_level_console (str): Logging level for console output
        log_file (str, optional): Custom log filename
        log_dir (str): Directory for log files
        app_name (str): Application name for default log filename

    Returns:
        str: Path to the created log file
    """

    # Create logs directory
    log_path_obj = Path(log_dir)
    log_path_obj.mkdir(exist_ok=True)

    # Generate log filename if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{app_name}_{timestamp}.log"

    log_file_path = log_path_obj / log_file

    # Logging configuration dictionary
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s | %(name)-20s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
            },
            'minimal': {
                'format': '%(levelname)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level_console,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level_file,
                'formatter': 'detailed',
                'filename': str(log_file_path),
                'mode': 'a',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }

    # Apply configuration
    logging.config.dictConfig(config)

    # Create logger for this module and log setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - File: {log_file_path}")
    logger.debug(f"File log level: {log_level_file}, Console log level: {log_level_console}")

    return str(log_file_path)


def get_logger(name):
    """
    Convenience function to get a logger with the configured settings.

    Args:
        name (str): Logger name (usually __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
