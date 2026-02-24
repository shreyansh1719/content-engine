# Platform Optimizer Module
"""
Platform Optimizer Module

This module handles the optimization of videos for different social media platforms.
It resizes, crops, and formats videos to meet the specific requirements of each platform.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional, Tuple

# Import MoviePy
try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, clips_array
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .utils import setup_logger

# Setup logger
logger = setup_logger('platform_optimizer')

# Platform specifications
PLATFORM_SPECS = {
    'instagram': {
        'feed': {'aspect_ratio': 1.0, 'resolution': (1080, 1080), 'max_duration': 60},
        'story': {'aspect_ratio': 9/16, 'resolution': (1080, 1920), 'max_duration': 15},
        'reels': {'aspect_ratio': 9/16, 'resolution': (1080, 1920), 'max_duration': 90}
    },
    'facebook': {
        'feed': {'aspect_ratio': 16/9, 'resolution': (1280, 720), 'max_duration': 240},
        'story': {'aspect_ratio': 9/16, 'resolution': (1080, 1920), 'max_duration': 20}
    },
    'youtube': {
        'video': {'aspect_ratio': 16/9, 'resolution': (1920, 1080), 'max_duration': None}
    },
    'tiktok': {
        'video': {'aspect_ratio': 9/16, 'resolution': (1080, 1920), 'max_duration': 60}
    }
}

def optimize_for_platforms(
    video_path: str,
    platforms: List[str],
    format_types: Optional[Dict[str, List[str]]] = None,
    output_dir: str = "output/platform_videos",
    maintain_quality: bool = True
) -> Dict[str, str]:
    """
    Optimize a video for multiple social media platforms.
    
    Args:
        video_path: Path to the input video
        platforms: List of platforms to optimize for (instagram, facebook, youtube, tiktok)
        format_types: Dict mapping platforms to specific format types (e.g., {'instagram': ['feed', 'story']})
        output_dir: Directory to save optimized videos
        maintain_quality: Whether to maintain high quality (True) or prioritize file size (False)
        
    Returns:
        Dictionary mapping platform names to optimized video paths
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy not installed; cannot optimize videos for platforms")
        return {platform: video_path for platform in platforms}
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Default to all format types if not specified
    if not format_types:
        format_types = {
            'instagram': ['feed'],
            'facebook': ['feed'],
            'youtube': ['video'],
            'tiktok': ['video']
        }
    
    # Load the original video
    try:
        original_video = VideoFileClip(video_path)
        results = {}
        
        # Process each platform
        for platform in platforms:
            if platform not in PLATFORM_SPECS:
                logger.warning(f"Unknown platform: {platform}. Skipping.")
                continue
                
            # Get format types for this platform
            platform_formats = format_types.get(platform, list(PLATFORM_SPECS[platform].keys()))
            
            for format_type in platform_formats:
                if format_type not in PLATFORM_SPECS[platform]:
                    logger.warning(f"Unknown format type '{format_type}' for {platform}. Skipping.")
                    continue
                
                # Get specs for this platform and format
                specs = PLATFORM_SPECS[platform][format_type]
                
                # Optimize video
                optimized_path = optimize_video(
                    original_video=original_video,
                    platform=platform,
                    format_type=format_type,
                    specs=specs,
                    output_dir=output_dir,
                    maintain_quality=maintain_quality
                )
                
                # Store result
                if optimized_path:
                    results[f"{platform}_{format_type}"] = optimized_path
        
        # Close original video to free resources
        original_video.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Error optimizing video for platforms: {e}")
        return {platform: video_path for platform in platforms}

def optimize_video(
    original_video: VideoFileClip,
    platform: str,
    format_type: str,
    specs: Dict[str, Any],
    output_dir: str,
    maintain_quality: bool = True
) -> Optional[str]:
    """
    Optimize a video for a specific platform and format.
    
    Args:
        original_video: Original VideoFileClip
        platform: Platform name
        format_type: Format type (feed, story, etc.)
        specs: Platform specifications
        output_dir: Output directory
        maintain_quality: Whether to maintain high quality
        
    Returns:
        Path to optimized video or None if failed
    """
    try:
        logger.info(f"Optimizing video for {platform} {format_type}")
        
        # Get target aspect ratio and resolution
        target_ar = specs['aspect_ratio']
        target_res = specs['resolution']
        max_duration = specs['max_duration']
        
        # Calculate current aspect ratio
        current_ar = original_video.w / original_video.h
        
        # Determine whether to resize or crop
        if abs(current_ar - target_ar) < 0.1:
            # Aspect ratios are similar, just resize
            resized_video = original_video.resize(target_res)
        else:
            # Aspect ratios differ significantly, use the appropriate method
            if current_ar > target_ar:
                # Original is wider, crop width
                resized_video = crop_to_aspect_ratio(original_video, target_ar, 'width')
            else:
                # Original is taller, crop height
                resized_video = crop_to_aspect_ratio(original_video, target_ar, 'height')
                
            # Now resize to target resolution
            resized_video = resized_video.resize(target_res)
        
        # Trim video if needed
        if max_duration and original_video.duration > max_duration:
            logger.info(f"Trimming video from {original_video.duration}s to {max_duration}s")
            resized_video = resized_video.subclip(0, max_duration)
        
        # Generate output filename
        timestamp = int(time.time())
        filename = f"{platform}_{format_type}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        # Set encoding parameters based on quality preference
        if maintain_quality:
            bitrate = "5000k"
            audio_bitrate = "192k"
        else:
            bitrate = "2000k"
            audio_bitrate = "128k"
        
        # Write video
        resized_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate=bitrate,
            audio_bitrate=audio_bitrate,
            threads=4,
            preset='medium',  # Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.info(f"Optimized video saved to {output_path}")
        
        # Clean up
        resized_video.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error optimizing video for {platform} {format_type}: {e}")
        return None

def crop_to_aspect_ratio(
    clip: VideoFileClip,
    target_ar: float,
    crop_dimension: str = 'width'
) -> VideoFileClip:
    """
    Crop a video clip to match a target aspect ratio.
    
    Args:
        clip: VideoFileClip to crop
        target_ar: Target aspect ratio (width/height)
        crop_dimension: Which dimension to crop ('width' or 'height')
        
    Returns:
        Cropped VideoFileClip
    """
    current_w, current_h = clip.size
    current_ar = current_w / current_h
    
    if crop_dimension == 'width':
        # Crop width to match target AR
        new_w = int(current_h * target_ar)
        crop_amount = (current_w - new_w) / 2
        
        # Ensure crop amount is non-negative
        if crop_amount < 0:
            logger.warning(f"Invalid crop: calculated width ({new_w}) exceeds current width ({current_w})")
            return clip
            
        return clip.crop(x1=crop_amount, y1=0, x2=current_w-crop_amount, y2=current_h)
        
    else:  # crop_dimension == 'height'
        # Crop height to match target AR
        new_h = int(current_w / target_ar)
        crop_amount = (current_h - new_h) / 2
        
        # Ensure crop amount is non-negative
        if crop_amount < 0:
            logger.warning(f"Invalid crop: calculated height ({new_h}) exceeds current height ({current_h})")
            return clip
            
        return clip.crop(x1=0, y1=crop_amount, x2=current_w, y2=current_h-crop_amount)

def create_multi_platform_grid(
    video_paths: Dict[str, str],
    output_dir: str = "output/comparison"
) -> Optional[str]:
    """
    Create a grid video showing multiple platform versions side by side.
    
    Args:
        video_paths: Dictionary mapping platform names to video paths
        output_dir: Output directory
        
    Returns:
        Path to the grid video or None if failed
    """
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy not installed; cannot create multi-platform grid")
        return None
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load all videos
        clips = []
        for platform, path in video_paths.items():
            clip = VideoFileClip(path)
            # Add platform label
            from moviepy.editor import TextClip
            label = TextClip(platform, fontsize=30, color='white', bg_color='black')
            label = label.set_position(('center', 'bottom')).set_duration(clip.duration)
            clip_with_label = CompositeVideoClip([clip, label])
            clips.append(clip_with_label)
        
        # Determine grid layout based on number of clips
        num_clips = len(clips)
        if num_clips <= 2:
            # Horizontal layout for 1-2 clips
            grid_clip = clips_array([clips])
        elif num_clips <= 4:
            # 2x2 grid for 3-4 clips
            # Fill in empty spots with black clips if needed
            while len(clips) < 4:
                black_clip = ColorClip(clips[0].size, color=(0, 0, 0), duration=clips[0].duration)
                clips.append(black_clip)
            grid_clip = clips_array([clips[:2], clips[2:4]])
        else:
            # 3x3 grid for 5-9 clips
            # Fill in empty spots with black clips if needed
            while len(clips) < 9:
                black_clip = ColorClip(clips[0].size, color=(0, 0, 0), duration=clips[0].duration)
                clips.append(black_clip)
            grid_clip = clips_array([clips[:3], clips[3:6], clips[6:9]])
        
        # Generate output filename
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"platform_comparison_{timestamp}.mp4")
        
        # Write video
        grid_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        logger.info(f"Multi-platform grid saved to {output_path}")
        
        # Close clips to free resources
        for clip in clips:
            clip.close()
        grid_clip.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating multi-platform grid: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if os.path.exists(video_path):
            platforms = ['instagram', 'facebook', 'youtube', 'tiktok']
            format_types = {
                'instagram': ['feed', 'story'],
                'facebook': ['feed'],
                'youtube': ['video'],
                'tiktok': ['video']
            }
            
            results = optimize_for_platforms(
                video_path=video_path,
                platforms=platforms,
                format_types=format_types
            )
            
            print("\nOptimized videos:")
            for platform, path in results.items():
                print(f"- {platform}: {path}")
                
            # Create comparison grid
            grid_path = create_multi_platform_grid(results)
            if grid_path:
                print(f"\nComparison grid: {grid_path}")
        else:
            print(f"Video file not found: {video_path}")
    else:
        print("Usage: python platform_optimizer.py <video_path>")