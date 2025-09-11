"""
ComfyUI S3 Storage Nodes
A comprehensive S3-compatible storage solution for ComfyUI using minio library.
Supports AWS S3, MinIO, DigitalOcean Spaces, Backblaze B2, and any S3-compatible storage.
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Metadata for ComfyUI Manager
WEB_DIRECTORY = "./web"
__version__ = "1.0.0"

# Node information
def get_extension_info():
    return {
        "name": "ComfyUI S3 Storage",
        "version": __version__,
        "description": "S3-compatible storage nodes with secure configuration management",
        "author": "mamorett",
        "license": "MIT",
        "reference": "https://github.com/mamorett/ComfyUI-S3",
    }
