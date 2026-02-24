# A/B Testing Module
"""
A/B Testing Module

This module generates variations of ads for A/B testing by modifying script content,
visual elements, and other parameters to help identify the most effective ad versions.
"""

import os
import numpy as np
import logging
import json
import time
import random
from typing import Dict, List, Any, Optional, Tuple
import uuid
import requests
import base64
import moviepy.editor as mp

logger = logging.getLogger(__name__)

 

try:
    import moviepy.editor as mp
    from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, ColorClip
    from moviepy.video.tools.subtitles import SubtitlesClip
    from moviepy.video.fx.all import fadein, fadeout, resize
    # Use the correct path for TextClip - it's already imported from moviepy.editor
    # from moviepy.video.VideoClip import TextClip - remove this line
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    # Create placeholder classes if needed
    class DummyClip:
        def __init__(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    # Define mock classes to prevent errors
    VideoFileClip = TextClip = ImageClip = CompositeVideoClip = ColorClip = SubtitlesClip = DummyClip

# Then add checks before video operations:
if not MOVIEPY_AVAILABLE:
    logger.error("MoviePy not installed; cannot process videos")

def create_ab_test_variations(
    base_ad: Dict[str, Any],
    variations_count: int = 2,
    config: Dict[str, Any] = None,
    output_dir: str = "output/ab_testing"
) -> List[Dict[str, Any]]:
    """
    Create variations of an ad for A/B testing.
    
    Args:
        base_ad: Base ad result dictionary
        variations_count: Number of variations to generate
        config: Configuration settings
        output_dir: Directory to save variations
        
    Returns:
        List of variation dictionaries
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    variations = []
    
    # Determine which aspects to vary for each variation
    variation_aspects = [
        "copy",                # Different ad copy/script
        "text_presentation",   # Different text styles/positioning
        "cta",                 # Different call-to-action
        "color_scheme",        # Different color scheme
        "pacing"               # Different video timing/cuts
    ]
    
    # Ensure we have a minimum set of information from the base ad
    if not all(key in base_ad for key in ['product', 'brand_name', 'audience', 'script']):
        logger.error("Base ad missing required information")
        return variations
    
    # Get variation parameters
    product = base_ad['product']
    brand_name = base_ad['brand_name']
    audience = base_ad.get('audience', "general consumers")
    script_data = base_ad['script']
    original_video_path = base_ad.get('branded_video_path', base_ad.get('original_video_path'))
    
    # Check if we have the video file
    if not original_video_path or not os.path.exists(original_video_path):
        logger.error(f"Video file not found: {original_video_path}")
        return variations
    
    try:
        logger.info(f"Creating {variations_count} A/B test variations")
        
        # Generate variations
        for i in range(variations_count):
            # Select 1-2 aspects to vary for this variation
            num_aspects = min(2, len(variation_aspects))
            aspects_to_vary = random.sample(variation_aspects, num_aspects)
            
            logger.info(f"Variation {i+1}: Varying {', '.join(aspects_to_vary)}")
            
            # Create variation
            variation = create_single_variation(
                base_ad=base_ad,
                aspects_to_vary=aspects_to_vary,
                variation_number=i+1,
                config=config,
                output_dir=output_dir
            )
            
            if variation:
                variations.append(variation)
                logger.info(f"Variation {i+1} created successfully")
            else:
                logger.error(f"Failed to create variation {i+1}")
        
        return variations
        
    except Exception as e:
        logger.error(f"Error creating A/B test variations: {e}")
        return variations

def create_single_variation(
    base_ad: Dict[str, Any],
    aspects_to_vary: List[str],
    variation_number: int,
    config: Dict[str, Any],
    output_dir: str
) -> Optional[Dict[str, Any]]:
    """
    Create a single variation of the ad.
    
    Args:
        base_ad: Base ad dictionary
        aspects_to_vary: List of aspects to vary
        variation_number: Variation number
        config: Configuration settings
        output_dir: Output directory
        
    Returns:
        Variation dictionary or None if failed
    """
    # Extract base info
    product = base_ad['product']
    brand_name = base_ad['brand_name']
    audience = base_ad.get('audience', "general consumers")
    style = base_ad.get('style', "modern")
    video_path = base_ad.get('branded_video_path', base_ad.get('original_video_path'))
    
    # Create result dictionary
    variation = {
        'product': product,
        'brand_name': brand_name,
        'audience': audience,
        'variation_number': variation_number,
        'varied_aspects': aspects_to_vary,
        'original_video_path': video_path
    }
    
    try:
        # 1. Vary script if needed
        if "copy" in aspects_to_vary:
            logger.info("Generating alternative ad copy")
            new_script = generate_ad_script(
                product=product,
                brand=brand_name,
                audience=audience,
                style=style,
                openai_api_key=config['openai_api_key']
            )
            
            variation['script'] = new_script
            logger.info(f"New script generated: {new_script['script_summary']}")
        else:
            # Use original script
            variation['script'] = base_ad['script']
        
        # 2. Apply brand overlays with variations
        brand_config = config.get('brands', {}).get(brand_name.lower(), {})
        
        # Modify brand config based on aspects to vary
        if "text_presentation" in aspects_to_vary:
            brand_config = modify_text_presentation(brand_config)
            variation['text_presentation_changes'] = "Modified text styles and animations"
            
        if "color_scheme" in aspects_to_vary:
            brand_config = modify_color_scheme(brand_config)
            variation['color_scheme_changes'] = "Modified color scheme"
            
        if "cta" in aspects_to_vary:
            # Modify CTA in the script
            variation['script'] = modify_cta(variation['script'], product)
            variation['cta_changes'] = "Modified call-to-action"
        
        # Apply overlays with modified config
        overlay_result = apply_brand_overlays(
            video_path=video_path,
            brand=brand_name,
            script_data=variation['script'],
            brand_config=brand_config,
            product=product,
            output_dir=output_dir
        )
        
        # 3. Apply pacing changes if needed
        if "pacing" in aspects_to_vary and MOVIEPY_AVAILABLE:
            logger.info("Modifying video pacing")
            pacing_result = modify_video_pacing(
                overlay_result['branded_video_path'],
                variation_number,
                output_dir
            )
            
            if pacing_result['success']:
                variation['branded_video_path'] = pacing_result['video_path']
                variation['pacing_changes'] = pacing_result['changes']
            else:
                # Use the original overlay result
                variation['branded_video_path'] = overlay_result['branded_video_path']
                variation['pacing_changes'] = "Failed to modify pacing"
        else:
            # Use the original overlay result
            variation['branded_video_path'] = overlay_result['branded_video_path']
        
        variation['thumbnail_path'] = overlay_result.get('thumbnail_path', '')
        variation['success'] = True
        
        return variation
        
    except Exception as e:
        logger.error(f"Error creating variation {variation_number}: {e}")
        return None

def modify_text_presentation(brand_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Modify text presentation styles for a variation.
    
    Args:
        brand_config: Brand configuration dictionary
        
    Returns:
        Modified brand configuration
    """
    # Make a copy to avoid modifying the original
    config = brand_config.copy() if brand_config else {}
    
    # Ensure text_styles exists
    if 'text_styles' not in config:
        config['text_styles'] = {}
    
    # Randomly select modifications to apply
    modifications = random.sample([
        'change_font_sizes',
        'change_animations',
        'change_positions',
        'change_fonts'
    ], k=min(2, 4))  # Apply 1-2 modifications
    
    if 'change_font_sizes' in modifications:
        # Modify font sizes
        for style in ['headline', 'body', 'cta', 'brand']:
            if style in config['text_styles']:
                current_size = config['text_styles'][style].get('fontsize', 50)
                # Increase or decrease by 10-30%
                factor = random.uniform(0.8, 1.3)
                config['text_styles'][style]['fontsize'] = int(current_size * factor)
    
    if 'change_animations' in modifications:
        # Modify animation style
        animations = ['standard', 'dynamic', 'minimal', 'energetic']
        config['animation'] = random.choice(animations)
    
    if 'change_positions' in modifications:
        # This would be applied during the text overlay process
        # Just set a flag to indicate this should happen
        config['_vary_positions'] = True
    
    if 'change_fonts' in modifications and 'font' in config:
        # Try alternate fonts
        alternate_fonts = {
            'Arial-Bold': ['Helvetica-Bold', 'Verdana-Bold', 'Tahoma-Bold'],
            'Arial': ['Helvetica', 'Verdana', 'Tahoma'],
            'Times New Roman-Bold': ['Georgia-Bold', 'Garamond-Bold'],
            'Times New Roman': ['Georgia', 'Garamond'],
            'Helvetica-Bold': ['Arial-Bold', 'Verdana-Bold'],
            'Helvetica': ['Arial', 'Verdana']
        }
        
        current_font = config.get('font', 'Arial')
        if current_font in alternate_fonts:
            config['font'] = random.choice(alternate_fonts[current_font])
    
    return config

def modify_color_scheme(brand_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Modify color scheme for a variation.
    
    Args:
        brand_config: Brand configuration dictionary
        
    Returns:
        Modified brand configuration
    """
    # Make a copy to avoid modifying the original
    config = brand_config.copy() if brand_config else {}
    
    # Ensure colors exists
    if 'colors' not in config:
        config['colors'] = {
            'primary': '#0066CC',
            'secondary': '#FFFFFF',
            'accent': '#FFD700'
        }
    
    # Define some color schemes
    color_schemes = [
        {'primary': '#0066CC', 'secondary': '#FFFFFF', 'accent': '#FFD700'},  # Blue/White/Gold
        {'primary': '#E50914', 'secondary': '#FFFFFF', 'accent': '#000000'},  # Red/White/Black
        {'primary': '#4CAF50', 'secondary': '#FFFFFF', 'accent': '#FF9800'},  # Green/White/Orange
        {'primary': '#9C27B0', 'secondary': '#FFFFFF', 'accent': '#FFC107'},  # Purple/White/Amber
        {'primary': '#FF5722', 'secondary': '#FFFFFF', 'accent': '#2196F3'},  # Deep Orange/White/Blue
        {'primary': '#3F51B5', 'secondary': '#FFFFFF', 'accent': '#FF4081'},  # Indigo/White/Pink
        {'primary': '#000000', 'secondary': '#FFFFFF', 'accent': '#FFC107'},  # Black/White/Amber
    ]
    
    # Select a random color scheme
    new_scheme = random.choice(color_schemes)
    config['colors'].update(new_scheme)
    
    # Update text colors in text styles if they exist
    if 'text_styles' in config:
        for style in config['text_styles']:
            # Randomly decide whether to use primary, secondary, or accent for this style
            color_key = random.choice(['primary', 'secondary', 'accent'])
            config['text_styles'][style]['color'] = new_scheme[color_key]
    
    return config

def modify_cta(script_data: Dict[str, Any], product: str) -> Dict[str, Any]:
    """
    Modify the call-to-action for a variation.
    
    Args:
        script_data: Script data dictionary
        product: Product name
        
    Returns:
        Modified script data
    """
    # Make a copy to avoid modifying the original
    script = script_data.copy()
    
    # Different CTA variations
    cta_variations = [
        f"Shop {product} Now",
        f"Get Yours Today",
        f"Experience {product}",
        f"Order Now",
        f"Limited Time Offer",
        f"Buy Now",
        f"Learn More",
        f"Discover {product}",
        f"Act Now",
        f"Don't Miss Out"
    ]
    
    # Select a random CTA
    new_cta = random.choice(cta_variations)
    
    # Update CTA in text_overlays if it exists
    if 'text_overlays' in script:
        for overlay in script['text_overlays']:
            if overlay.get('type', '').lower() == 'cta':
                overlay['text'] = new_cta
    
    # Also update the voiceover to match if possible
    if 'voiceover' in script:
        # Try to find and replace the CTA in the voiceover
        common_ctas = ['shop now', 'buy now', 'get yours', 'order now']
        
        voiceover = script['voiceover']
        for cta in common_ctas:
            if cta in voiceover.lower():
                # Replace it with new CTA
                script['voiceover'] = voiceover.replace(cta, new_cta.lower())
                break
    
    return script

def modify_video_pacing(
    video_path: str,
    variation_number: int,
    output_dir: str
) -> Dict[str, Any]:
    """
    Modify the pacing of a video for variation testing.
    
    Args:
        video_path: Path to the video
        variation_number: Variation number
        output_dir: Output directory
        
    Returns:
        Dictionary with modification results
    """
    if not MOVIEPY_AVAILABLE:
        return {'success': False, 'error': 'MoviePy not available'}
    
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Pick a pacing modification
        modification_type = random.choice([
            'speed_up',
            'speed_down',
            'add_pause',
            'emphasize_sections'
        ])
        
        changes_description = ""
        
        if modification_type == 'speed_up':
            # Speed up the video slightly
            factor = random.uniform(1.1, 1.3)
            modified = video.speedx(factor=factor)
            changes_description = f"Increased playback speed by {(factor-1)*100:.0f}%"
            
        elif modification_type == 'speed_down':
            # Slow down the video slightly
            factor = random.uniform(0.8, 0.95)
            modified = video.speedx(factor=factor)
            changes_description = f"Decreased playback speed by {(1-factor)*100:.0f}%"
            
        elif modification_type == 'add_pause':
            # Add a brief pause at a strategic point (e.g., before CTA)
            pause_point = video.duration * 0.7  # 70% through the video
            pause_duration = random.uniform(0.3, 0.7)
            
            # Create the video with pause
            first_part = video.subclip(0, pause_point)
            last_part = video.subclip(pause_point, video.duration)
            
            # Create a freeze frame for the pause
            freeze_frame = video.get_frame(pause_point)
            freeze_clip = ImageClip(freeze_frame).set_duration(pause_duration)
            
            # Concatenate the parts
            from moviepy.editor import concatenate_videoclips
            modified = concatenate_videoclips([first_part, freeze_clip, last_part])
            changes_description = f"Added {pause_duration:.1f}s pause at {pause_point:.1f}s"
            
        elif modification_type == 'emphasize_sections':
            # Emphasize certain sections by slightly changing speed
            # Divide the video into sections
            num_sections = random.randint(3, 5)
            section_duration = video.duration / num_sections
            
            clips = []
            for i in range(num_sections):
                start = i * section_duration
                end = (i + 1) * section_duration
                section = video.subclip(start, end)
                
                # Emphasize every other section
                if i % 2 == 0:
                    factor = random.uniform(0.9, 1.1)
                    section = section.speedx(factor=factor)
                
                clips.append(section)
            
            # Concatenate the modified sections
            from moviepy.editor import concatenate_videoclips
            modified = concatenate_videoclips(clips)
            changes_description = f"Varied pacing across {num_sections} sections"
        
        else:
            # No modification
            modified = video
            changes_description = "No pacing changes applied"
        
        # Generate output filename
        timestamp = int(time.time())
        filename = f"pacing_var{variation_number}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        # Write the video
        modified.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Close clips to free resources
        modified.close()
        video.close()
        
        return {
            'success': True,
            'video_path': output_path,
            'changes': changes_description
        }
        
    except Exception as e:
        logger.error(f"Error modifying video pacing: {e}")
        return {
            'success': False,
            'error': str(e),
            'video_path': video_path
        }

def generate_variation_comparison(
    base_video_path: str,
    variation_paths: List[str],
    output_dir: str = "output/comparisons"
) -> Optional[str]:
    """
    Generate a side-by-side comparison of the base video and variations.
    
    Args:
        base_video_path: Path to the base video
        variation_paths: List of paths to variation videos
        output_dir: Output directory
        
    Returns:
        Path to the comparison video or None if failed
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy not installed; cannot create comparison")
        return None
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load videos
        base_video = VideoFileClip(base_video_path)
        variation_videos = [VideoFileClip(path) for path in variation_paths]
        
        # Resize all videos to the same size
        target_size = (base_video.w // 2, base_video.h // 2)
        resized_base = base_video.resize(target_size)
        resized_variations = [v.resize(target_size) for v in variation_videos]
        
        # Add labels
        from moviepy.editor import TextClip
        
        # Label the base video
        base_label = TextClip("Original", fontsize=30, color='white', bg_color='black')
        base_label = base_label.set_position(('center', 'bottom')).set_duration(resized_base.duration)
        base_with_label = CompositeVideoClip([resized_base, base_label])
        
        # Label the variations
        labeled_variations = []
        for i, video in enumerate(resized_variations):
            label = TextClip(f"Variation {i+1}", fontsize=30, color='white', bg_color='black')
            label = label.set_position(('center', 'bottom')).set_duration(video.duration)
            labeled_variations.append(CompositeVideoClip([video, label]))
        
        # Create grid layout
        all_clips = [base_with_label] + labeled_variations
        
        # Determine grid dimensions
        from math import ceil, sqrt
        n = len(all_clips)
        grid_size = max(2, ceil(sqrt(n)))
        
        # Fill grid with blank clips if needed
        from moviepy.editor import ColorClip
        while len(all_clips) < grid_size * grid_size:
            blank = ColorClip(target_size, color=(0, 0, 0), duration=base_video.duration)
            all_clips.append(blank)
        
        # Create rows for clips_array
        from moviepy.editor import clips_array
        rows = []
        for i in range(0, len(all_clips), grid_size):
            rows.append(all_clips[i:i+grid_size])
        
        # Create comparison grid
        comparison = clips_array(rows)
        
        # Generate output filename
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"ab_comparison_{timestamp}.mp4")
        
        # Write video
        comparison.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.info(f"Comparison video saved to {output_path}")
        
        # Close clips to free resources
        base_video.close()
        for v in variation_videos:
            v.close()
        comparison.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating comparison: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # This would be the output from a previous ad generation
    example_base_ad = {
        'product': 'Wireless Headphones',
        'brand_name': 'SoundPro',
        'headline': 'EXPERIENCE PREMIUM SOUND',
        'subheadline': 'Noise cancellation that adapts to your environment',
        'body_text': 'Enjoy crystal-clear audio and up to 50 hours of battery life with our most advanced headphones yet.',
        'call_to_action': 'SHOP NOW',
        'script': {
            'script_summary': 'Experience premium sound quality with noise cancellation that adapts to you',
            'text_overlays': [
                {"text": "PREMIUM SOUND", "type": "headline", "time": 1.0},
                {"text": "Noise cancellation that adapts to you", "type": "benefit", "time": 3.5},
                {"text": "50-hour battery life", "type": "benefit", "time": 6.0},
                {"text": "GET YOURS TODAY", "type": "cta", "time": 8.5}
            ],
            'voiceover': "Introducing the SoundPro Wireless Headphones. Experience premium sound quality with advanced noise cancellation that adapts to your environment. Enjoy up to 50 hours of battery life. Get yours today for an immersive audio experience."
        },
        'branded_video_path': 'example_video.mp4'  # This should be a real path for testing
    }
    
    # If there's a test video path provided
    import sys
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        example_base_ad['branded_video_path'] = sys.argv[1]
        example_base_ad['original_video_path'] = sys.argv[1]
        
        config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'brands': {
                'soundpro': {
                    'font': 'Arial-Bold',
                    'colors': {
                        'primary': '#0066CC',
                        'secondary': '#FFFFFF',
                        'accent': '#FFD700'
                    }
                }
            }
        }
        
        variations = create_ab_test_variations(
            base_ad=example_base_ad,
            variations_count=2,
            config=config
        )
        
        print(f"Created {len(variations)} variations")
        for i, variation in enumerate(variations):
            print(f"\nVariation {i+1}:")
            print(f"- Video: {variation.get('branded_video_path', 'N/A')}")
            print(f"- Varied: {', '.join(variation.get('varied_aspects', []))}")
            if 'color_scheme_changes' in variation:
                print(f"- Color changes: {variation['color_scheme_changes']}")
            if 'cta_changes' in variation:
                print(f"- CTA changes: {variation['cta_changes']}")
            if 'pacing_changes' in variation:
                print(f"- Pacing changes: {variation['pacing_changes']}")
        
        # Generate comparison if videos were created
        variation_paths = [v.get('branded_video_path') for v in variations 
                          if v.get('branded_video_path') and os.path.exists(v.get('branded_video_path'))]
        
        if variation_paths:
            comparison_path = generate_variation_comparison(
                base_video_path=example_base_ad['branded_video_path'],
                variation_paths=variation_paths
            )
            
            if comparison_path:
                print(f"\nComparison video: {comparison_path}")
    else:
        print("No test video provided. Usage: python ab_testing.py <test_video.mp4>")