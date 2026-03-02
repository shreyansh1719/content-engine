"""Font configuration settings for typography system"""
import os

# Set the absolute path to your fonts directory
FONTS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# Default fallback fonts that must be available
DEFAULT_FONTS = {
    'headline': 'Arial-Bold.ttf',
    'subheadline': 'Arial.ttf',
    'body': 'Arial.ttf',
    'cta': 'Arial-Bold.ttf',
    'brand': 'Arial-Bold.ttf'
}

# Copy some minimal default fonts to ensure system always has fallbacks
ENSURE_FONTS_EXIST = True