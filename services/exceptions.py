class AppError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

class DataConnectionError(AppError):
    """Raised when there are issues connecting to the data source."""
    pass

class DataPermissionError(AppError):
    """Raised when there are permission issues (e.g., 403 Forbidden)."""
    pass

class DataNotFoundError(AppError):
    """Raised when the requested data (spreadsheet/worksheet) is not found."""
    pass

class DataValidationError(AppError):
    """Raised when the data does not conform to the expected contract."""
    pass
