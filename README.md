# ComfyUI S3 Storage Nodes

A comprehensive S3-compatible storage solution for ComfyUI that supports **any S3-compatible storage provider** including AWS S3, MinIO, DigitalOcean Spaces, Backblaze B2, and more.

## 🚀 Features

- **Universal S3 Compatibility** - Works with any S3-compatible storage using the minio library
- **Secure Configuration** - Credentials stored in local config file, not in workflows
- **Multiple Profiles** - Switch between different storage providers easily
- **Complete Image Support** - Save/load images with metadata preservation
- **Bucket Management** - Auto-create buckets, list objects, manage files
- **No Vendor Lock-in** - Use any S3-compatible provider

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "S3 Storage"
3. Install the node

### Method 2: Manual Installation
1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
```
Clone this repository:

bash


git clone https://github.com/your-repo/ComfyUI-S3-Storage.git
Install dependencies:

bash


cd ComfyUI-S3-Storage
pip install -r requirements.txt
Restart ComfyUI

⚙️ Configuration
}
Provider	Endpoint Example	Notes
DigitalOcean Spaces	nyc3.digitaloceanspaces.com	Replace region as needed
# ComfyUI S3 Storage Nodes

A comprehensive S3-compatible storage solution for ComfyUI that supports **any S3-compatible storage provider** including AWS S3, MinIO, DigitalOcean Spaces, Backblaze B2, and more.

## 🚀 Features

- **Universal S3 Compatibility** - Works with any S3-compatible storage using the minio library
- **Secure Configuration** - Credentials stored in local config file, not in workflows
- **Multiple Profiles** - Switch between different storage providers easily
- **Complete Image Support** - Save/load images with metadata preservation
- **Bucket Management** - Auto-create buckets, list objects, manage files
- **No Vendor Lock-in** - Use any S3-compatible provider

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "S3 Storage"
3. Install the node

### Method 2: Manual Installation
1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/ComfyUI-S3-Storage.git
   ```
3. Install dependencies:
   ```bash
   cd ComfyUI-S3-Storage
   pip install -r requirements.txt
   ```
4. Restart ComfyUI

## ⚙️ Configuration

### First Time Setup

1. Start ComfyUI - The node will auto-create a config file on first use
2. Find the config file - Located at `ComfyUI/custom_nodes/ComfyUI-S3-Storage/s3_config.json`
3. Edit credentials - Replace the placeholder values with your actual S3 credentials

#### Configuration File Structure

```json
{
    "profiles": {
        "aws_s3": {
            "name": "AWS S3",
            "endpoint": "s3.amazonaws.com",
            "access_key": "YOUR_AWS_ACCESS_KEY",
            "secret_key": "YOUR_AWS_SECRET_KEY",
            "secure": true,
            "region": "us-east-1"
        },
        "minio_local": {
            "name": "Local MinIO",
            "endpoint": "localhost:9000",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "secure": false,
            "region": "us-east-1"
        }
    }
}
```

## Supported Storage Providers

| Provider            | Endpoint Example                       | Notes                              |
|---------------------|----------------------------------------|------------------------------------|
| AWS S3              | s3.amazonaws.com                       | Standard AWS S3                    |
| MinIO               | localhost:9000                         | Self-hosted or cloud MinIO         |
| DigitalOcean Spaces | nyc3.digitaloceanspaces.com            | Replace region as needed           |
| Backblaze B2        | s3.us-west-004.backblazeb2.com         | Use S3-compatible API              |
| Wasabi              | s3.wasabisys.com                       | High-performance cloud storage     |
| Cloudflare R2       | <account-id>.r2.cloudflarestorage.com  | Cloudflare's S3-compatible storage |

## 🎯 Available Nodes

### 💾 Save Image to S3
* **Purpose:** Save generated images to S3 storage
* **Inputs:** Images, profile, bucket, prefix, filename prefix
* **Outputs:** JSON with URLs and metadata
* **Features:** Automatic timestamping, metadata preservation, batch processing

### 📁 Load Image from S3
* **Purpose:** Load images from S3 storage
* **Inputs:** Profile, bucket, object key
* **Outputs:** Image tensor and mask
* **Features:** Automatic format detection, alpha channel extraction

### 📋 List S3 Objects
* **Purpose:** Browse and list objects in S3 buckets
* **Inputs:** Profile, bucket, optional prefix filter
* **Outputs:** JSON list of objects with metadata
* **Features:** Prefix filtering, size limits, metadata display

### ⚙️ S3 Config Info
* **Purpose:** Display configuration status and help
* **Inputs:** Optional refresh trigger
* **Outputs:** Configuration information and setup instructions
* **Features:** Profile validation, setup guidance

## 🔧 Usage Examples

### Basic Image Save Workflow
1. Add "Save Image to S3" node
2. Select your configured profile (e.g., "aws_s3")
3. Enter bucket name
4. Set prefix (e.g., "my-art/")
5. Connect your image output
6. Run workflow

### Loading Saved Images
1. Add "Load Image from S3" node
2. Select same profile
3. Enter bucket name
4. Enter full object key (e.g., "my-art/image_20231201_143022_0001.png")
5. Connect to your image processing nodes

### Browsing Your Storage
1. Add "List S3 Objects" node
2. Select profile and bucket
3. Optionally set prefix filter
4. View JSON output to see all your stored files

## 🛡️ Security Features
- No credentials in workflows - All sensitive data stays in local config file
- Profile-based access - Easy switching between different storage accounts
- Validation checks - Warns about misconfigured profiles
- Local config only - Credentials never leave your machine

## 🐛 Troubleshooting

### Common Issues

**"Profile not found" error**
- Check that `s3_config.json` exists in the node directory
- Verify profile names match exactly (case-sensitive)

**"Invalid credentials" error**
- Ensure `access_key` and `secret_key` don't start with "YOUR_"
- Verify credentials are correct for your storage provider
- Check endpoint URL format (no `https://` prefix usually)

**"Bucket not found" error**
- Verify bucket name is correct
- Check that your credentials have access to the bucket
- Some providers auto-create buckets, others require manual creation

**Connection timeout**
- Verify endpoint URL is correct
- Check if you need `secure: false` for local/development setups
- Ensure firewall allows connections to your storage provider

### Getting Help
- Use the "S3 Config Info" node to check your configuration
- Check ComfyUI console for detailed error messages
- Verify your storage provider's S3 API documentation
- Test with a simple MinIO local setup first

## 📝 Example Configurations

### Complete Config File Structure

The `s3_config.json` file must have this structure:

```json
{
    "profiles": {
        "profile_name_here": {
            "name": "Display Name",
            "endpoint": "...",
            "access_key": "...",
            "secret_key": "...",
            "secure": true,
            "region": "..."
        }
    },
    "default_profile": "profile_name_here"
}
```


### AWS S3
```json
{
    "profiles": {
        "aws_production": {
            "name": "AWS S3 Production",
            "endpoint": "s3.amazonaws.com",
            "access_key": "AKIA...",
            "secret_key": "...",
            "secure": true,
            "region": "us-west-2"
        }
    },
    "default_profile": "aws_production"
}

```

### Local MinIO Development
```json
{
    "profiles": {
        "minio_local": {
            "name": "Local Development",
            "endpoint": "localhost:9000", 
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "secure": false,
            "region": "us-east-1"
        }
    },
    "default_profile": "minio_local"
}

```

### Multiple profiles
```json
{
    "profiles": {
        "aws_s3": {
            "name": "AWS S3 Production",
            "endpoint": "s3.amazonaws.com",
            "access_key": "AKIA...",
            "secret_key": "...",
            "secure": true,
            "region": "us-west-2"
        },
        "minio_dev": {
            "name": "Local Development",
            "endpoint": "localhost:9000",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "secure": false,
            "region": "us-east-1"
        },
        "digitalocean": {
            "name": "DigitalOcean NYC",
            "endpoint": "nyc3.digitaloceanspaces.com",
            "access_key": "DO_ACCESS_KEY",
            "secret_key": "DO_SECRET_KEY",
            "secure": true,
            "region": "nyc3"
        }
    },
    "default_profile": "aws_s3"
}

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built on the excellent minio-py library  
Inspired by the ComfyUI community's need for reliable cloud storage  
Thanks to all contributors and testers

---

## `examples/example_workflow.json`

```json
{
  "last_node_id": 4,
  "last_link_id": 4,
  "nodes": [
    {
      "id": 1,
      "type": "SaveImageToS3",
      "pos": [400, 200],
      "size": [320, 280],
      "flags": {},
      "order": 2,
      "mode": 0,
      "inputs": [
        {
          "name": "images",
          "type": "IMAGE",
          "link": 1
        }
      ],
      "outputs": [
        {
          "name": "result",
          "type": "STRING",
          "links": [2],
          "shape": 3
        }
      ],
      "properties": {
        "Node name for S&R": "SaveImageToS3"
      },
      "widgets_values": [
        "aws_s3",
        "my-comfyui-bucket",
        "generated-images/",
        "artwork"
      ]
    },
    {
      "id": 2,
      "type": "S3ConfigInfo", 
      "pos": [50, 50],
      "size": [300, 200],
      "flags": {},
      "order": 0,
      "mode": 0,
      "outputs": [
        {
          "name": "config_info",
          "type": "STRING",
          "links": [3],
          "shape": 3
        }
      ],
      "properties": {
        "Node name for S&R": "S3ConfigInfo"
      },
      "widgets_values": [false]
    }
  ],
  "links": [
    [1, 0, 0, 1, 0, "IMAGE"],
    [2, 1, 0, 3, 0, "STRING"],
    [3, 2, 0, 4, 0, "STRING"]
  ],
  "groups": [],
  "config": {},
  "extra": {},
  "version": 0.4
}
```
