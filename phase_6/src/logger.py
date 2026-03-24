import logging
import os

# Define log file path relative to execution
LOG_FILE = "phase_6_dump.log"

def setup_logger():
    """Sets up a centralized logger that writes to dump.log."""
    logger = logging.getLogger("market_analyst")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.handlers:
        # Create file handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)

        # Create console handler (optional, but good for local dev)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logger()

from functools import wraps

def log_function_call(func):
    """Decorator to log function calls and their results."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in function {func.__name__}: {str(e)}", exc_info=True)
            raise e
    return wrapper
