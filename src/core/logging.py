"""
Logging Module
Centralized logging with structured output and performance tracking
"""
import logging
import functools
import time
from pathlib import Path
from typing import Any, Callable
from datetime import datetime

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure loggers
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup a logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_file = LOG_DIR / f"{name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Application loggers
app_logger = setup_logger("app")
data_logger = setup_logger("data")
analysis_logger = setup_logger("analysis")
cache_logger = setup_logger("cache")
error_logger = setup_logger("error", level="ERROR")


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper


def log_cache_operation(operation: str):
    """Decorator to log cache operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_logger.debug(f"Cache {operation}: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                cache_logger.debug(f"Cache {operation} successful: {func.__name__}")
                return result
            except Exception as e:
                cache_logger.error(f"Cache {operation} failed: {func.__name__} - {e}")
                raise
        return wrapper
    return decorator


def log_data_fetch(source: str):
    """Decorator to log data fetching operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ticker = kwargs.get('ticker', args[0] if args else 'unknown')
            data_logger.info(f"Fetching {source} data for {ticker}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                data_logger.info(f"Successfully fetched {source} data for {ticker} in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                data_logger.error(f"Failed to fetch {source} data for {ticker} after {execution_time:.2f}s: {e}")
                raise
        return wrapper
    return decorator


def log_analysis(analysis_type: str):
    """Decorator to log analysis operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            analysis_logger.info(f"Starting {analysis_type} analysis")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                analysis_logger.info(f"{analysis_type} analysis completed in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                analysis_logger.error(f"{analysis_type} analysis failed after {execution_time:.2f}s: {e}")
                raise
        return wrapper
    return decorator


def log_error(error: Exception, context: str = ""):
    """Log detailed error information"""
    error_logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}", exc_info=True)


class PerformanceTracker:
    """Track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = setup_logger("performance")
    
    def start(self, operation: str):
        """Start tracking an operation"""
        self.metrics[operation] = {
            "start": time.time(),
            "end": None,
            "duration": None
        }
    
    def end(self, operation: str):
        """End tracking an operation"""
        if operation in self.metrics:
            self.metrics[operation]["end"] = time.time()
            self.metrics[operation]["duration"] = (
                self.metrics[operation]["end"] - self.metrics[operation]["start"]
            )
            self.logger.info(f"{operation}: {self.metrics[operation]['duration']:.3f}s")
    
    def get_metrics(self) -> dict:
        """Get all tracked metrics"""
        return self.metrics
    
    def reset(self):
        """Reset all metrics"""
        self.metrics = {}


# Global performance tracker
perf_tracker = PerformanceTracker()


def log_app_start():
    """Log application start"""
    app_logger.info("=" * 50)
    app_logger.info("StocksV2 Dashboard Starting")
    app_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    app_logger.info("=" * 50)


def log_app_stop():
    """Log application stop"""
    app_logger.info("=" * 50)
    app_logger.info("StocksV2 Dashboard Stopped")
    app_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    app_logger.info("=" * 50)


# Export commonly used loggers
__all__ = [
    'setup_logger',
    'app_logger',
    'data_logger',
    'analysis_logger',
    'cache_logger',
    'error_logger',
    'log_execution_time',
    'log_cache_operation',
    'log_data_fetch',
    'log_analysis',
    'log_error',
    'PerformanceTracker',
    'perf_tracker',
    'log_app_start',
    'log_app_stop',
]
