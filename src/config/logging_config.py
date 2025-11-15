"""
Logging Configuration
Centralized logging setup for the entire application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from src.core.constants import (
    LOGS_DIR,
    LOG_FILE,
    ERROR_LOG_FILE,
    DEBUG_LOG_FILE,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
)

# =============================================================================
# Logging Configuration
# =============================================================================

class LoggingConfig:
    """Centralized logging configuration."""
    
    def __init__(
        self,
        log_level: str = LOG_LEVEL_INFO,
        log_to_file: bool = True,
        log_to_console: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            log_to_console: Enable console logging
            max_file_size: Maximum size of log file before rotation (bytes)
            backup_count: Number of backup log files to keep
        """
        self.log_level = log_level
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Ensure logs directory exists
        Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self) -> logging.Logger:
        """
        Setup logging configuration.
        
        Returns:
            Root logger instance
        """
        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        
        # Remove existing handlers
        logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        
        # Console handler
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handlers
        if self.log_to_file:
            # Main log file (all levels)
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Error log file (errors only)
            error_handler = RotatingFileHandler(
                ERROR_LOG_FILE,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(LOG_LEVEL_ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)
            
            # Debug log file (debug and above)
            if self.log_level == LOG_LEVEL_DEBUG:
                debug_handler = RotatingFileHandler(
                    DEBUG_LOG_FILE,
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count,
                    encoding='utf-8'
                )
                debug_handler.setLevel(LOG_LEVEL_DEBUG)
                debug_handler.setFormatter(formatter)
                logger.addHandler(debug_handler)
        
        return logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the given name.
        
        Args:
            name: Logger name (usually __name__ of the module)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


# =============================================================================
# Specialized Loggers
# =============================================================================

class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(LOG_LEVEL_INFO)
        
        # Performance log file
        handler = RotatingFileHandler(
            f"{LOGS_DIR}/performance.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            LOG_DATE_FORMAT
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_timing(self, operation: str, duration: float, details: Optional[dict] = None):
        """Log timing information."""
        msg = f"{operation}: {duration:.4f}s"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)
    
    def log_cache_hit(self, cache_key: str):
        """Log cache hit."""
        self.logger.debug(f"Cache HIT: {cache_key}")
    
    def log_cache_miss(self, cache_key: str):
        """Log cache miss."""
        self.logger.debug(f"Cache MISS: {cache_key}")


class APILogger:
    """Logger for API requests and responses."""
    
    def __init__(self):
        self.logger = logging.getLogger("api")
        self.logger.setLevel(LOG_LEVEL_INFO)
        
        # API log file
        handler = TimedRotatingFileHandler(
            f"{LOGS_DIR}/api.log",
            when='midnight',
            interval=1,
            backupCount=7,  # Keep 7 days
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            LOG_DATE_FORMAT
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_request(self, api_name: str, endpoint: str, params: Optional[dict] = None):
        """Log API request."""
        msg = f"[{api_name}] Request: {endpoint}"
        if params:
            msg += f" | Params: {params}"
        self.logger.info(msg)
    
    def log_response(self, api_name: str, status_code: int, duration: float):
        """Log API response."""
        self.logger.info(f"[{api_name}] Response: {status_code} ({duration:.2f}s)")
    
    def log_error(self, api_name: str, error: Exception):
        """Log API error."""
        self.logger.error(f"[{api_name}] Error: {str(error)}", exc_info=True)


class DataLogger:
    """Logger for data operations."""
    
    def __init__(self):
        self.logger = logging.getLogger("data")
        self.logger.setLevel(LOG_LEVEL_INFO)
        
        # Data log file
        handler = RotatingFileHandler(
            f"{LOGS_DIR}/data.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_fetch(self, ticker: str, data_type: str, success: bool):
        """Log data fetch operation."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Fetch {data_type} for {ticker}: {status}")
    
    def log_cache_save(self, key: str, size: int):
        """Log cache save operation."""
        self.logger.debug(f"Cache SAVE: {key} ({size} bytes)")
    
    def log_cache_load(self, key: str):
        """Log cache load operation."""
        self.logger.debug(f"Cache LOAD: {key}")


# =============================================================================
# Global Logging Setup
# =============================================================================

# Initialize logging configuration
_logging_config = LoggingConfig()
_logging_config.setup_logging()

# Initialize specialized loggers
performance_logger = PerformanceLogger()
api_logger = APILogger()
data_logger = DataLogger()


# =============================================================================
# Utility Functions
# =============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str):
    """
    Set global log level.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(level)


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """
    Log exception with full traceback.
    
    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context about the error
    """
    msg = f"Exception: {str(exc)}"
    if context:
        msg = f"{context} - {msg}"
    logger.error(msg, exc_info=True)


def log_performance_metric(operation: str, duration: float, **kwargs):
    """
    Log performance metric.
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        **kwargs: Additional details
    """
    performance_logger.log_timing(operation, duration, kwargs)


def log_api_call(api_name: str, endpoint: str, status: int, duration: float):
    """
    Log API call.
    
    Args:
        api_name: Name of the API
        endpoint: API endpoint
        status: HTTP status code
        duration: Duration in seconds
    """
    api_logger.log_request(api_name, endpoint)
    api_logger.log_response(api_name, status, duration)


def get_log_files() -> dict[str, Path]:
    """
    Get paths to all log files.
    
    Returns:
        Dictionary mapping log type to file path
    """
    return {
        "main": Path(LOG_FILE),
        "error": Path(ERROR_LOG_FILE),
        "debug": Path(DEBUG_LOG_FILE),
        "performance": Path(f"{LOGS_DIR}/performance.log"),
        "api": Path(f"{LOGS_DIR}/api.log"),
        "data": Path(f"{LOGS_DIR}/data.log"),
    }


def clear_old_logs(days_to_keep: int = 7):
    """
    Clear log files older than specified days.
    
    Args:
        days_to_keep: Number of days of logs to keep
    """
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(days=days_to_keep)
    logs_path = Path(LOGS_DIR)
    
    for log_file in logs_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff.timestamp():
            try:
                log_file.unlink()
                logging.info(f"Deleted old log file: {log_file}")
            except Exception as e:
                logging.error(f"Failed to delete log file {log_file}: {e}")


# =============================================================================
# Context Managers
# =============================================================================

class log_execution:
    """Context manager for logging function execution."""
    
    def __init__(self, logger: logging.Logger, operation: str, log_args: bool = False):
        """
        Initialize context manager.
        
        Args:
            logger: Logger instance
            operation: Name of the operation
            log_args: Whether to log function arguments
        """
        self.logger = logger
        self.operation = operation
        self.log_args = log_args
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.debug(f"Completed: {self.operation} ({duration:.4f}s)")
            performance_logger.log_timing(self.operation, duration)
        else:
            self.logger.error(f"Failed: {self.operation} ({duration:.4f}s)", exc_info=True)
        
        return False  # Don't suppress exceptions
