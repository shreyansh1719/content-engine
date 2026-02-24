# Video Ad Generator entry point
#!/usr/bin/env python3
"""
Video Ad Generator - Main Orchestrator

This script orchestrates the entire process of generating high-converting video advertisements
for various social media platforms using Runway's API for video generation and OpenAI for script creation.
"""

import os
import argparse
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import our modules
from .script_generator import generate_ad_script
from .video_generator import generate_runway_video
from .brand_overlay import apply_brand_overlays
from .platform_optimizer import optimize_for_platforms
from .ab_testing import create_ab_test_variations
from .utils import setup_logger, encode_image_to_base64, load_config

# Setup logger
logger = setup_logger('video_ad_generator')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate high-converting video ads for social media')
    
    parser.add_argument('--product', type=str, required=True, 
                        help='Name of the product for the ad')
    
    parser.add_argument('--brand', type=str, required=True,
                        help='Brand name for consistency in styling')
    
    parser.add_argument('--audience', type=str, default='young adults interested in lifestyle products',
                        help='Target audience persona')
    
    parser.add_argument('--image', type=str, required=True,
                        help='Path to product image or logo to use as base')
    
    parser.add_argument('--style', type=str, default='modern',
                        choices=['modern', 'elegant', 'energetic', 'minimalist', 'bold'],
                        help='Visual style for the ad')
    
    parser.add_argument('--duration', type=int, default=15,
                        help='Duration of the video in seconds')
    
    parser.add_argument('--platforms', type=str, nargs='+', 
                        default=['instagram', 'facebook', 'tiktok', 'youtube'],
                        help='Platforms to optimize for')
    
    parser.add_argument('--ab-testing', action='store_true',
                        help='Generate A/B testing variations')
    
    parser.add_argument('--variations', type=int, default=2,
                        help='Number of A/B testing variations to generate')
    
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save generated videos')
    
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to configuration file')
    
    return parser.parse_args()

def generate_ad(
    product: str,
    brand: str, 
    audience: str,
    image_path: str,
    style: str,
    duration: int,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a complete video advertisement.
    
    Args:
        product: Name of the product
        brand: Brand name
        audience: Target audience description
        image_path: Path to product image
        style: Visual style for the ad
        duration: Duration in seconds
        config: Configuration settings
        
    Returns:
        Dictionary with generated ad metadata and paths
    """
    logger.info(f"Starting ad generation for {product} by {brand}")
    
    # Step 1: Generate ad script with OpenAI
    logger.info("Generating ad script...")
    script_data = generate_ad_script(
        product=product,
        brand=brand,
        audience=audience,
        style=style,
        openai_api_key=config['openai_api_key']
    )
    
    logger.info(f"Script generated successfully: {script_data['script_summary']}")
    
    # Step 2: Encode base image for Runway
    try:
        encoded_image = encode_image_to_base64(image_path)
    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise
    
    # Step 3: Generate video with Runway
    logger.info("Generating video using Runway API...")
    prompt = f"A high-converting advertisement showcasing {product} by {brand} in a {style} style. {script_data['visual_direction']}"
    
    video_result = generate_runway_video(
        encoded_image=encoded_image,
        prompt=prompt,
        duration=duration,
        runway_api_key=config['runway_api_key']
    )
    
    if not video_result['success']:
        logger.error(f"Video generation failed: {video_result['error']}")
        raise Exception(f"Video generation failed: {video_result['error']}")
    
    logger.info(f"Video generated successfully: {video_result['video_path']}")
    
    # Step 4: Apply brand overlays (text, logo, etc.)
    logger.info("Applying brand overlays...")
    overlay_result = apply_brand_overlays(
        video_path=video_result['video_path'],
        brand=brand,
        script_data=script_data,
        brand_config=config.get('brands', {}).get(brand.lower(), {}),
        product=product
    )
    
    logger.info(f"Brand overlays applied: {overlay_result['branded_video_path']}")
    
    # Return metadata and paths
    return {
        'product': product,
        'brand': brand,
        'audience': audience,
        'style': style,
        'duration': duration,
        'script': script_data,
        'original_video_path': video_result['video_path'],
        'branded_video_path': overlay_result['branded_video_path'],
        'thumbnail_path': overlay_result.get('thumbnail_path'),
        'generation_time': datetime.now().isoformat(),
    }

def main():
    """Main function to orchestrate the video ad generation process."""
    # Parse arguments
    args = parse_arguments()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load configuration
    config = load_config(args.config)
    
    try:
        # Generate base ad
        ad_result = generate_ad(
            product=args.product,
            brand=args.brand,
            audience=args.audience,
            image_path=args.image,
            style=args.style,
            duration=args.duration,
            config=config
        )
        
        # Step 5: Optimize for different platforms
        logger.info(f"Optimizing for platforms: {args.platforms}")
        platform_videos = optimize_for_platforms(
            video_path=ad_result['branded_video_path'],
            platforms=args.platforms,
            output_dir=args.output_dir
        )
        
        ad_result['platform_versions'] = platform_videos
        
        # Step 6: Generate A/B testing variations if requested
        if args.ab_testing:
            logger.info(f"Generating {args.variations} A/B test variations...")
            variations = create_ab_test_variations(
                base_ad=ad_result,
                variations_count=args.variations,
                config=config
            )
            
            ad_result['ab_test_variations'] = variations
        
        # Save metadata to JSON
        metadata_path = os.path.join(
            args.output_dir, 
            f"{args.brand}_{args.product}_ad_metadata.json"
        )
        
        with open(metadata_path, 'w') as f:
            json.dump(ad_result, f, indent=2)
        
        logger.info(f"Ad generation complete. Metadata saved to {metadata_path}")
        
        # Print summary
        print("\n=== Video Ad Generation Complete ===")
        print(f"Product: {args.product}")
        print(f"Brand: {args.brand}")
        print(f"Base video: {ad_result['branded_video_path']}")
        print("\nPlatform Versions:")
        for platform, path in ad_result['platform_versions'].items():
            print(f"- {platform.title()}: {path}")
        
        if args.ab_testing:
            print(f"\nGenerated {len(ad_result['ab_test_variations'])} A/B test variations")
        
        print(f"\nMetadata saved to: {metadata_path}")
        
    except Exception as e:
        logger.error(f"Ad generation failed: {e}")
        logger.error(f"Exception details: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())