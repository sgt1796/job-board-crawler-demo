"""
Helpers for the application submission step.

These functions provide hooks for integrating with external systems such as
application forms, file uploads and screenshots.  In this demo they simply
print messages.  In a production environment you would replace them with
real implementations or delegate to a separate service.
"""

from .form_filler import fill_form
from .upload import upload_resume, upload_cover_letter
from .screenshot import take_screenshot
from .confirm import request_confirmation

__all__ = [
    "fill_form",
    "upload_resume",
    "upload_cover_letter",
    "take_screenshot",
    "request_confirmation",
]