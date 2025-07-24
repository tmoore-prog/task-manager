import logging
import json
from datetime import datetime, timezone


class StructuredLogger:
    '''A customized logger that writes JSON with structured data to file'''

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler('logs.json', 'a', encoding='UTF-8')
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, event, **kwargs):
        '''Log level INFO with structured data'''
        log_data = self._build_log_entry(event, "INFO", **kwargs)
        self.logger.info(json.dumps(log_data))

    def error(self, event, **kwargs):
        '''Log level ERROR with structured data'''
        log_data = self._build_log_entry(event, "ERROR", **kwargs)
        self.logger.error(json.dumps(log_data))

    def warning(self, event, **kwargs):
        '''Log level WARNING with structured data'''
        log_data = self._build_log_entry(event, "WARNING", **kwargs)
        self.logger.warning(json.dumps(log_data))

    def _build_log_entry(self, event, level, **kwargs):
        '''Build standardized log entry'''
        from flask import g
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            "request_id": getattr(g, 'request_id', None),
            "service": "task_api",
            "version": 1.0
        }
        log_entry.update(**kwargs)
        return log_entry


class JsonFormatter(logging.Formatter):
    '''Custom formatter to ensure JSON'''
    def format(self, record):
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name
            }
            return json.dumps(log_entry)
