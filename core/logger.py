import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures a rotating file logger for the application.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Set the minimum level of messages to log

    # Prevent the logger from propagating messages to the parent (e.g., console)
    logger.propagate = False

    # Create a rotating file handler
    # This will create up to 5 log files, each 1MB in size.
    handler = RotatingFileHandler(
        "synapse.log", maxBytes=1_000_000, backupCount=5
    )
    
    # Create a formatter to define the log message structure
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger, but only if it doesn't have handlers already
    if not logger.handlers:
        logger.addHandler(handler)

