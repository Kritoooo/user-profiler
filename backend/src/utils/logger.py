import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        colored_level = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Create formatted message
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Add context info if available
        context = ""
        if hasattr(record, 'user_id'):
            context += f"[user:{record.user_id}] "
        if hasattr(record, 'platform'):
            context += f"[{record.platform}] "
        if hasattr(record, 'operation'):
            context += f"[{record.operation}] "
            
        return f"{timestamp} | {colored_level:20} | {context}{record.getMessage()}"

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add custom fields
        for attr in ['user_id', 'platform', 'operation', 'url', 'duration']:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
                
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """Setup application logging with both console and file handlers"""
    
    # Create logs directory
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("user_profiler")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColorFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger() -> logging.Logger:
    """Get the application logger"""
    return logging.getLogger("user_profiler")

class LogContext:
    """Context manager for adding structured logging context"""
    
    def __init__(self, **context):
        self.context = context
        self.logger = get_logger()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def info(self, message: str, **extra):
        self._log(logging.INFO, message, extra)
        
    def debug(self, message: str, **extra):
        self._log(logging.DEBUG, message, extra)
        
    def warning(self, message: str, **extra):
        self._log(logging.WARNING, message, extra)
        
    def error(self, message: str, **extra):
        self._log(logging.ERROR, message, extra)
        
    def _log(self, level: int, message: str, extra: dict):
        # Combine context and extra data
        combined_extra = {**self.context, **extra}
        
        # Create log record with extra data
        record = self.logger.makeRecord(
            self.logger.name, level, __file__, 0, message, (), None
        )
        
        # Add extra attributes to record
        for key, value in combined_extra.items():
            setattr(record, key, value)
            
        self.logger.handle(record)