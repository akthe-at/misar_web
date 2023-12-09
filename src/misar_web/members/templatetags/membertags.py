from django import template

register = template.Library()


def filesize(value):
    """Calculate uploaded file size if between KB and GB in size."""
    if value < 512_000:
        value = value / 1024.0
        ext = "KB"
    elif value < 4_194_304_000:
        value = value / 1_048_576.0
        ext = "MB"
    else:
        value = value / 107_341_824.0
        ext = "GB"
    return f"{value:.2f} {ext}"


register.filter("filesize", filesize)


def extension(file: str) -> str:
    """return the file extension"""
    return file.split(".")[-1]


register.filter("extension", extension)

