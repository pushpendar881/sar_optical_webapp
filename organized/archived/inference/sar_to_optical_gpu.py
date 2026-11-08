"""
GPU-optimized SAR -> Optical inference using the trained Seg-CycleGAN G_AB generator.
This version prefers GPU but falls back to CPU if CUDA is unavailable.

Usage:
    python sar_to_optical_gpu.py --sar path/to/sar.png \
        --checkpoint path/to/checkpoint.pth \
        --output out.png
"""
import argparse
import sys
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

try:
    import numpy as np
    import torch
    import torch.nn as nn
    from PIL import Image
    
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install torch torchvision pillow numpy")
    sys.exit(1)

class ResnetBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1), nn.Conv2d(dim, dim, 3), nn.InstanceNorm2d(dim), nn.ReLU(True),
            nn.ReflectionPad2d(1), nn.Conv2d(dim, dim, 3), nn.InstanceNorm2d(dim),
        )

    def forward(self, x):
        return x + self.block(x)


class ResnetGenerator(nn.Module):
    """Must match training-notebook architecture exactly (in_ch=1, out_ch=3, ngf=64, n_blocks=9)."""
    def __init__(self, in_ch=1, out_ch=3, ngf=64, n_blocks=9):
        super().__init__()
        model = [nn.ReflectionPad2d(3), nn.Conv2d(in_ch, ngf, 7), nn.InstanceNorm2d(ngf), nn.ReLU(True)]
        n_down = 2
        for i in range(n_down):
            mult = 2 ** i
            model += [nn.Conv2d(ngf * mult, ngf * mult * 2, 3, stride=2, padding=1),
                      nn.InstanceNorm2d(ngf * mult * 2), nn.ReLU(True)]
        mult = 2 ** n_down
        for _ in range(n_blocks):
            model += [ResnetBlock(ngf * mult)]
        for i in range(n_down):
            mult = 2 ** (n_down - i)
            model += [nn.ConvTranspose2d(ngf * mult, int(ngf * mult / 2), 3, stride=2, padding=1, output_padding=1),
                      nn.InstanceNorm2d(int(ngf * mult / 2)), nn.ReLU(True)]
        model += [nn.ReflectionPad2d(3), nn.Conv2d(ngf, out_ch, 7), nn.Tanh()]
        self.model = nn.Sequential(*model)

    def forward(self, x):
        return self.model(x)


def get_device():
    """Smart device selection with fallback"""
    if torch.cuda.is_available():
        device = 'cuda'
        gpu_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🔥 Using GPU: {gpu_name} ({memory_gb:.1f}GB)")
    else:
        device = 'cpu'
        print("💻 Using CPU (GPU not available)")
    return device


def load_generator(checkpoint_path, device):
    """Load generator model with robust error handling"""
    try:
        print(f"Loading checkpoint from: {checkpoint_path}")
        G_AB = ResnetGenerator(in_ch=1, out_ch=3, ngf=64, n_blocks=9).to(device)
        
        # Load checkpoint
        ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(ckpt, dict) and "G_AB" in ckpt:
            state_dict = ckpt["G_AB"]
        elif isinstance(ckpt, dict) and "state_dict" in ckpt:
            state_dict = ckpt["state_dict"]
        else:
            state_dict = ckpt
        
        G_AB.load_state_dict(state_dict)
        G_AB.eval()
        
        print(f"✅ Model loaded successfully on {device.upper()}")
        return G_AB
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        if device == 'cuda':
            print("⚠️  Trying CPU fallback...")
            return load_generator(checkpoint_path, 'cpu')
        raise


@torch.no_grad()
def sar_to_optical(G_AB, sar_path, img_size, device):
    """Convert SAR image to optical with performance monitoring"""
    import time
    
    try:
        start_time = time.time()
        
        # Load and preprocess image
        print(f"Processing image: {sar_path}")
        sar_img = Image.open(sar_path).convert("L").resize((img_size, img_size), Image.Resampling.LANCZOS)
        
        # Convert to tensor
        sar_array = np.array(sar_img, dtype=np.float32) / 127.5 - 1.0
        sar_t = torch.from_numpy(sar_array).unsqueeze(0).unsqueeze(0).to(device)  # [1, 1, H, W]
        
        print("Running inference...")
        inference_start = time.time()
        
        # Forward pass
        fake_t = G_AB(sar_t)[0].permute(1, 2, 0).cpu().numpy()
        
        inference_time = time.time() - inference_start
        
        # Post-process
        fake_np = ((fake_t + 1) * 127.5).clip(0, 255).astype(np.uint8)
        result_img = Image.fromarray(fake_np)
        
        total_time = time.time() - start_time
        
        print(f"✅ Inference completed successfully")
        print(f"⚡ Inference time: {inference_time*1000:.1f}ms")
        print(f"⏱️  Total time: {total_time*1000:.1f}ms")
        
        if device == 'cuda':
            memory_used = torch.cuda.max_memory_allocated() / (1024**3)
            print(f"💾 Peak GPU memory: {memory_used:.3f}GB")
            torch.cuda.reset_peak_memory_stats()
        
        return result_img
        
    except Exception as e:
        print(f"❌ Error during inference: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="SAR -> Optical colorization inference (GPU optimized)")
    parser.add_argument("--sar", required=True, help="Path to input SAR image")
    parser.add_argument("--checkpoint", required=True, help="Path to G_AB checkpoint (.pth)")
    parser.add_argument("--output", default="optical_output.png", help="Path to save the generated optical image")
    parser.add_argument("--img-size", type=int, default=256, help="Image size for processing (default 256)")
    parser.add_argument("--device", choices=['cpu', 'cuda', 'auto'], default='auto', 
                       help="Device to use: cpu, cuda, or auto (default: auto)")
    args = parser.parse_args()

    print("🛰️ SAR to Optical Conversion (GPU Optimized)")
    print("=" * 50)
    
    # Validate inputs
    sar_path = Path(args.sar)
    if not sar_path.exists():
        print(f"❌ SAR image not found: {sar_path}")
        sys.exit(1)
    
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        sys.exit(1)
    
    try:
        # Determine device
        if args.device == 'auto':
            device = get_device()
        else:
            device = args.device
            if device == 'cuda' and not torch.cuda.is_available():
                print("⚠️  CUDA requested but not available, falling back to CPU")
                device = 'cpu'
        
        # Load model
        G_AB = load_generator(checkpoint_path, device)
        
        # Run inference
        result_img = sar_to_optical(G_AB, sar_path, args.img_size, device)
        
        # Save result
        output_path = Path(args.output)
        result_img.save(output_path, quality=95)
        
        print(f"✅ Generated optical image saved to: {output_path}")
        print(f"📊 Image size: {args.img_size}x{args.img_size}")
        print(f"💾 File size: {output_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()