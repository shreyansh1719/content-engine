#!/usr/bin/env python3
import os
import json
import sys

def test_imports():
    """Test that all modules can be imported."""
    try:
        import script_generator
        import video_generator
        import brand_overlay
        import platform_optimizer
        import ab_testing
        import tts_generator
        import typography_integration
        import utils
        print("All modules imported successfully!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def test_config():
    """Test that config file can be loaded."""
    try:
        with open('video_config.json', 'r') as f:
            config = json.load(f)
        print("Configuration loaded successfully!")
        return True
    except Exception as e:
        print(f"Config error: {e}")
        return False

def test_directories():
    """Test that output directories exist."""
    with open('video_config.json', 'r') as f:
        config = json.load(f)
    
    output_dir = config.get('output_dir', '../output')
    subdirs = config.get('video_subdirs', {})
    
    for key, subdir in subdirs.items():
        path = os.path.join(output_dir, subdir)
        if not os.path.exists(path):
            print(f"Warning: Directory {path} does not exist!")
            return False
    
    print("All output directories verified!")
    return True

if __name__ == "__main__":
    print("Testing video ad generator setup...")
    imports_ok = test_imports()
    config_ok = test_config()
    dirs_ok = test_directories()
    
    if imports_ok and config_ok and dirs_ok:
        print("\nSuccess! Your video ad generator setup is complete and working correctly.")
        print("To generate a video ad, run:")
        print("python video_ad_generator.py --product \"Your Product\" --brand \"Your Brand\" --image \"path/to/image.jpg\"")
    else:
        print("\nSetup incomplete. Please fix the issues above.")
