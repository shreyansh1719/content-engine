# Brand Overlay Module
"""
Brand Overlay Module

This module handles text overlays, logo insertion, and maintaining brand consistency
for video advertisements. It uses moviepy to add dynamic text elements and brand assets
to the generated videos.
"""

import os
import logging
import json
from typing import Dict, Any, List, Tuple, Optional
import uuid
import time
from PIL import Image
import moviepy.editor

# Import MoviePy
try:
    from moviepy.editor import (
        VideoFileClip, TextClip, ImageClip, CompositeVideoClip, 
        ColorClip, AudioFileClip
    )
    from moviepy.video.tools.subtitles import SubtitlesClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .utils import setup_logger, download_file

# Setup logger
logger = setup_logger('brand_overlay')

def apply_brand_overlays(
    video_path: str,
    brand: str,
    script_data: Dict[str, Any],
    brand_config: Dict[str, Any] = None,
    product: str = "",
    output_dir: str = "output/branded_videos",
    logo_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply brand-consistent text overlays and logo to a video.
    
    Args:
        video_path: Path to the generated video
        brand: Brand name
        script_data: Script data containing text overlays
        brand_config: Brand configuration with colors, fonts, etc.
        product: Product name
        output_dir: Directory to save the branded video
        logo_path: Path to brand logo (optional)
        
    Returns:
        Dictionary with paths to branded video
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy not installed; cannot apply brand overlays")
        return {'branded_video_path': video_path}
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        logger.info(f"Applying brand overlays to video: {video_path}")
        
        # Load the video
        video = VideoFileClip(video_path)
        video_duration = video.duration
        
        # Use default brand config if none provided
        if not brand_config:
            brand_config = get_default_brand_config(brand)
        
        # Prepare clips list (we'll add all overlay elements to this)
        clips = [video]  # Start with the base video
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            logo_clip = add_logo(logo_path, video, brand_config)
            if logo_clip:
                clips.append(logo_clip)
                
        # Add text overlays
        text_overlays = extract_text_overlays(script_data, brand_config, video_duration)
        for overlay in text_overlays:
            text_clip = create_text_clip(
                text=overlay['text'],
                start_time=overlay['start_time'],
                end_time=overlay['end_time'],
                position=overlay['position'],
                style=overlay['style'],
                brand_config=brand_config
            )
            if text_clip:
                clips.append(text_clip)
        
        # Add final CTA with more emphasis
        cta = extract_cta(script_data, product)
        if cta:
            cta_clip = create_cta_clip(
                cta=cta,
                start_time=max(0, video_duration - 6),  # Show in the last 6 seconds
                end_time=video_duration,
                brand_config=brand_config
            )
            if cta_clip:
                clips.append(cta_clip)
        
        # Add brand name at the end
        brand_clip = create_text_clip(
            text=brand.upper(),
            start_time=max(0, video_duration - 4),  # Show in the last 4 seconds
            end_time=video_duration,
            position=('center', 0.85),  # Near bottom center
            style='brand',
            brand_config=brand_config
        )
        if brand_clip:
            clips.append(brand_clip)
        
        # Compose the final video
        final_video = CompositeVideoClip(clips)
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"{brand}_{product.replace(' ', '_')}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        # Write the final video
        final_video.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True,
            fps=30
        )
        
        logger.info(f"Branded video saved to {output_path}")
        
        # Generate thumbnail
        thumbnail_path = generate_thumbnail(final_video, output_dir, brand, product)
        
        # Close clips to release resources
        final_video.close()
        video.close()
        
        return {
            'branded_video_path': output_path,
            'thumbnail_path': thumbnail_path
        }
        
    except Exception as e:
        logger.error(f"Error applying brand overlays: {e}")
        return {'branded_video_path': video_path, 'error': str(e)}

def get_default_brand_config(brand: str) -> Dict[str, Any]:
    """
    Get default brand configuration if none is provided.
    
    Args:
        brand: Brand name
        
    Returns:
        Default brand configuration
    """
    # Convert brand to lowercase for case-insensitive matching
    brand_lower = brand.lower()
    
    # Some predefined brand configurations for well-known brands
    predefined_configs = {
        'apple': {
            'font': 'SF-Pro-Display-Bold',
            'font_fallback': 'Helvetica-Bold',
            'colors': {
                'primary': '#000000',
                'secondary': '#FFFFFF',
                'accent': '#0066CC'
            },
            'text_styles': {
                'headline': {'fontsize': 70, 'color': 'white', 'font': 'SF-Pro-Display-Bold'},
                'body': {'fontsize': 40, 'color': 'white', 'font': 'SF-Pro-Display-Regular'},
                'cta': {'fontsize': 60, 'color': 'white', 'font': 'SF-Pro-Display-Bold'},
                'brand': {'fontsize': 50, 'color': 'white', 'font': 'SF-Pro-Display-Bold'}
            },
            'animation': 'minimal'
        },
        'nike': {
            'font': 'Futura-Bold',
            'font_fallback': 'Arial-Bold',
            'colors': {
                'primary': '#000000',
                'secondary': '#FFFFFF',
                'accent': '#F15C22'
            },
            'text_styles': {
                'headline': {'fontsize': 80, 'color': 'white', 'font': 'Futura-Bold'},
                'body': {'fontsize': 40, 'color': 'white', 'font': 'Futura-Medium'},
                'cta': {'fontsize': 70, 'color': 'white', 'font': 'Futura-Bold'},
                'brand': {'fontsize': 60, 'color': 'white', 'font': 'Futura-Bold'}
            },
            'animation': 'dynamic'
        },
        'coca-cola': {
            'font': 'TCCC-UnityHeadline',
            'font_fallback': 'Arial-Bold',
            'colors': {
                'primary': '#F40009',
                'secondary': '#FFFFFF',
                'accent': '#F40009'
            },
            'text_styles': {
                'headline': {'fontsize': 70, 'color': 'white', 'font': 'Arial-Bold'},
                'body': {'fontsize': 40, 'color': 'white', 'font': 'Arial'},
                'cta': {'fontsize': 60, 'color': 'white', 'font': 'Arial-Bold'},
                'brand': {'fontsize': 50, 'color': 'white', 'font': 'Arial-Bold'}
            },
            'animation': 'energetic'
        }
    }
    
    # Check if we have a predefined config for this brand
    if brand_lower in predefined_configs:
        return predefined_configs[brand_lower]
    
    # Default configuration
    return {
        'font': 'Arial-Bold',
        'font_fallback': 'Arial',
        'colors': {
            'primary': '#0066CC',  # Blue
            'secondary': '#FFFFFF',  # White
            'accent': '#FFD700'  # Gold
        },
        'text_styles': {
            'headline': {'fontsize': 70, 'color': 'white', 'font': 'Arial-Bold'},
            'body': {'fontsize': 40, 'color': 'white', 'font': 'Arial'},
            'cta': {'fontsize': 60, 'color': 'white', 'font': 'Arial-Bold', 'bg_color': '#0066CC'},
            'brand': {'fontsize': 50, 'color': 'white', 'font': 'Arial-Bold'}
        },
        'animation': 'standard'
    }

def add_logo(
    logo_path: str, 
    video: VideoFileClip, 
    brand_config: Dict[str, Any]
) -> Optional[ImageClip]:
    """
    Add logo to the video.
    
    Args:
        logo_path: Path to logo image
        video: VideoFileClip object
        brand_config: Brand configuration
        
    Returns:
        ImageClip with the logo or None if failed
    """
    try:
        # Create logo clip
        logo = ImageClip(logo_path)
        
        # Resize logo to a reasonable size (e.g., 15% of video width)
        logo_width = video.w * 0.15
        logo = logo.resize(width=logo_width)
        
        # Set position (top-right corner with padding)
        padding = video.w * 0.03  # 3% padding
        logo = logo.set_position((video.w - logo_width - padding, padding))
        
        # Set duration to full video
        logo = logo.set_duration(video.duration)
        
        # Add animation if specified
        animation = brand_config.get('animation', 'standard')
        if animation == 'fade_in':
            logo = logo.fadein(1.5)
        
        return logo
        
    except Exception as e:
        logger.error(f"Error adding logo: {e}")
        return None

def extract_text_overlays(
    script_data: Dict[str, Any],
    brand_config: Dict[str, Any],
    video_duration: float
) -> List[Dict[str, Any]]:
    """
    Extract and format text overlays from script data.
    
    Args:
        script_data: Script data dictionary
        brand_config: Brand configuration
        video_duration: Duration of the video
        
    Returns:
        List of formatted text overlays
    """
    overlays = []
    
    # Process overlays from script_data if available
    for idx, overlay in enumerate(script_data.get('text_overlays', [])):
        # Skip if no text
        if not overlay.get('text'):
            continue
            
        # Determine overlay type/style
        overlay_type = overlay.get('type', '').lower()
        if 'headline' in overlay_type or idx == 0:
            style = 'headline'
        elif 'cta' in overlay_type:
            style = 'cta'
        else:
            style = 'body'
            
        # Get timestamp or calculate based on position in sequence
        start_time = overlay.get('time', idx * (video_duration / (len(script_data.get('text_overlays', [])) + 1)))
        
        # Ensure start_time is within video duration
        start_time = min(start_time, video_duration - 2)
        
        # End time is either specified or 3 seconds after start (or end of video)
        end_time = min(overlay.get('end_time', start_time + 3), video_duration)
        
        # Determine position
        position = overlay.get('position', 'center')
        if position == 'center':
            position = ('center', 'center')
        elif position == 'top':
            position = ('center', 0.15)
        elif position == 'bottom':
            position = ('center', 0.85)
        
        overlays.append({
            'text': overlay.get('text', ''),
            'start_time': start_time,
            'end_time': end_time,
            'position': position,
            'style': style
        })
    
    # If no overlays from script_data, add headline from script_summary
    if not overlays and 'script_summary' in script_data:
        overlays.append({
            'text': script_data['script_summary'],
            'start_time': 1.0,  # Start after 1 second
            'end_time': 4.0,    # Display for 3 seconds
            'position': ('center', 0.15),  # Top center
            'style': 'headline'
        })
    
    # Extract key benefits if available
    key_benefits = []
    for frame in script_data.get('key_frames', []):
        if 'benefit' in frame.get('description', '').lower():
            key_benefits.append(frame.get('description', ''))
    
    # Add key benefits as body text if we have them
    if key_benefits:
        benefit_count = len(key_benefits)
        for idx, benefit in enumerate(key_benefits[:3]):  # Limit to 3 benefits
            # Distribute benefits evenly in the middle section of the video
            mid_point = video_duration / 2
            spread = video_duration / 4  # 1/4 of video duration
            
            # Calculate start time based on position in sequence
            if benefit_count > 1:
                relative_pos = idx / (benefit_count - 1) - 0.5  # -0.5 to 0.5
            else:
                relative_pos = 0
                
            start_time = mid_point + (relative_pos * spread)
            end_time = start_time + 2.5  # Show each benefit for 2.5 seconds
            
            # Limit to video duration
            start_time = max(0, min(start_time, video_duration - 2.5))
            end_time = min(end_time, video_duration)
            
            # Add to overlays
            overlays.append({
                'text': benefit[:80],  # Limit length
                'start_time': start_time,
                'end_time': end_time,
                'position': ('center', 0.5 + (idx * 0.1)),  # Center, slightly offset for each
                'style': 'body'
            })
    
    return overlays

def extract_cta(script_data: Dict[str, Any], product: str) -> str:
    """
    Extract call-to-action from script data.
    
    Args:
        script_data: Script data dictionary
        product: Product name
        
    Returns:
        Call-to-action text
    """
    # Look for CTA in text_overlays
    for overlay in script_data.get('text_overlays', []):
        if overlay.get('type', '').lower() == 'cta':
            return overlay.get('text', '')
    
    # Look for CTA in key_frames
    for frame in script_data.get('key_frames', []):
        if 'cta' in frame.get('description', '').lower():
            return frame.get('description', '')
    
    # Scan voiceover for common CTA phrases
    common_ctas = [
        'shop now', 'buy now', 'get yours', 'experience', 'discover', 
        'try it', 'learn more', 'sign up', 'download', 'visit'
    ]
    
    voiceover = script_data.get('voiceover', '').lower()
    
    for cta in common_ctas:
        if cta in voiceover:
            # Find the sentence containing the CTA
            sentences = voiceover.split('.')
            for sentence in sentences:
                if cta in sentence.lower():
                    # Extract just the CTA part if possible
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if cta.split()[0] in word.lower() and i < len(words) - 1:
                            candidate_cta = ' '.join(words[i:i+2])
                            return candidate_cta.strip().capitalize()
                    return sentence.strip().capitalize()
    
    # Default CTA
    return f"Shop {product} Now"

def create_text_clip(
    text: str,
    start_time: float,
    end_time: float,
    position: Tuple[str, float],
    style: str,
    brand_config: Dict[str, Any]
) -> Optional[TextClip]:
    """
    Create a text clip with the specified style and timing.
    
    Args:
        text: Text content
        start_time: Start time in seconds
        end_time: End time in seconds
        position: Position tuple (horizontal, vertical)
        style: Text style (headline, body, cta, brand)
        brand_config: Brand configuration
        
    Returns:
        TextClip object or None if failed
    """
    try:
        # Get style settings
        style_config = brand_config.get('text_styles', {}).get(style, {})
        
        # Set defaults if not specified
        fontsize = style_config.get('fontsize', 60 if style == 'headline' else 40)
        color = style_config.get('color', 'white')
        font = style_config.get('font', brand_config.get('font', 'Arial-Bold'))
        
        # Fallback font if needed
        try:
            text_clip = TextClip(text, fontsize=fontsize, color=color, font=font)
        except:
            fallback_font = style_config.get('font_fallback', brand_config.get('font_fallback', 'Arial'))
            text_clip = TextClip(text, fontsize=fontsize, color=color, font=fallback_font)
        
        # Set position
        text_clip = text_clip.set_position(position)
        
        # Set duration
        text_clip = text_clip.set_start(start_time).set_end(end_time)
        
        # Add animation based on style
        animation = brand_config.get('animation', 'standard')
        if animation == 'dynamic':
            text_clip = text_clip.fadein(0.5).fadeout(0.5)
        elif animation == 'energetic':
            # More energetic animation for certain brands
            text_clip = text_clip.fadein(0.3)
            if style == 'headline':
                text_clip = text_clip.crossfadein(0.3)
        else:  # standard or minimal
            text_clip = text_clip.fadein(0.5).fadeout(0.5)
        
        # Add background for CTA if specified
        if style == 'cta' and style_config.get('bg_color'):
            bg_color = style_config.get('bg_color')
            padding = fontsize * 0.3  # Padding based on font size
            
            # Create background clip
            bg_width = text_clip.w + padding * 2
            bg_height = text_clip.h + padding * 2
            bg_clip = ColorClip(size=(int(bg_width), int(bg_height)), color=bg_color)
            bg_clip = bg_clip.set_opacity(0.8)
            bg_clip = bg_clip.set_position(position)
            bg_clip = bg_clip.set_start(start_time).set_end(end_time)
            
            # Combine background and text
            result_clip = CompositeVideoClip([bg_clip, text_clip])
            return result_clip
        
        return text_clip
        
    except Exception as e:
        logger.error(f"Error creating text clip: {e}")
        return None

def create_cta_clip(
    cta: str,
    start_time: float,
    end_time: float,
    brand_config: Dict[str, Any]
) -> Optional[CompositeVideoClip]:
    """
    Create a special call-to-action clip with background and emphasis.
    
    Args:
        cta: Call-to-action text
        start_time: Start time in seconds
        end_time: End time in seconds
        brand_config: Brand configuration
        
    Returns:
        CompositeVideoClip object or None if failed
    """
    try:
        # Get CTA style
        style_config = brand_config.get('text_styles', {}).get('cta', {})
        
        # Set defaults if not specified
        fontsize = style_config.get('fontsize', 60)
        color = style_config.get('color', 'white')
        font = style_config.get('font', brand_config.get('font', 'Arial-Bold'))
        
        # Get brand colors
        bg_color = style_config.get('bg_color', brand_config.get('colors', {}).get('accent', '#0066CC'))
        
        # Try to create text clip with specified font
        try:
            text_clip = TextClip(cta.upper(), fontsize=fontsize, color=color, font=font)
        except:
            # Fallback to Arial
            text_clip = TextClip(cta.upper(), fontsize=fontsize, color=color, font='Arial-Bold')
        
        # Calculate background dimensions with padding
        padding_x = fontsize * 0.5
        padding_y = fontsize * 0.3
        bg_width = text_clip.w + padding_x * 2
        bg_height = text_clip.h + padding_y * 2
        
        # Create background with rounded corners (if moviepy supports it)
        try:
            from moviepy.video.tools.drawing import circle
            
            # Create background clip
            bg_clip = ColorClip(size=(int(bg_width), int(bg_height)), color=bg_color)
            
            # Try to create rounded corners (this is a simple approximation)
            radius = min(int(bg_height / 4), 20)  # Radius of corner rounding
            
            # Apply mask for rounded corners
            mask = Image.new('L', (int(bg_width), int(bg_height)), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (int(bg_width), int(bg_height))], 
                radius=radius, 
                fill=255
            )
            bg_clip = bg_clip.set_mask(ImageClip(numpy.array(mask)))
            
        except (ImportError, NameError, AttributeError):
            # Fallback to regular rectangle if rounded corners not available
            bg_clip = ColorClip(size=(int(bg_width), int(bg_height)), color=bg_color)
        
        # Set position to center-bottom
        position = ('center', 0.85)
        bg_clip = bg_clip.set_position(position)
        
        # Center text on background
        text_pos = ('center', 'center')
        text_clip = text_clip.set_position(text_pos)
        
        # Set duration and animation
        bg_clip = bg_clip.set_start(start_time).set_end(end_time)
        text_clip = text_clip.set_start(start_time).set_end(end_time)
        
        # Add fade in/out
        bg_clip = bg_clip.fadein(0.5).fadeout(0.3)
        text_clip = text_clip.fadein(0.5).fadeout(0.3)
        
        # Combine clips
        return CompositeVideoClip([bg_clip, text_clip])
        
    except Exception as e:
        logger.error(f"Error creating CTA clip: {e}")
        return None

def generate_thumbnail(
    video_clip: VideoFileClip,
    output_dir: str,
    brand: str,
    product: str
) -> str:
    """
    Generate a thumbnail from the video.
    
    Args:
        video_clip: VideoFileClip object
        output_dir: Output directory
        brand: Brand name
        product: Product name
        
    Returns:
        Path to the generated thumbnail
    """
    try:
        # Get frame from first third of the video
        thumbnail_time = video_clip.duration / 3
        thumbnail = video_clip.get_frame(thumbnail_time)
        
        # Convert to PIL Image and save
        from PIL import Image
        import numpy as np
        
        img = Image.fromarray(np.uint8(thumbnail))
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"{brand}_{product.replace(' ', '_')}_thumbnail_{timestamp}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        # Save image
        img.save(output_path, quality=95)
        
        logger.info(f"Thumbnail saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return ""

if __name__ == "__main__":
    # Example usage
    example_script_data = {
        "script_summary": "Experience the revolution in sound quality",
        "text_overlays": [
            {"text": "PREMIUM SOUND", "type": "headline", "time": 1.0},
            {"text": "Noise cancellation that adapts to you", "type": "benefit", "time": 3.5},
            {"text": "50-hour battery life", "type": "benefit", "time": 6.0},
            {"text": "GET YOURS TODAY", "type": "cta", "time": 8.5}
        ],
        "key_frames": [
            {"timestamp": 2.0, "description": "Product appears with dramatic lighting"},
            {"timestamp": 4.0, "description": "Noise cancellation visualization"},
            {"timestamp": 7.0, "description": "Battery life indicator showing 50 hours"},
            {"timestamp": 9.0, "description": "Call to action with product and pricing"}
        ],
        "voiceover": "Introducing the SoundPro X1. Experience premium sound quality with advanced noise cancellation that adapts to your environment. Enjoy up to 50 hours of battery life. Get yours today for an immersive audio experience."
    }
    
    brand_config = {
        'font': 'Arial-Bold',
        'colors': {
            'primary': '#0066CC',
            'secondary': '#FFFFFF',
            'accent': '#FFD700'
        },
        'text_styles': {
            'headline': {'fontsize': 70, 'color': 'white', 'font': 'Arial-Bold'},
            'body': {'fontsize': 40, 'color': 'white', 'font': 'Arial'},
            'cta': {'fontsize': 60, 'color': 'white', 'font': 'Arial-Bold', 'bg_color': '#0066CC'},
            'brand': {'fontsize': 50, 'color': 'white', 'font': 'Arial-Bold'}
        },
        'animation': 'standard'
    }
    
    # This would apply overlays to a test video
    # apply_brand_overlays("test_video.mp4", "SoundPro", example_script_data, brand_config, "Wireless Headphones")