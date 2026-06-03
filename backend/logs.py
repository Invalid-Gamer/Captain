# Author: @ingressy
import logging
import os
from logging.handlers import TimedRotatingFileHandler

def log_handler() -> None:
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)

    log_file = os.path.join(LOG_DIR, "main.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
    )

    handler = TimedRotatingFileHandler(
        log_file,
        when="H",
        interval=1,
        backupCount=48,
        encoding="utf-8",
    )
    handler.suffix = "%Y-%m-%d_%H-%M-%S"
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # verhindert doppelte Handler beim erneuten Import
    if root.handlers:
        root.handlers.clear()

    root.addHandler(handler)
    root.addHandler(console)