# Video Generator Module
"""
Video Generator Module

This module handles video generation using Runway's API. It takes a base image
and a text prompt to generate dynamic, engaging video content for advertisements.
"""

import os
import json
import time
import requests
import logging
from typing import Dict, Any, Optional
import uuid
import moviepy.editor as mp 
import PIL
import openai
import pandas as pd
import numpy as np

from .utils import setup_logger

# Setup logger
logger = setup_logger('video_generator')

def generate_runway_video(
    encoded_image: str,
    prompt: str,
    duration: int = 10,
    resolution: str = "1280x768",
    runway_api_key: Optional[str] = None,
    output_dir: str = "output/videos",
    max_retries: int = 3,
    polling_interval: int = 5
) -> Dict[str, Any]:
    """
    Generate a video using Runway's Gen-2 Video-to-Video API.
    
    Args:
        encoded_image: Base64-encoded image data
        prompt: Text prompt describing the desired video
        duration: Duration of the video in seconds (max 16)
        resolution: Desired video resolution
        runway_api_key: Runway API key
        output_dir: Directory to save the video
        max_retries: Maximum number of retries
        polling_interval: Time between status checks in seconds
        
    Returns:
        Dictionary with video generation metadata
    """
    if not runway_api_key:
        raise ValueError("Runway API key is required")
        
    # Ensure duration is within limits
    if duration > 16:
        logger.warning(f"Duration {duration}s exceeds maximum (16s). Setting to 16 seconds.")
        duration = 16
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare the request
    url = "https://api.runwayml.com/v1/generate/video"
    
    headers = {
        "Authorization": f"Bearer {runway_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "input": {
            "image": f"data:image/png;base64,{encoded_image}",
            "prompt": prompt
        },
        "parameters": {
            "duration": duration,
            "resolution": resolution
        }
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Submitting video generation request to Runway (Attempt {attempt+1}/{max_retries})")
            
            # Submit generation request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            job_id = response.json().get('id')
            if not job_id:
                raise ValueError("No job ID returned from Runway API")
                
            logger.info(f"Video generation job submitted successfully. Job ID: {job_id}")
            
            # Poll for job completion
            status_url = f"https://api.runwayml.com/v1/jobs/{job_id}"
            while True:
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'completed':
                    logger.info(f"Video generation completed successfully")
                    video_url = status_data.get('output', {}).get('video', None)
                    
                    if not video_url:
                        raise ValueError("No video URL in the completed job response")
                    
                    # Download the video
                    video_response = requests.get(video_url)
                    video_response.raise_for_status()
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"runway_video_{timestamp}_{uuid.uuid4().hex[:8]}.mp4"
                    video_path = os.path.join(output_dir, filename)
                    
                    # Save the video
                    with open(video_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    logger.info(f"Video saved to {video_path}")
                    
                    return {
                        'success': True,
                        'video_path': video_path,
                        'job_id': job_id,
                        'duration': duration,
                        'prompt': prompt
                    }
                    
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    logger.error(f"Video generation failed: {error}")
                    raise Exception(f"Runway API job failed: {error}")
                    
                else:
                    # Still processing
                    progress = status_data.get('progress', 0)
                    logger.info(f"Video generation in progress: {progress}%")
                    time.sleep(polling_interval)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            if attempt == max_retries - 1:
                return {
                    'success': False,
                    'error': f"API request failed after {max_retries} attempts: {str(e)}"
                }
            time.sleep(2)  # Wait before retrying
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            if attempt == max_retries - 1:
                return {
                    'success': False,
                    'error': f"Video generation failed: {str(e)}"
                }
            time.sleep(2)  # Wait before retrying

def generate_fallback_video(
    image_path: str,
    output_dir: str = "output/videos"
) -> Dict[str, Any]:
    """
    Generate a fallback video (simple animation) when Runway generation fails.
    Requires moviepy to be installed.
    
    Args:
        image_path: Path to the base image
        output_dir: Directory to save the video
        
    Returns:
        Dictionary with video metadata
    """
    try:
        from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
        import numpy as np
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create image clip
        image_clip = ImageClip(image_path).set_duration(10)
        
        # Add a simple zoom effect
        def zoom(t):
            return 1 + 0.1 * t  # Start at 1x zoom and end at 2x zoom
            
        image_clip = image_clip.resize(zoom)
        
        # Add a simple text that says "Your Ad Here"
        txt_clip = TextClip("Your Ad Here", fontsize=70, color='white')
        txt_clip = txt_clip.set_position('center').set_duration(10)
        
        # Composite the clips
        video = CompositeVideoClip([image_clip, txt_clip])
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"fallback_video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, filename)
        
        # Write the video
        video.write_videofile(video_path, fps=24)
        
        logger.info(f"Fallback video saved to {video_path}")
        
        return {
            'success': True,
            'video_path': video_path,
            'fallback': True
        }
        
    except ImportError:
        logger.error("MoviePy not installed; cannot generate fallback video")
        return {
            'success': False,
            'error': "Cannot generate fallback video: MoviePy not installed"
        }
    
    except Exception as e:
        logger.error(f"Error generating fallback video: {e}")
        return {
            'success': False,
            'error': f"Fallback video generation failed: {str(e)}"
        }

if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    from .utils import encode_image_to_base64
    
    load_dotenv()
    api_key = os.getenv("RUNWAY_API_KEY")
    
    if api_key:
        try:
            test_image_path = "test_product.jpg"  # Replace with an actual image path
            
            if os.path.exists(test_image_path):
                encoded_image = encode_image_to_base64(test_image_path)
                
                result = generate_runway_video(
                    encoded_image=encoded_image,
                    prompt="A dynamic advertisement showcasing the product with motion and energy",
                    duration=8,
                    runway_api_key=api_key
                )
                
                if result['success']:
                    print(f"Video generated successfully: {result['video_path']}")
                else:
                    print(f"Video generation failed: {result['error']}")
                    
                    # Try fallback
                    fallback = generate_fallback_video(test_image_path)
                    if fallback['success']:
                        print(f"Fallback video generated: {fallback['video_path']}")
            else:
                print(f"Test image not found: {test_image_path}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("RUNWAY_API_KEY not found in environment variables")