class FlirExtractorError(Exception):
    """Base exception for the flirextractor library"""
    pass

class UnsupportedImageError(FlirExtractorError):
    """Thrown when the input image is not supported by this program.
    """
    pass
