from loguru import logger
import logging
import inspect
from asuna_bot.config import __version__, __logpath__


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def set_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.add(f"{__logpath__}asuna_{__version__}.log", backtrace=True, diagnose=True, rotation="50 MB")