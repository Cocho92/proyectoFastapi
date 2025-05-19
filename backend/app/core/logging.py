import logging
import sys
from typing import Dict, Any

def setup_logging():
    """Configura el logging de la aplicación"""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {"handlers": ["console"], "level": "INFO"},
            "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
            "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "gspread": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        },
    }
    
    # Configuración del logging
    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado"""
    return logging.getLogger(name)