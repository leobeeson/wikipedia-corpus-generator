import logging
import coloredlogs
from datetime import datetime


def setup_logger(name):
    logger = logging.getLogger(name)
    if name == "":
        coloredlogs.install(level="INFO", logger=logger)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_handler = logging.FileHandler(f"logs/logger_{timestamp}.log")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(file_handler)    
    return logger
