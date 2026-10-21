"""Data layer exceptions."""


class DataValidationError(ValueError):
    """Raised when incoming data cannot be normalized or validated."""


class DataQualityError(ValueError):
    """Raised when validated data fails deterministic quality constraints."""
