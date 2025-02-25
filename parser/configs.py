from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

BASE_DIR = Path(__file__).parent


def configure_logging():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'report_parser.log'

    rotating_heandler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=5, encoding='utf-8')

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DT_FORMAT,
        handlers=(rotating_heandler, logging.StreamHandler())
    )