# Script Generator Module
"""
Script Generator Module

This module handles the generation of ad scripts using OpenAI's API.
It creates persuasive, high-converting scripts tailored to specific products,
brands, and target audiences.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

from openai import OpenAI
from .utils import setup_logger

# Setup logger
logger = setup_logger('script_generator')

def generate_ad_script(
    product: str,
    brand: str,
    audience: str,
    style: str = "modern",
    max_retries: int = 3,
    openai_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an advertisement script using OpenAI.
    
    Args:
        product: Name of the product
        brand: Brand name
        audience: Target audience description
        style: Visual style for the ad
        max_retries: Maximum number of retries on failure
        openai_api_key: OpenAI API key
        
    Returns:
        Dictionary containing the generated script and metadata
    """
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Prepare the prompt for advanced script generation
    system_prompt = """You are an expert advertising copywriter specializing in creating high-converting video ad scripts. 
    Your scripts are concise, emotionally engaging, and drive action. 
    You focus on benefits, not features, and create a narrative arc that captures attention immediately.
    Format your response as structured JSON with script, visual_direction, key_frames, and other necessary fields."""
    
    user_prompt = f"""Create a compelling 30-second video ad script for {product} by {brand} targeting {audience}.

    The ad should have a {style} visual style and include:
    
    1. An attention-grabbing opening (5 seconds)
    2. Key product benefits (15 seconds)
    3. Strong emotional appeal
    4. Clear call-to-action (final 5-10 seconds)
    
    Structure your response as JSON with the following fields:
    
    - script_full: Complete 30-second script with timing indicators
    - script_summary: 1-sentence summary of the script concept
    - visual_direction: Direction for the video's visual style and feel
    - voiceover: The script text for voiceover
    - key_frames: List of 4-5 key moments in the video with timestamp and description
    - text_overlays: List of text to overlay at specific timestamps (headline, key benefits, CTA)
    - tone: The emotional tone of the ad
    - hooks: The key attention hooks used
    
    Make the script concise, high-energy, and focused on the most compelling product benefits.
    Ensure the call-to-action is clear and motivating.
    """
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Generating script for {product} by {brand} (Attempt {attempt+1}/{max_retries})")
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            script_data = json.loads(response_text)
            
            # Validate the required fields
            required_fields = [
                'script_full', 'script_summary', 'visual_direction', 
                'voiceover', 'key_frames', 'text_overlays'
            ]
            
            for field in required_fields:
                if field not in script_data:
                    raise ValueError(f"Required field '{field}' missing from OpenAI response")
            
            # Add metadata
            script_data['product'] = product
            script_data['brand'] = brand
            script_data['audience'] = audience
            script_data['style'] = style
            
            logger.info(f"Script generated successfully for {product}")
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retrying
            
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retrying

def extract_key_benefits(script_data: Dict[str, Any]) -> List[str]:
    """
    Extract key benefits from a generated script.
    
    Args:
        script_data: The script data dictionary
        
    Returns:
        List of key benefit statements
    """
    benefits = []
    
    # Try to extract from text_overlays
    for overlay in script_data.get('text_overlays', []):
        if 'benefit' in overlay.get('type', '').lower():
            benefits.append(overlay.get('text', ''))
    
    # If we don't have enough, try to extract from the voiceover
    if len(benefits) < 3:
        # Simple heuristic: look for sentences containing keywords
        benefit_keywords = ['benefit', 'advantage', 'feature', 'offer', 'provide', 'deliver', 'improve']
        voiceover = script_data.get('voiceover', '')
        
        # Split into sentences
        sentences = [s.strip() for s in voiceover.split('.') if s.strip()]
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in benefit_keywords):
                if sentence not in benefits:
                    benefits.append(sentence)
    
    # Ensure benefits are concise
    return [b if len(b) <= 60 else b[:57] + '...' for b in benefits[:3]]

def generate_cta(script_data: Dict[str, Any]) -> str:
    """
    Extract or generate a call to action.
    
    Args:
        script_data: The script data dictionary
        
    Returns:
        Call to action text
    """
    # Try to extract from text_overlays
    for overlay in script_data.get('text_overlays', []):
        if 'cta' in overlay.get('type', '').lower():
            return overlay.get('text', '')
    
    # Look for common CTA phrases in the voiceover
    cta_patterns = [
        'buy now', 'shop now', 'get yours', 'try it today', 'download now', 
        'sign up', 'learn more', 'visit', 'discover', 'join'
    ]
    
    voiceover = script_data.get('voiceover', '').lower()
    
    for pattern in cta_patterns:
        if pattern in voiceover:
            # Extract the sentence containing the CTA
            sentences = [s.strip() for s in voiceover.split('.') if pattern in s.lower()]
            if sentences:
                return sentences[0].strip().capitalize()
    
    # Default CTA based on script tone
    tone = script_data.get('tone', 'persuasive').lower()
    if 'urgent' in tone or 'limited' in tone:
        return "Shop Now - Limited Time Offer!"
    elif 'elegant' in tone or 'luxury' in tone:
        return "Discover the Experience"
    else:
        return "Shop Now"

if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            script = generate_ad_script(
                product="Premium Wireless Headphones",
                brand="SoundPro",
                audience="tech-savvy professionals who value quality audio and style",
                openai_api_key=api_key
            )
            
            print(json.dumps(script, indent=2))
            
            print("\nKey Benefits:")
            for benefit in extract_key_benefits(script):
                print(f"- {benefit}")
                
            print(f"\nCTA: {generate_cta(script)}")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("OPENAI_API_KEY not found in environment variables")