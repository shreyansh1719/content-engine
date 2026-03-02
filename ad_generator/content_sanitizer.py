"""
Content sanitization module to avoid AI generation issues
"""
import re
import logging
import random
from typing import Dict, Any, List

class ContentSanitizer:
    def __init__(self):
        """Initialize content sanitizer with patterns and brand lists"""
        self.logger = logging.getLogger('ContentSanitizer')
        
        # Patterns that might cause DALL-E to reject prompts
        self.restricted_patterns = [
            r'\b(porn|nude|naked|sex|sexy|nudes|explicit|nsfw)\b',
            r'\b(violence|gore|bloody|disturbing|graphic)\b',
            r'\b(illegal|criminal|crime|drugs)\b',
            r'copyright(?:ed)?|trademark', 
            r'\b(disney|marvel|pixar|star wars|coca.?cola|pepsi|nike|adidas)\b'
        ]
        
        # List of sensitive brand names that might trigger rejections
        self.sensitive_brands = [
            'disney', 'coca-cola', 'coke', 'pepsi', 'marvel', 'playboy', 
            'louis vuitton', 'gucci', 'chanel', 'prada', 'rolex', 
            'nike', 'adidas', 'starbucks', 'mcdonalds', 'ferrari'
        ]
        
        # Safe phrasings to replace problematic terms
        self.safe_replacements = {
            'branded': 'premium',
            'logo': 'emblem',
            'mascot': 'symbol',
            'character': 'design element',
            'copyrighted': 'distinctive',
            'trademarked': 'signature'
        }
    
    def sanitize_image_prompt(self, prompt: str, brand: str = None) -> str:
        """Sanitize image generation prompt to avoid content policy violations"""
        
        # Original prompt for logging
        original = prompt
        
        # Check for restricted patterns
        for pattern in self.restricted_patterns:
            prompt = re.sub(pattern, '[appropriate content]', prompt, flags=re.IGNORECASE)
        
        # If specific brand is causing issues
        if brand:
            brand_lower = brand.lower()
            if any(sensitive in brand_lower for sensitive in self.sensitive_brands):
                # Replace with a generic term
                prompt = prompt.replace(brand, 'premium brand')
        
        # Replace problematic terms with safe alternatives
        for term, replacement in self.safe_replacements.items():
            prompt = re.sub(r'\b' + term + r'\b', replacement, prompt, flags=re.IGNORECASE)
        
        # Ensure prompt focuses on the product, not the brand
        prompt = re.sub(r'(logo|mascot|character|icon) of', 'product from', prompt, flags=re.IGNORECASE)
        
        # Add safe generation qualifiers
        prompt += " professional, clean, appropriate for advertising"
        
        # Log if changes were made
        if prompt != original:
            self.logger.info(f"Sanitized prompt: {original} -> {prompt}")
        
        return prompt
    
    def enhance_prompt_for_text_overlay(self, prompt: str) -> str:
        """Enhance prompt to ensure space for text overlay"""
        
        # Request space for text
        text_space_patterns = [
            "with space for text overlay at the top",
            "with clean area for headline text",
            "with negative space for text placement",
            "with minimalist composition allowing for text"
        ]
        
        # Add randomly selected text space pattern
        text_space = random.choice(text_space_patterns)
        
        # Add to prompt if not already mentioned
        if not any(pattern in prompt.lower() for pattern in ["space for text", "area for text", "room for text"]):
            prompt += f", {text_space}"
        
        return prompt