"""
ComfyUI S3 Storage Nodes
A comprehensive S3-compatible storage solution for ComfyUI using minio library.
Supports AWS S3, MinIO, DigitalOcean Spaces, Backblaze B2, and any S3-compatible storage.
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Metadata
__version__ = "1.0.0"
__author__ = "mamorett"
__description__ = "S3-compatible storage nodes for ComfyUI with secure configuration management"
