import logging
from argparse import ArgumentParser
from logging.handlers import RotatingFileHandler
from typing import KeysView

from constants import (BASE_DIR, DT_FORMAT, LOG_FORMAT, RESPONSE_ENCODING,
                       OutputType)


def configure_argument_parser(available_modes: KeysView) -> ArgumentParser:
    parser = ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=OutputType.from_string,
        choices=tuple([e.value for e in OutputType]),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'

    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding=RESPONSE_ENCODING
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
