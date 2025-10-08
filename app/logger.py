from loguru import logger
import sys
import os

LOG_LEVEL = "DEBUG" if os.getenv("ENVIRONMENT") != "production" else "INFO"

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level=LOG_LEVEL,
    colorize=True,
)

log = logger
