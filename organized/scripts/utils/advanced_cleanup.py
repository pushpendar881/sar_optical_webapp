#!/usr/bin/env python3
"""
Advanced Project Cleanup and Organization Script
Organizes scattered files into proper folder structure
"""
import os
import shutil
from pathlib import Path
import datetime

def create_folder_structure():
    """Create organized folder structure"""
    folders = [
        "organized/scripts/inference",
        "organized/scripts/setup", 
        "organized/scripts/utils",
        "organized/docs",
        "organized/temp_files",
        "organized/test_results",
        "organized/archived"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {folder}")

def organize_files():
    """Move files to appropriate folders"""
    
    # File organization mapping
    file_moves = {
        # Scripts - Inference
        "sar_to_optical_cpu.py": "organized/scripts/inference/",
        
        # Scripts - Setup and deployment
        "deploy.py": "organized/scripts/setup/",
        "start_backend.py": "organized/scripts/setup/",
        
        # Scripts - Utilities
        "compare_inference.py": "organized/scripts/utils/",
        "debug_colors.py": "organized/scripts/utils/",
        "test_setup.py": "organized/scripts/utils/",
        
        # Documentation
        "README.md": "organized/docs/",
        "SETUP_README.md": "organized/docs/",
        "DEPLOYMENT_CHECKLIST.md": "organized/docs/",
        
        # Test result images
        "backend_style_result.png": "organized/test_results/",
        "direct_inference_result.png": "organized/test_results/",
        "difference_image.png": "organized/test_results/",
        "test_direct.png": "organized/test_results/",
    }
    
    print("\n📦 Moving files to organized structure...")
    
    for source_file, dest_folder in file_moves.items():
        if Path(source_file).exists():
            try:
                shutil.move(source_file, dest_folder)
                print(f"✅ Moved: {source_file} → {dest_folder}")
            except Exception as e:
                print(f"❌ Error moving {source_file}: {e}")
        else:
            print(f"⚠️  File not found: {source_file}")

def handle_duplicate_folders():
    """Handle duplicate folder structures"""
    
    # If there's an existing scripts folder, merge it
    if Path("scripts").exists():
        print(f"\n🔄 Merging existing 'scripts' folder...")
        try:
            # Move contents to organized structure
            for item in Path("scripts").iterdir():
                dest = Path("organized/archived") / item.name
                shutil.move(str(item), str(dest))
                print(f"📦 Archived: scripts/{item.name} → organized/archived/")
            
            # Remove empty scripts folder
            Path("scripts").rmdir()
            print("🗑️  Removed empty 'scripts' folder")
        except Exception as e:
            print(f"❌ Error handling scripts folder: {e}")
    
    # If there's an existing setup folder, merge it  
    if Path("setup").exists():
        print(f"\n🔄 Merging existing 'setup' folder...")
        try:
            for item in Path("setup").iterdir():
                dest = Path("organized/archived") / f"setup_{item.name}"
                shutil.move(str(item), str(dest))
                print(f"📦 Archived: setup/{item.name} → organized/archived/")
            
            Path("setup").rmdir()
            print("🗑️  Removed empty 'setup' folder")
        except Exception as e:
            print(f"❌ Error handling setup folder: {e}")

def create_cleanup_summary():
    """Create a summary of what was organized"""
    
    summary = f"""# Project Cleanup Summary
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Organized Structure Created:

### 📁 organized/
├── 📁 scripts/
│   ├── 📁 inference/     # SAR to optical inference scripts
│   ├── 📁 setup/         # Deployment and setup scripts  
│   └── 📁 utils/         # Utility and debugging scripts
├── 📁 docs/              # All documentation files
├── 📁 test_results/      # Generated test images and results
├── 📁 temp_files/        # Temporary files (safe to delete)
└── 📁 archived/          # Original folder contents

## Files Kept in Root:
- `image.png` - Sample input image
- `SegCycleGAN_SegEarthOV-H100 (1).ipynb` - Main notebook
- `DRAG_AND_DROP_YOUR_PROJECT_HERE.bat` - Convenience script
- `backend/` and `frontend/` folders - Core application

## Benefits:
✅ Clean root directory
✅ Logical file organization  
✅ Easy to find specific files
✅ Professional project structure
✅ Safe archival of existing folders

## Next Steps:
1. Review the organized structure
2. Delete `organized/temp_files/` if not needed
3. Move frequently used scripts back to root if preferred
4. Update any hardcoded file paths in scripts
"""

    with open("CLEANUP_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("📝 Created CLEANUP_SUMMARY.md")

def print_final_structure():
    """Display the final organized structure"""
    
    print(f"\n📁 Final Project Structure:")
    print("=" * 50)
    
    # Root level
    root_files = [f for f in Path(".").iterdir() if f.is_file() and not f.name.startswith('.')]
    root_dirs = [d for d in Path(".").iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    for directory in sorted(root_dirs):
        print(f"📁 {directory.name}/")
        
        # Show some contents
        try:
            contents = list(directory.iterdir())[:3]
            for item in contents:
                if item.is_dir():
                    print(f"  📁 {item.name}/")
                else:
                    print(f"  📄 {item.name}")
            
            if len(list(directory.iterdir())) > 3:
                remaining = len(list(directory.iterdir())) - 3
                print(f"  ... and {remaining} more items")
        except:
            pass
        
        print()
    
    print("Root files:")
    for file in sorted(root_files)[:5]:
        print(f"📄 {file.name}")
    
    if len(root_files) > 5:
        print(f"... and {len(root_files) - 5} more files")

def main():
    """Main cleanup function"""
    
    print("🧹 Advanced Project Cleanup Starting...")
    print("=" * 50)
    
    # Create organized folder structure
    create_folder_structure()
    
    # Move scattered files to organized locations
    organize_files()
    
    # Handle any existing duplicate folders
    handle_duplicate_folders()
    
    # Create cleanup summary
    create_cleanup_summary()
    
    # Show final structure
    print_final_structure()
    
    print("\n" + "=" * 50)
    print("✅ Advanced cleanup completed successfully!")
    print("📋 Check CLEANUP_SUMMARY.md for details")
    print("🔍 Review the 'organized/' folder structure")

if __name__ == "__main__":
    main()