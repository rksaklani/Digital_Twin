#!/usr/bin/env python3
"""
GPU warmup script.
Pre-allocates GPU memory and warms up models to reduce first-inference latency.
"""

import torch
import time
from pathlib import Path
import yaml


def load_config(config_path):
    """Load YAML configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def warmup_gpu():
    """Warm up GPU with dummy operations"""
    print("Warming up GPU...")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return False
    
    device = torch.device("cuda:0")
    
    # Allocate some memory
    print("  Allocating GPU memory...")
    dummy_tensors = []
    for i in range(5):
        tensor = torch.randn(1000, 1000, device=device)
        dummy_tensors.append(tensor)
    
    # Run some operations
    print("  Running warmup operations...")
    for _ in range(10):
        result = torch.matmul(dummy_tensors[0], dummy_tensors[1])
        torch.cuda.synchronize()
    
    # Clear
    del dummy_tensors
    torch.cuda.empty_cache()
    
    print("✅ GPU warmup complete")
    return True


def check_memory():
    """Check available GPU memory"""
    if not torch.cuda.is_available():
        return
    
    device = torch.device("cuda:0")
    total_memory = torch.cuda.get_device_properties(device).total_memory / 1e9
    allocated = torch.cuda.memory_allocated(device) / 1e9
    reserved = torch.cuda.memory_reserved(device) / 1e9
    free = total_memory - reserved
    
    print(f"\nGPU Memory Status:")
    print(f"  Total: {total_memory:.2f} GB")
    print(f"  Reserved: {reserved:.2f} GB")
    print(f"  Allocated: {allocated:.2f} GB")
    print(f"  Free: {free:.2f} GB")


def main():
    """Main warmup routine"""
    print("=" * 60)
    print("GPU Warmup")
    print("=" * 60)
    print()
    
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ CUDA not available. Cannot warm up GPU.")
        return 1
    
    # Load GPU config
    gpu_config_path = Path("configs/gpu.yaml")
    if gpu_config_path.exists():
        config = load_config(gpu_config_path)
        memory_fraction = config.get('memory_fraction', 0.9)
        print(f"Memory fraction: {memory_fraction}")
    else:
        print("⚠️  configs/gpu.yaml not found, using defaults")
    
    # Warmup
    if not warmup_gpu():
        return 1
    
    # Check memory
    check_memory()
    
    print("\n✅ Warmup complete")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

