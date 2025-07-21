import logging
import sys
from logging.handlers import RotatingFileHandler

class LoggerFactory:
    @staticmethod
    def create_logger(name: str, file_name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.DEBUG)
            logger.addHandler(console_handler)

            file_handler = RotatingFileHandler(
                file_name,
                maxBytes=5 * 1024 * 1024,
                backupCount=2,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)

        return logger
