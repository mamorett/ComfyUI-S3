"""
Generic S3 Storage Node for ComfyUI with JSON Configuration
Uses minio library for compatibility with any S3-compatible storage
Credentials loaded from config file for security
"""

import io
import json
import numpy as np
import torch
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
import tempfile
import os
from pathlib import Path

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    print("Warning: minio library not installed. Install with: pip install minio")

# Get the directory where this node file is located
NODE_DIR = Path(__file__).parent
CONFIG_FILE = NODE_DIR / "s3_config.json"

class S3ConfigManager:
    """Manages S3 configuration from JSON file"""
    
    @staticmethod
    def get_config_path():
        """Get the path to the config file"""
        return CONFIG_FILE
    
    @staticmethod
    def load_config():
        """Load S3 configuration from JSON file"""
        if not CONFIG_FILE.exists():
            S3ConfigManager.create_default_config()
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            raise ValueError(f"Failed to load S3 config from {CONFIG_FILE}: {str(e)}")
    
    @staticmethod
    def create_default_config():
        """Create default configuration file"""
        default_config = {
            "profiles": {
                "aws_s3": {
                    "name": "AWS S3",
                    "endpoint": "s3.amazonaws.com",
                    "access_key": "YOUR_AWS_ACCESS_KEY",
                    "secret_key": "YOUR_AWS_SECRET_KEY",
                    "secure": True,
                    "region": "us-east-1"
                },
                "minio_local": {
                    "name": "Local MinIO",
                    "endpoint": "localhost:9000",
                    "access_key": "minioadmin",
                    "secret_key": "minioadmin",
                    "secure": False,
                    "region": "us-east-1"
                },
                "digitalocean": {
                    "name": "DigitalOcean Spaces",
                    "endpoint": "nyc3.digitaloceanspaces.com",
                    "access_key": "YOUR_DO_ACCESS_KEY",
                    "secret_key": "YOUR_DO_SECRET_KEY",
                    "secure": True,
                    "region": "nyc3"
                },
                "backblaze": {
                    "name": "Backblaze B2",
                    "endpoint": "s3.us-west-004.backblazeb2.com",
                    "access_key": "YOUR_B2_KEY_ID",
                    "secret_key": "YOUR_B2_APPLICATION_KEY",
                    "secure": True,
                    "region": "us-west-004"
                }
            },
            "default_profile": "aws_s3"
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            print(f"✅ Created default S3 config at: {CONFIG_FILE}")
            print("📝 Please edit this file with your S3 credentials!")
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
    
    @staticmethod
    def get_profile_names():
        """Get list of available profile names"""
        try:
            config = S3ConfigManager.load_config()
            return list(config.get("profiles", {}).keys())
        except:
            return ["default"]
    
    @staticmethod
    def get_profile(profile_name):
        """Get specific profile configuration"""
        config = S3ConfigManager.load_config()
        profiles = config.get("profiles", {})
        
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' not found in config. Available: {list(profiles.keys())}")
        
        profile = profiles[profile_name]
        
        # Validate required fields
        required_fields = ["endpoint", "access_key", "secret_key"]
        for field in required_fields:
            if not profile.get(field) or profile[field].startswith("YOUR_"):
                raise ValueError(f"Profile '{profile_name}' has invalid {field}. Please update {CONFIG_FILE}")
        
        return profile

class S3Client:
    """S3 Client wrapper using minio"""
    
    @staticmethod
    def create_from_profile(profile_name):
        """Create S3 client from profile configuration"""
        if not MINIO_AVAILABLE:
            raise ImportError("minio library is required. Install with: pip install minio")
        
        profile = S3ConfigManager.get_profile(profile_name)
        
        endpoint = profile["endpoint"]
        # Remove protocol from endpoint if present
        if endpoint.startswith('https://'):
            endpoint = endpoint[8:]
            secure = True
        elif endpoint.startswith('http://'):
            endpoint = endpoint[7:]
            secure = False
        else:
            secure = profile.get("secure", True)
            
        return Minio(
            endpoint=endpoint,
            access_key=profile["access_key"],
            secret_key=profile["secret_key"],
            secure=secure
        ), profile

class SaveImageToS3:
    """Save images to any S3-compatible storage using profile from config file"""
    
    def __init__(self):
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        profiles = S3ConfigManager.get_profile_names()
        
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Images to be saved"}),
                "profile": (profiles, {"default": profiles[0] if profiles else "default", "tooltip": "S3 profile from config file"}),
                "bucket": ("STRING", {"default": "", "tooltip": "S3 bucket name"}),
                "prefix": ("STRING", {"default": "comfyui/", "tooltip": "Object key prefix"}),
                "filename_prefix": ("STRING", {"default": "image", "tooltip": "Filename prefix"}),
            },
            "optional": {
                "custom_region": ("STRING", {"default": "", "tooltip": "Override region from profile (optional)"}),
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "s3_storage"
    DESCRIPTION = "Save images to S3-compatible storage using config profiles"

    def save_images(self, images, profile, bucket, prefix="comfyui/", 
                   filename_prefix="image", custom_region="", prompt=None, extra_pnginfo=None):
        """Save images to S3 storage"""
        
        if not bucket:
            raise ValueError("Bucket name is required")
        
        try:
            client, profile_config = S3Client.create_from_profile(profile)
            region = custom_region or profile_config.get("region", "us-east-1")
            
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket, location=region)
            
            results = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for batch_number, image in enumerate(images):
                i = 255. * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                
                filename = f"{filename_prefix}_{timestamp}_{batch_number:04d}.png"
                object_key = f"{prefix.rstrip('/')}/{filename}"
                
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG', pnginfo=metadata, compress_level=self.compress_level)
                img_buffer.seek(0)
                
                client.put_object(
                    bucket_name=bucket,
                    object_name=object_key,
                    data=img_buffer,
                    length=len(img_buffer.getvalue()),
                    content_type='image/png'
                )
                
                endpoint = profile_config["endpoint"]
                secure = profile_config.get("secure", True)
                protocol = "https" if secure else "http"
                if not endpoint.startswith(('http://', 'https://')):
                    url = f"{protocol}://{endpoint}/{bucket}/{object_key}"
                else:
                    url = f"{endpoint}/{bucket}/{object_key}"
                
                results.append({
                    "filename": filename,
                    "object_key": object_key,
                    "url": url,
                    "bucket": bucket,
                    "profile": profile,
                    "timestamp": timestamp,
                    "batch_number": batch_number
                })
            
            return (json.dumps(results, indent=2),)
            
        except S3Error as e:
            raise ValueError(f"S3 Error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to save images: {str(e)}")

class LoadImageFromS3:
    """Load images from any S3-compatible storage using profile from config file"""

    @classmethod  
    def INPUT_TYPES(cls):
        profiles = S3ConfigManager.get_profile_names()
        
        return {
            "required": {
                "profile": (profiles, {"default": profiles[0] if profiles else "default", "tooltip": "S3 profile from config file"}),
                "bucket": ("STRING", {"default": "", "tooltip": "S3 bucket name"}),
                "object_key": ("STRING", {"default": "", "tooltip": "S3 object key (full path)"}),
            }
        }

    CATEGORY = "s3_storage"
    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    DESCRIPTION = "Load images from S3-compatible storage using config profiles"

    def load_image(self, profile, bucket, object_key):
        """Load image from S3 storage"""
        
        if not bucket or not object_key:
            raise ValueError("Bucket and object key are required")
        
        try:
            client, profile_config = S3Client.create_from_profile(profile)
            
            response = client.get_object(bucket, object_key)
            image_data = response.read()
            response.close()
            response.release_conn()
            
            img = Image.open(io.BytesIO(image_data))
            img = ImageOps.exif_transpose(img)
            
            if img.mode == 'I':
                img = img.point(lambda i: i * (1 / 255))
            
            if 'A' in img.getbands():
                mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((img.height, img.width), dtype=torch.float32)
            
            image = img.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            return (image, mask.unsqueeze(0))
            
        except S3Error as e:
            raise ValueError(f"S3 Error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")

class ListS3Objects:
    """List objects in S3 bucket using profile from config file"""

    @classmethod
    def INPUT_TYPES(cls):
        profiles = S3ConfigManager.get_profile_names()
        
        return {
            "required": {
                "profile": (profiles, {"default": profiles[0] if profiles else "default"}),
                "bucket": ("STRING", {"default": ""}),
            },
            "optional": {
                "prefix": ("STRING", {"default": "", "tooltip": "Filter objects by prefix"}),
                "max_objects": ("INT", {"default": 100, "min": 1, "max": 1000, "tooltip": "Maximum objects to return"}),
            }
        }

    CATEGORY = "s3_storage"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("objects_list",)
    FUNCTION = "list_objects"
    DESCRIPTION = "List objects in S3 bucket using config profiles"

    def list_objects(self, profile, bucket, prefix="", max_objects=100):
        """List objects in S3 bucket"""
        
        if not bucket:
            raise ValueError("Bucket name is required")
        
        try:
            client, profile_config = S3Client.create_from_profile(profile)
            
            objects = client.list_objects(bucket, prefix=prefix, recursive=True)
            
            results = []
            count = 0
            for obj in objects:
                if count >= max_objects:
                    break
                    
                results.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag
                })
                count += 1
            
            return (json.dumps(results, indent=2),)
            
        except S3Error as e:
            raise ValueError(f"S3 Error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to list objects: {str(e)}")

class S3ConfigInfo:
    """Display S3 configuration information and help create config file"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "refresh": ("BOOLEAN", {"default": False, "tooltip": "Refresh config info"}),
            }
        }

    CATEGORY = "s3_storage"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("config_info",)
    FUNCTION = "get_config_info"
    DESCRIPTION = "Display S3 configuration file information"

    def get_config_info(self, refresh=False):
        """Get configuration file information"""
        
        config_path = S3ConfigManager.get_config_path()
        
        info = {
            "config_file_path": str(config_path),
            "config_exists": config_path.exists(),
            "profiles": [],
            "instructions": []
        }
        
        if config_path.exists():
            try:
                config = S3ConfigManager.load_config()
                profiles = config.get("profiles", {})
                
                for profile_name, profile_data in profiles.items():
                    profile_info = {
                        "name": profile_name,
                        "display_name": profile_data.get("name", profile_name),
                        "endpoint": profile_data.get("endpoint", ""),
                        "configured": not (
                            profile_data.get("access_key", "").startswith("YOUR_") or
                            profile_data.get("secret_key", "").startswith("YOUR_")
                        )
                    }
                    info["profiles"].append(profile_info)
                
                info["instructions"] = [
                    f"Config file found at: {config_path}",
                    f"Found {len(profiles)} profile(s)",
                    "Edit the config file to add your S3 credentials",
                    "Replace 'YOUR_*' placeholders with actual values"
                ]
                
            except Exception as e:
                info["instructions"] = [
                    f"Config file exists but has errors: {str(e)}",
                    "Please check the JSON syntax"
                ]
        else:
            info["instructions"] = [
                f"Config file not found at: {config_path}",
                "A default config will be created on first use",
                "Edit the generated file with your S3 credentials"
            ]
        
        return (json.dumps(info, indent=2),)

# Node registration
NODE_CLASS_MAPPINGS = {
    "SaveImageToS3": SaveImageToS3,
    "LoadImageFromS3": LoadImageFromS3,
    "ListS3Objects": ListS3Objects,
    "S3ConfigInfo": S3ConfigInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageToS3": "💾 Save Image to S3",
    "LoadImageFromS3": "📁 Load Image from S3", 
    "ListS3Objects": "📋 List S3 Objects",
    "S3ConfigInfo": "⚙️ S3 Config Info",
}
