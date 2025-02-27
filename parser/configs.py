import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = "%d.%m.%Y %H:%M:%S"

BASE_DIR = Path(__file__).parent


def configure_logging():
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "report_parser.log"

    rotating_heandler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=5, encoding="utf-8")

    logging.basicConfig(
        level=logging.INFO, format=LOG_FORMAT, datefmt=DT_FORMAT, handlers=(rotating_heandler, logging.StreamHandler())
    )


def configure_argument_parser():
    """Запуск парсера из терминала"""
    parser = argparse.ArgumentParser(description="Парсер 'Бюллетени по итогам торгов Нефтепродуктов'")
    parser.add_argument(
        "-y", "--year_stop", default=2023, type=int, help="Год давности бюллетеней. До какого года парсить бюллетени."
    )
    return parser
