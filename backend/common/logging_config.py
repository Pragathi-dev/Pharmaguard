import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class JsonLinesFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs log records as single-line JSON objects.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_object)


def get_logger(name: str = "pharmaguard") -> logging.Logger:
    """
    Creates and configures a structured JSON lines logger.
    Logs are written to both standard output and `logs/pharmaguard.jsonl`.

    Args:
        name (str): Name of the logger component.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if logger is fetched multiple times
    if logger.handlers:
        return logger

    formatter = JsonLinesFormatter()

    # Console Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (logs/pharmaguard.jsonl)
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        logs_dir = project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(logs_dir / "pharmaguard.jsonl", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass  # If file logging cannot be initialized, fallback to console handler

    return logger
