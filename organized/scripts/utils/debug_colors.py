"""
Debug script to analyze color channel issues in SAR-to-optical conversion
"""
import numpy as np
import torch
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_image_colors(image_path):
    """Analyze color distribution in an image"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    print(f"Image shape: {img_array.shape}")
    print(f"Red channel - min: {img_array[:,:,0].min()}, max: {img_array[:,:,0].max()}, mean: {img_array[:,:,0].mean():.1f}")
    print(f"Green channel - min: {img_array[:,:,1].min()}, max: {img_array[:,:,1].max()}, mean: {img_array[:,:,1].mean():.1f}")
    print(f"Blue channel - min: {img_array[:,:,2].min()}, max: {img_array[:,:,2].max()}, mean: {img_array[:,:,2].mean():.1f}")
    
    # Check if green is dominant
    green_dominance = img_array[:,:,1].mean() / (img_array.mean() + 1e-8)
    print(f"Green dominance ratio: {green_dominance:.2f}")
    
    return img_array

def analyze_checkpoint_weights(checkpoint_path):
    """Analyze the checkpoint to see if there are issues with the model weights"""
    try:
        ckpt = torch.load(checkpoint_path, map_location='cpu')
        
        if isinstance(ckpt, dict) and "G_AB" in ckpt:
            state_dict = ckpt["G_AB"]
            print("Checkpoint contains G_AB model")
        else:
            state_dict = ckpt
            print("Checkpoint is direct state dict")
        
        # Check the final layer weights (should map to RGB)
        final_conv_weight = None
        for name, param in state_dict.items():
            if 'model.22.weight' in name:  # Final conv layer
                final_conv_weight = param
                break
        
        if final_conv_weight is not None:
            print(f"Final layer weight shape: {final_conv_weight.shape}")
            # Should be [3, channels, 7, 7] for RGB output
            if final_conv_weight.shape[0] == 3:  # RGB channels
                for i, channel in enumerate(['Red', 'Green', 'Blue']):
                    channel_weights = final_conv_weight[i]
                    print(f"{channel} channel weights - mean: {channel_weights.mean():.4f}, std: {channel_weights.std():.4f}")
            else:
                print(f"Warning: Final layer has {final_conv_weight.shape[0]} output channels instead of 3")
        
        return True
        
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        return False

def create_test_correction(image_path, output_path):
    """Try to correct the green bias manually"""
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img).astype(np.float32)
    
    # Reduce green channel and boost red/blue
    corrected = img_array.copy()
    corrected[:,:,1] *= 0.6  # Reduce green by 40%
    corrected[:,:,0] *= 1.2  # Boost red by 20%
    corrected[:,:,2] *= 1.2  # Boost blue by 20%
    
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    
    Image.fromarray(corrected).save(output_path)
    print(f"Color-corrected image saved to: {output_path}")

if __name__ == "__main__":
    # Find the most recent output image
    output_dir = Path("backend/data/outputs")
    if output_dir.exists():
        output_files = list(output_dir.glob("*_output.png"))
        if output_files:
            latest_output = max(output_files, key=lambda x: x.stat().st_mtime)
            print(f"Analyzing latest output: {latest_output}")
            print("=" * 50)
            
            img_array = analyze_image_colors(latest_output)
            
            print("\n" + "=" * 50)
            print("Creating color-corrected version...")
            corrected_path = output_dir / f"corrected_{latest_output.name}"
            create_test_correction(latest_output, corrected_path)
        else:
            print("No output images found")
    
    # Analyze checkpoint
    checkpoint_path = Path("backend/data/checkpoints/cyclegan_checkpoint_latest.pth")
    if checkpoint_path.exists():
        print("\n" + "=" * 50)
        print("Analyzing checkpoint weights...")
        analyze_checkpoint_weights(checkpoint_path)
    else:
        print("Checkpoint not found")