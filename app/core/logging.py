import logging
from logging.handlers import RotatingFileHandler
from typing import List

from app.middlewares.logging import RequestLogData

class LoggerFactory:
    @staticmethod
    def create_console_logger(name="console_api_logger", level=logging.INFO):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(level)
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        return logger

    @staticmethod
    def create_file_logger(
            name="file_api_logger",
            level=logging.INFO,
            file_path="api_requests.log",
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5
    ):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(level)
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger