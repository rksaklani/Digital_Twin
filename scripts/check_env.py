#!/usr/bin/env python3
"""
Environment validation script.
Checks for required dependencies, GPU availability, and configuration.
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version >= 3.10"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False


def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA available: {device_count} device(s)")
            print(f"   Device 0: {device_name}")
            print(f"   CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("❌ CUDA not available")
            return False
    except ImportError:
        print("❌ PyTorch not installed")
        return False


def check_node():
    """Check Node.js installation"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ Node.js {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found")
        return False


def check_directories():
    """Check required directories exist"""
    required_dirs = [
        "apps/frontend",
        "apps/signaling",
        "services",
        "configs",
        "data",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist


def check_config_files():
    """Check configuration files exist"""
    config_files = [
        "configs/models.yaml",
        "configs/gpu.yaml",
        "configs/latency.yaml",
        "configs/webrtc.yaml",
    ]
    
    all_exist = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks"""
    print("=" * 60)
    print("Environment Check")
    print("=" * 60)
    print()
    
    checks = []
    
    print("Python Environment:")
    checks.append(check_python_version())
    print()
    
    print("Required Packages:")
    required_packages = [
        ("torch", "torch"),
        ("numpy", "numpy"),
        ("aiortc", "aiortc"),
        ("yaml", "yaml"),
        ("faster-whisper", "faster_whisper"),
    ]
    for package, import_name in required_packages:
        checks.append(check_package(package, import_name))
    print()
    
    print("CUDA/GPU:")
    checks.append(check_cuda())
    print()
    
    print("Node.js:")
    checks.append(check_node())
    print()
    
    print("Directory Structure:")
    checks.append(check_directories())
    print()
    
    print("Configuration Files:")
    checks.append(check_config_files())
    print()
    
    print("=" * 60)
    if all(checks):
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

