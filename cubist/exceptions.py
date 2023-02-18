class _Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CubistError(_Error):
    """Raised when the C Cubist library raises errors"""
    pass
