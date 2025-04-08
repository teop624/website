import logging
import uuid
from logging.handlers import RotatingFileHandler
import os
from flask import g

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        # Get request ID from Flask's g object or generate a new one
        if not hasattr(g, 'request_id'):
            g.request_id = str(uuid.uuid4())
        record.request_id = g.request_id
        return True

def setup_logger(app):
    # Configure logging
    app.logger.setLevel(logging.DEBUG)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - [%(username)s] - %(message)s'
    )
    
    # Add filter to handlers
    request_id_filter = RequestIDFilter()
    console_handler.addFilter(request_id_filter)
    file_handler.addFilter(request_id_filter)
    
    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Add username to log records
    class UsernameFilter(logging.Filter):
        def filter(self, record):
            from flask import session
            record.username = session.get('username', 'anonymous')
            return True
    
    username_filter = UsernameFilter()
    app.logger.addFilter(username_filter)
    
    return app.logger

def get_session_id():
    """Generate a new session ID"""
    return str(uuid.uuid4())

def log_with_session(func):
    """Decorator to add session ID to logging"""
    def wrapper(*args, **kwargs):
        session_id = get_session_id()
        extra = {'session_id': session_id}
        logger.info(f"Starting {func.__name__}", extra=extra)
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}", extra=extra)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", extra=extra)
            raise
    return wrapper 