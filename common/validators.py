from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def validate_image_size(image) -> None:
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"حجم تصویر نباید بیشتر از {MAX_IMAGE_SIZE_MB} مگابایت باشد."
        )


def validate_image_content(image) -> None:

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
