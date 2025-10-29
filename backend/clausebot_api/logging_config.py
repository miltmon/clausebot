"""
ClauseBot Structured Logging
Enterprise-grade logging with JSON output for centralized log aggregation

Features:
- Structured JSON logs (timestamp, service, level, message, context)
- Correlation IDs for request tracing
- Performance metrics (duration tracking)
- Error context capture
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Integration:
- Works with Render logs (JSON parsing)
- Compatible with Datadog, CloudWatch, LogDNA, etc.
- Request ID propagation for distributed tracing
"""
import logging
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
from functools import wraps

# Context var for request correlation ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Output format:
    {
        "timestamp": "2025-10-28T15:30:00.123Z",
        "level": "INFO",
        "service": "clausebot-api",
        "message": "Cache hit",
        "request_id": "abc123",
        "context": {"endpoint": "/quiz", "hit_rate": 0.75}
    }
    """
    
    def __init__(self, service_name: str = "clausebot"):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_ctx.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add module/function context
        log_entry["location"] = f"{record.filename}:{record.lineno}"
        
        # Add extra context if provided
        if hasattr(record, 'context'):
            log_entry["context"] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add duration if present (from timing decorator)
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        return json.dumps(log_entry)


class StructuredLogger:
    """
    Structured logger wrapper with convenience methods.
    
    Usage:
        logger = StructuredLogger("clausebot-api")
        
        # Simple logging
        logger.info("Cache hit", endpoint="/quiz", hit_rate=0.75)
        
        # With request ID
        with logger.request_context("req-123"):
            logger.info("Processing request")
            logger.error("Failed", error="timeout")
    """
    
    def __init__(self, service_name: str, level: str = "INFO"):
        self.service = service_name
        self.logger = logging.getLogger(service_name)
        
        # Set log level
        self.logger.setLevel(getattr(logging, level))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add structured JSON handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter(service_name))
        self.logger.addHandler(handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log(self, level: str, message: str, **context):
        """Internal logging method with context."""
        extra = {'context': context} if context else {}
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def debug(self, message: str, **context):
        """Log debug message with context."""
        self._log("DEBUG", message, **context)
    
    def info(self, message: str, **context):
        """Log info message with context."""
        self._log("INFO", message, **context)
    
    def warning(self, message: str, **context):
        """Log warning message with context."""
        self._log("WARNING", message, **context)
    
    def error(self, message: str, **context):
        """Log error message with context."""
        self._log("ERROR", message, **context)
    
    def critical(self, message: str, **context):
        """Log critical message with context."""
        self._log("CRITICAL", message, **context)
    
    def exception(self, message: str, exc: Exception, **context):
        """Log exception with full traceback."""
        context['exception_type'] = type(exc).__name__
        context['exception_message'] = str(exc)
        self.logger.exception(message, extra={'context': context})
    
    def request_context(self, request_id: str):
        """
        Context manager for request-scoped logging.
        
        Usage:
            with logger.request_context("req-123"):
                logger.info("Processing request")
        """
        class RequestContext:
            def __enter__(self_):
                self_.token = request_id_ctx.set(request_id)
                return self
            
            def __exit__(self_, *args):
                request_id_ctx.reset(self_.token)
        
        return RequestContext()
    
    def timed(self, operation: str = None):
        """
        Decorator to log operation duration.
        
        Usage:
            @logger.timed("fetch_quiz")
            def fetch_quiz():
                ...
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                op_name = operation or func.__name__
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start) * 1000
                    
                    # Log with duration
                    record = self.logger.makeRecord(
                        self.service,
                        logging.INFO,
                        func.__code__.co_filename,
                        func.__code__.co_firstlineno,
                        f"Operation completed: {op_name}",
                        (),
                        None
                    )
                    record.duration_ms = round(duration_ms, 2)
                    record.context = {'operation': op_name}
                    self.logger.handle(record)
                    
                    return result
                
                except Exception as e:
                    duration_ms = (time.time() - start) * 1000
                    self.error(
                        f"Operation failed: {op_name}",
                        operation=op_name,
                        duration_ms=round(duration_ms, 2),
                        error=str(e)
                    )
                    raise
            
            return wrapper
        return decorator


# Global logger instances
api_logger = StructuredLogger("clausebot-api", level="INFO")
worker_logger = StructuredLogger("clausebot-worker", level="INFO")
sync_logger = StructuredLogger("clausebot-sync", level="INFO")


# FastAPI middleware for request logging
class RequestLoggingMiddleware:
    """
    ASGI middleware for automatic request/response logging.
    
    Usage in FastAPI:
        from clausebot_api.logging_config import RequestLoggingMiddleware
        
        app.add_middleware(RequestLoggingMiddleware)
    """
    
    def __init__(self, app, logger: StructuredLogger = None):
        self.app = app
        self.logger = logger or api_logger
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing
        start_time = time.time()
        
        # Log request
        with self.logger.request_context(request_id):
            self.logger.info(
                "Request started",
                method=scope["method"],
                path=scope["path"],
                client=scope.get("client", ["unknown", 0])[0]
            )
            
            # Capture response status
            status_code = 500  # Default
            
            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                await send(message)
            
            try:
                await self.app(scope, receive, send_wrapper)
            finally:
                # Log response
                duration_ms = (time.time() - start_time) * 1000
                
                log_level = "info" if status_code < 400 else "error"
                getattr(self.logger, log_level)(
                    "Request completed",
                    method=scope["method"],
                    path=scope["path"],
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2)
                )


# Convenience function for setup
def setup_logging(service_name: str = "clausebot", level: str = "INFO") -> StructuredLogger:
    """
    Setup structured logging for a service.
    
    Args:
        service_name: Name of the service (for log tagging)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured StructuredLogger instance
    
    Usage:
        from clausebot_api.logging_config import setup_logging
        
        logger = setup_logging("clausebot-api", level="INFO")
        logger.info("Service started")
    """
    return StructuredLogger(service_name, level)

