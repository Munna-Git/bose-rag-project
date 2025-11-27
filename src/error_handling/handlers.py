"""
Comprehensive error handling with recovery strategies
"""
from typing import Optional, Callable
from config.constants import ErrorType, ERROR_MESSAGES
from src.error_handling.logger import logger
import traceback


class ErrorHandler:
    """Handle errors gracefully with fallback strategies"""
    
    def __init__(self):
        self.error_count = 0
        self.error_log = []
    
    def handle_error(self,
                     error_type: ErrorType,
                     error: Exception,
                     context: dict = None,
                     fallback_fn: Optional[Callable] = None):
        """
        Handle error with fallback strategy
        
        Args:
            error_type: Type of error
            error: Exception object
            context: Additional context
            fallback_fn: Fallback function to call
        """
        
        self.error_count += 1
        context = context or {}
        
        # Log error
        error_msg = ERROR_MESSAGES.get(
            error_type,
            f"Unknown error: {str(error)}"
        )
        
        logger.warning(
            f"Error #{self.error_count}: {error_type.value}\n"
            f"Message: {error_msg}\n"
            f"Context: {context}\n"
            f"Details: {str(error)}"
        )
        
        # Store error log
        self.error_log.append({
            'count': self.error_count,
            'type': error_type.value,
            'message': error_msg,
            'context': context,
            'error': str(error),
            'traceback': traceback.format_exc()
        })
        
        # Execute fallback
        if fallback_fn:
            try:
                logger.info(f"Executing fallback for {error_type.value}")
                return fallback_fn()
            except Exception as fallback_error:
                logger.error(f"Fallback failed: {str(fallback_error)}")
                return None
        
        return None
    
    def get_error_summary(self) -> dict:
        """Get error summary"""
        return {
            'total_errors': self.error_count,
            'errors': self.error_log
        }


# Global error handler
error_handler = ErrorHandler()
