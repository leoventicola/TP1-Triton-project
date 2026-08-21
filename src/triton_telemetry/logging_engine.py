# src/triton_telemetry/logging_engine.py
import json
import logging
import logging.config
import logging.handlers
import queue
import os
import gzip
import shutil
from datetime import datetime, timezone
from typing import Any, Dict

# Callbacks de compresión en caliente para el RotatingFileHandler
def gzip_namer(name: str) -> str:
    """Modifica el nombre del archivo de backup agregando la extensión .gz."""
    return name + ".gz"


def gzip_rotator(source: str, dest: str):
    """Comprime el archivo rotado a formato .gz de forma atómica y elimina el original."""
    with open(source, 'rb') as f_in:
        with gzip.open(dest, 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(source)


class AsyncJSONFormatter(logging.Formatter):
    """
    Formateador JSON de nivel productivo capaz de serializar tracebacks y
    estructuras complejas recursivas de ExceptionGroups de forma jerárquica.
    """
    def _serialize_exception(self, exc: BaseException) -> Dict[str, Any]:
        """Estructura recursivamente excepciones, notas dinámicas y causas raíz."""
        exc_data: Dict[str, Any] = {
            "class": exc.__class__.__name__,
            "message": str(exc),
            "notes": getattr(exc, "__notes__", [])
        }

        # Soporte para ExceptionGroup (Python 3.11+)
        if isinstance(exc, ExceptionGroup):
            exc_data["nested_exceptions"] = [
                self._serialize_exception(nested_err)
                for nested_err in exc.exceptions
            ]
        # Soporte para encadenamiento raise ... from
        elif exc.__cause__:
            exc_data["cause"] = self._serialize_exception(exc.__cause__)
            
        return exc_data

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp ISO 8601 UTC estricto (compatible con Python 3.12+)
        dt_utc = datetime.fromtimestamp(record.created, tz=timezone.utc)
        
        log_payload: Dict[str, Any] = {
            "timestamp": dt_utc.isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "async_task": getattr(record, "taskName", "None"),
            "thread_name": record.threadName,
            "filename": record.filename,
            "line": record.lineno
        }

        # Serialización del árbol de excepciones
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_value:
                log_payload["exception_tree"] = self._serialize_exception(exc_value)
                log_payload["stack_trace"] = self.formatException(record.exc_info)

        # Captura dinámica de metadatos inyectados vía 'extra'
        reserved_fields = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName"
        }
        
        for key, value in record.__dict__.items():
            if key not in reserved_fields and not key.startswith('_'):
                log_payload[key] = value

        return json.dumps(log_payload, ensure_ascii=False)


def setup_triton_logging(log_filename: str = "triton_services.log") -> logging.Logger:
    """Configura el pipeline de logging declarativo dictConfig y acopla el listener asíncrono."""
    logging_schema = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_structured": {
                "()": AsyncJSONFormatter
            },
            "console_clean": {
                "format": "%(asctime)s [%(levelname)s] (%(taskName)s) %(message)s",
                "datefmt": "%H:%M:%S"
            }
        },
        "handlers": {
            "stdout_console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console_clean",
                "stream": "ext://sys.stdout"
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json_structured",
                "filename": log_filename,
                "maxBytes": 2 * 1024 * 1024,  # 2 MB por archivo
                "backupCount": 3,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "triton_monitor": {
                "level": "DEBUG",
                "handlers": ["stdout_console", "rotating_file"],
                "propagate": False
            }
        }
    }

    logging.config.dictConfig(logging_schema)
    app_logger = logging.getLogger("triton_monitor")

    # Inyección de las retrollamadas de compresión GZIP
    file_handler = next((h for h in app_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)), None)
    if file_handler:
        file_handler.namer = gzip_namer
        file_handler.rotator = gzip_rotator

    # Desacoplamiento No Bloqueante: QueueHandler + QueueListener
    log_queue = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    
    # Extraer los handlers síncronos y asignarle al Listener asíncrono
    real_handlers = app_logger.handlers
    listener = logging.handlers.QueueListener(log_queue, *real_handlers, respect_handler_level=True)
    
    # Forzar al logger a pasar todo de forma instantánea a la cola
    app_logger.handlers = [queue_handler]
    
    # Arrancar despachador secundario
    listener.start()
    app_logger.listener = listener

    return app_logger