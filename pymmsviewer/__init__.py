from sys import stderr

from loguru import logger

log_fmt = "<level>{level:<8}</level> | <green>{message}</green> | {file}<d>/fn:</d>{function}<d>/line:</d>{line} @ <yellow>{time:ddd DD-MM-YYYY HH:mm:ss.SS}</yellow>"

logger.remove(0)
logger.add(
    stderr,
    format=log_fmt,
)
logger.add("JP_log.log", rotation="10 MB", format=log_fmt)
