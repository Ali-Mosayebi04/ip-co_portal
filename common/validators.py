"""Small, dependency-free helpers shared across apps.

This is a plain Python package, not a Django app — it holds no models,
so it never needs to appear in ``INSTALLED_APPS`` or own migrations.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def validate_image_size(image) -> None:
    """Reject uploaded images larger than ``MAX_IMAGE_SIZE_MB``."""
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"حجم تصویر نباید بیشتر از {MAX_IMAGE_SIZE_MB} مگابایت باشد."
        )


def validate_image_content(image) -> None:
    """Verify the uploaded file is a genuine, decodable image.

    The extension whitelist alone can be defeated by renaming an
    arbitrary file to ``.jpg``. Asking Pillow to actually decode the
    file closes that gap without adding a runtime dependency, since
    Pillow is already required for ``ImageField``.
    """
    from PIL import Image, UnidentifiedImageError

    try:
        image.seek(0)
        with Image.open(image) as opened:
            opened.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("فایل انتخاب‌شده یک تصویر معتبر نیست.")
    finally:
        image.seek(0)


IMAGE_VALIDATORS = [
    validate_image_size,
    validate_image_content,
    FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
]
