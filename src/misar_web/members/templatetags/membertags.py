from django import template
from pathlib import Path

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


def get_file_name(filepath: str) -> str:
    """Gets the name of the file from the path for displaying in the file directory"""
    file_name = Path(filepath).name
    return file_name


register.filter("file_name", get_file_name)
