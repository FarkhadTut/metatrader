import logging
import colorlog

# Create a logger

logger = logging.getLogger(__name__)
logging.addLevelName(10, 'SUCCESS')

# Create a color formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(log_color)s%(levelname)s] [%(asctime)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S",
    log_colors={
        'SUCCESS': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# Create a console handler and set the formatter
ch = logging.StreamHandler()
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

# Set the logging level
logger.setLevel(logging.DEBUG)
# # Example usage
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")