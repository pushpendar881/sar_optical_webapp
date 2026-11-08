"""
Compare direct inference vs backend processing to find the green bias source
"""
import numpy as np
import torch
from PIL import Image
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))
from model import load_generator

def test_direct_inference(image_path, checkpoint_path):
    """Test using the exact same method as your working inference script"""
    print("=" * 50)
    print("DIRECT INFERENCE (like your working script)")
    print("=" * 50)
    
    device = 'cpu'  # Force CPU
    
    # Load model
    G_AB = load_generator(checkpoint_path, device)
    
    # Process image exactly like working inference script
    sar_img = Image.open(image_path).convert("L").resize((256, 256), Image.Resampling.LANCZOS)
    print(f"Input image size: {sar_img.size}, mode: {sar_img.mode}")
    
    # Convert to tensor
    sar_array = np.array(sar_img, dtype=np.float32) / 127.5 - 1.0
    sar_t = torch.from_numpy(sar_array).unsqueeze(0).unsqueeze(0).to(device)
    print(f"Tensor shape: {sar_t.shape}, min: {sar_t.min():.3f}, max: {sar_t.max():.3f}")
    
    # Forward pass
    with torch.no_grad():
        fake_t = G_AB(sar_t)[0].permute(1, 2, 0).cpu().numpy()
    
    print(f"Output tensor shape: {fake_t.shape}, min: {fake_t.min():.3f}, max: {fake_t.max():.3f}")
    print(f"Channel means - R: {fake_t[:,:,0].mean():.3f}, G: {fake_t[:,:,1].mean():.3f}, B: {fake_t[:,:,2].mean():.3f}")
    
    # Post-process
    fake_np = ((fake_t + 1) * 127.5).clip(0, 255).astype(np.uint8)
    print(f"Final image shape: {fake_np.shape}, min: {fake_np.min()}, max: {fake_np.max()}")
    print(f"Final channel means - R: {fake_np[:,:,0].mean():.1f}, G: {fake_np[:,:,1].mean():.1f}, B: {fake_np[:,:,2].mean():.1f}")
    
    result_img = Image.fromarray(fake_np)
    result_img.save("direct_inference_result.png")
    print("Saved: direct_inference_result.png")
    
    return fake_np

def test_backend_style(image_path, checkpoint_path):
    """Test using backend style processing"""
    print("\n" + "=" * 50)
    print("BACKEND STYLE INFERENCE")
    print("=" * 50)
    
    import io
    
    device = 'cpu'  # Force CPU
    
    # Load model
    G_AB = load_generator(checkpoint_path, device)
    
    # Process like backend does
    with open(image_path, 'rb') as f:
        raw = f.read()
    
    sar_img = Image.open(io.BytesIO(raw)).convert("L").resize((256, 256), Image.Resampling.LANCZOS)
    print(f"Input image size: {sar_img.size}, mode: {sar_img.mode}")
    
    # Convert to tensor - backend style
    sar_array = np.array(sar_img, dtype=np.float32) / 127.5 - 1.0
    sar_t = torch.from_numpy(sar_array).unsqueeze(0).unsqueeze(0).to(device)
    print(f"Tensor shape: {sar_t.shape}, min: {sar_t.min():.3f}, max: {sar_t.max():.3f}")
    
    # Forward pass
    with torch.no_grad():
        fake_t = G_AB(sar_t)[0].permute(1, 2, 0).cpu().numpy()
    
    print(f"Output tensor shape: {fake_t.shape}, min: {fake_t.min():.3f}, max: {fake_t.max():.3f}")
    print(f"Channel means - R: {fake_t[:,:,0].mean():.3f}, G: {fake_t[:,:,1].mean():.3f}, B: {fake_t[:,:,2].mean():.3f}")
    
    # Post-process
    fake_np = ((fake_t + 1) * 127.5).clip(0, 255).astype(np.uint8)
    print(f"Final image shape: {fake_np.shape}, min: {fake_np.min()}, max: {fake_np.max()}")
    print(f"Final channel means - R: {fake_np[:,:,0].mean():.1f}, G: {fake_np[:,:,1].mean():.1f}, B: {fake_np[:,:,2].mean():.1f}")
    
    result_img = Image.fromarray(fake_np)
    result_img.save("backend_style_result.png")
    print("Saved: backend_style_result.png")
    
    return fake_np

def compare_results(result1, result2):
    """Compare the two results"""
    print("\n" + "=" * 50)
    print("COMPARISON")
    print("=" * 50)
    
    diff = np.abs(result1.astype(np.float32) - result2.astype(np.float32))
    print(f"Max difference: {diff.max()}")
    print(f"Mean difference: {diff.mean():.2f}")
    print(f"Channel differences - R: {diff[:,:,0].mean():.2f}, G: {diff[:,:,1].mean():.2f}, B: {diff[:,:,2].mean():.2f}")
    
    if diff.max() < 1:
        print("✅ Results are nearly identical!")
    else:
        print("❌ Results differ significantly!")
        
    # Save difference image
    diff_img = (diff * 10).clip(0, 255).astype(np.uint8)  # Amplify differences
    Image.fromarray(diff_img).save("difference_image.png")
    print("Saved: difference_image.png (differences amplified 10x)")

if __name__ == "__main__":
    # Use the test image
    image_path = "image.png"  # Your test image
    checkpoint_path = "backend/data/checkpoints/cyclegan_checkpoint_latest.pth"
    
    if not Path(image_path).exists():
        print(f"Please put your test image as '{image_path}'")
        sys.exit(1)
        
    if not Path(checkpoint_path).exists():
        print(f"Checkpoint not found: {checkpoint_path}")
        sys.exit(1)
    
    try:
        result1 = test_direct_inference(image_path, checkpoint_path)
        result2 = test_backend_style(image_path, checkpoint_path)
        compare_results(result1, result2)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()