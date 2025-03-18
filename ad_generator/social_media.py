"""
Social media trends analysis for ad optimization
"""
import os
import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

def search_social_media_ads(product: str, brand_name: str = None, industry: str = None) -> Dict[str, Any]:
    """
    Search for and analyze social media ad trends for a product or industry.
    
    Args:
        product: Product name/description
        brand_name: Brand name (optional)
        industry: Industry category (optional)
        
    Returns:
        Dictionary with social media insights
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Try to load real social media data
        insights = _load_social_media_insights(product, industry)
        
        if insights:
            logger.info(f"Loaded real social media insights for {product}")
            return insights
        
        # If no real data, generate insights based on industry and product type
        logger.info(f"Generating synthetic insights for {product} in {industry}")
        return _generate_synthetic_insights(product, brand_name, industry)
        
    except Exception as e:
        logger.error(f"Error searching social media ads: {str(e)}")
        return _default_insights()

def _load_social_media_insights(product: str, industry: str) -> Optional[Dict[str, Any]]:
    """
    Load real social media insights from cached data.
    
    Args:
        product: Product name/description
        industry: Industry category
        
    Returns:
        Dictionary with insights or None if not found
    """
    # Define paths where insights might be stored
    data_dirs = [
        'data/processed',
        'data/training'
    ]
    
    # Look for insights files
    for data_dir in data_dirs:
        if not os.path.exists(data_dir):
            continue
            
        insights_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and 'social' in f]
        
        for file in insights_files:
            try:
                with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
                    insights_data = json.load(f)
                
                # Check if this file has insights for our product/industry
                if 'products' in insights_data:
                    # Check product match
                    for prod in insights_data['products']:
                        if product.lower() in prod.lower():
                            return insights_data.get('insights', {})
                
                if 'industries' in insights_data:
                    # Check industry match
                    for ind in insights_data['industries']:
                        if industry and industry.lower() in ind.lower():
                            return insights_data.get('insights', {})
            
            except Exception:
                continue
    
    return None

def _generate_synthetic_insights(product: str, brand_name: str, industry: str) -> Dict[str, Any]:
    """
    Generate synthetic insights based on industry and product type.
    
    Args:
        product: Product name/description
        brand_name: Brand name
        industry: Industry category
        
    Returns:
        Dictionary with synthetic insights
    """
    # Normalize inputs for matching
    product_lower = product.lower() if product else ""
    industry_lower = industry.lower() if industry else ""
    
    # Technology products
    if any(term in product_lower for term in ["phone", "smartphone", "laptop", "computer", "gadget", "tech"]) or \
       any(term in industry_lower for term in ["tech", "electronics", "digital", "computing"]):
        return {
            "recommended_format": "Product-focused with clean background",
            "text_placement": "centered",
            "text_style": "modern and minimal",
            "key_elements": ["product close-up", "feature highlight", "tech specs"],
            "visual_focus": "product details and screen",
            "color_scheme": "tech blue or minimal dark/white",
            "trending_keywords": ["innovative", "powerful", "seamless", "experience", "smart"],
            "successful_examples": ["Apple product photography with minimal text", 
                                   "Samsung feature highlight approach", 
                                   "Clean UI overlays on tech product images"]
        }
    
    # Fashion/Apparel
    elif any(term in product_lower for term in ["cloth", "fashion", "apparel", "shoe", "dress", "wear"]) or \
         any(term in industry_lower for term in ["fashion", "apparel", "clothing", "footwear"]):
        return {
            "recommended_format": "Lifestyle imagery with model",
            "text_placement": "left or bottom",
            "text_style": "elegant and stylish",
            "key_elements": ["model wearing product", "lifestyle context", "emotional connection"],
            "visual_focus": "product in use and styling",
            "color_scheme": "neutral with brand accent",
            "trending_keywords": ["style", "premium", "essential", "crafted", "design"],
            "successful_examples": ["High-end fashion photography with minimal text", 
                                   "Lifestyle in-context product usage", 
                                   "Aspirational imagery with subtle branding"]
        }
    
    # Beauty/Cosmetics
    elif any(term in product_lower for term in ["beauty", "skin", "cream", "makeup", "cosmetic"]) or \
         any(term in industry_lower for term in ["beauty", "cosmetic", "skin", "personal care"]):
        return {
            "recommended_format": "Clean product photography with ingredients visualization",
            "text_placement": "right or centered",
            "text_style": "elegant and scientific",
            "key_elements": ["product close-up", "texture or application", "results visualization"],
            "visual_focus": "product design and formula",
            "color_scheme": "clean whites/pastels with accent colors",
            "trending_keywords": ["transform", "rejuvenate", "enhance", "protect", "nourish"],
            "successful_examples": ["Clean product against simple background", 
                                   "Before/after subtle suggestion", 
                                   "Ingredient visualization with product"]
        }
    
    # Food/Beverage
    elif any(term in product_lower for term in ["food", "drink", "beverage", "snack", "meal"]) or \
         any(term in industry_lower for term in ["food", "beverage", "restaurant", "grocery"]):
        return {
            "recommended_format": "Appetizing product photography with context",
            "text_placement": "top or bottom",
            "text_style": "fun and inviting",
            "key_elements": ["appealing food presentation", "emotion/enjoyment", "freshness cues"],
            "visual_focus": "product appeal and environment",
            "color_scheme": "warm and appetizing tones",
            "trending_keywords": ["delicious", "fresh", "crafted", "authentic", "quality"],
            "successful_examples": ["Close-up of food with steam/freshness cues", 
                                   "Context environmental shots", 
                                   "People enjoying product (partial shots)"]
        }
    
    # Home/Furniture
    elif any(term in product_lower for term in ["home", "furniture", "decor", "house", "interior"]) or \
         any(term in industry_lower for term in ["home", "furniture", "interior", "decor"]):
        return {
            "recommended_format": "In-context and standalone product photography",
            "text_placement": "bottom or centered",
            "text_style": "clean and sophisticated",
            "key_elements": ["product in context", "detail shots", "lifestyle environment"],
            "visual_focus": "design features and environment",
            "color_scheme": "neutral with warm accents",
            "trending_keywords": ["design", "quality", "comfort", "style", "craftsmanship"],
            "successful_examples": ["Product in beautiful interior setting", 
                                   "Detail shots highlighting quality", 
                                   "Lifestyle context showing usage"]
        }
    
    # Luxury items
    elif any(term in product_lower for term in ["luxury", "premium", "exclusive", "high-end"]) or \
         any(term in industry_lower for term in ["luxury", "premium", "jewelry"]) or \
         (brand_name and any(brand in brand_name.lower() for brand in ["rolex", "louis", "gucci", "prada"])):
        return {
            "recommended_format": "Minimalist product-focused with premium cues",
            "text_placement": "centered or subtle corner",
            "text_style": "elegant and minimal",
            "key_elements": ["product craftsmanship", "subtle luxury cues", "premium materials"],
            "visual_focus": "details and quality",
            "color_scheme": "dark/black with gold or silver accents",
            "trending_keywords": ["craftsmanship", "heritage", "excellence", "exclusive", "timeless"],
            "successful_examples": ["Dramatic lighting on product details", 
                                   "Minimal composition with perfect execution", 
                                   "Subtle luxury environment cues"]
        }
    
    # Default for other products
    else:
        return {
            "recommended_format": "Clean product photography with context",
            "text_placement": "centered",
            "text_style": "professional and balanced",
            "key_elements": ["product clarity", "key feature highlight", "brand presence"],
            "visual_focus": "product benefits",
            "color_scheme": "brand-aligned colors",
            "trending_keywords": ["quality", "innovative", "essential", "value", "premium"],
            "successful_examples": ["Product against clean background", 
                                   "Lifestyle context showing benefits", 
                                   "Professional studio photography"]
        }

def _default_insights() -> Dict[str, Any]:
    """
    Provide default social media insights when no specific matches found.
    
    Returns:
        Dictionary with default insights
    """
    return {
        "recommended_format": "Product-focused with clean background",
        "text_placement": "centered",
        "text_style": "professional and balanced",
        "key_elements": ["product clarity", "key feature highlight", "brand presence"],
        "visual_focus": "product benefits",
        "color_scheme": "brand colors or neutral palette",
    }

def extract_trends_from_marketplace_data(data_folder: str) -> Dict[str, Any]:
    """
    Extract trends from Facebook Marketplace scraper data.
    
    Args:
        data_folder: Folder containing marketplace data
        
    Returns:
        Dictionary with extracted trends
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Find all JSON files in the data folder
        json_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
        
        if not json_files:
            logger.warning(f"No JSON files found in {data_folder}")
            return {}
        
        # Process each file
        combined_data = []
        
        for json_file in json_files:
            try:
                with open(os.path.join(data_folder, json_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    combined_data.extend(data)
                elif isinstance(data, dict) and 'data' in data:
                    combined_data.extend(data['data'])
                elif isinstance(data, dict):
                    combined_data.append(data)
            except Exception as e:
                logger.error(f"Error processing {json_file}: {str(e)}")
        
        # Extract trends from combined data
        if not combined_data:
            return {}
        
        # We'll categorize the data by industry first
        industries = {}
        
        # Process ads to extract trends
        # This is a simplified approach and should be expanded based on your actual data structure
        for ad in combined_data:
            # Extract industry if available
            industry = ad.get('category', 'Unknown')
            
            if industry not in industries:
                industries[industry] = {
                    'ads': [],
                    'title_lengths': [],
                    'image_features': [],
                    'price_points': []
                }
            
            # Add to industry collection
            industries[industry]['ads'].append(ad)
            
            # Extract title length if available
            if 'title' in ad:
                industries[industry]['title_lengths'].append(len(ad['title'].split()))
            
            # Extract price if available
            if 'price' in ad:
                try:
                    price = float(ad['price'].replace('$', '').replace(',', ''))
                    industries[industry]['price_points'].append(price)
                except (ValueError, AttributeError):
                    pass
            
            # Extract image features if available
            if 'image_features' in ad:
                industries[industry]['image_features'].append(ad['image_features'])
        
        # Calculate trends for each industry
        trends = {
            "extraction_date": datetime.now().isoformat(),
            "total_ads_analyzed": len(combined_data),
            "industries": {}
        }
        
        for industry, data in industries.items():
            industry_trends = {
                "ad_count": len(data['ads']),
                "avg_title_length": sum(data['title_lengths']) / len(data['title_lengths']) if data['title_lengths'] else 0,
                "common_price_ranges": _calculate_price_ranges(data['price_points']) if data['price_points'] else {},
                "visual_trends": _extract_visual_trends(data['image_features']) if data['image_features'] else {}
            }
            
            trends["industries"][industry] = industry_trends
        
        # Save trends to file
        _save_trends_to_file(trends, data_folder)
        
        return trends
        
    except Exception as e:
        logger.error(f"Error extracting trends from marketplace data: {str(e)}")
        return {}

def _calculate_price_ranges(price_points: List[float]) -> Dict[str, Any]:
    """
    Calculate common price ranges from price points.
    
    Args:
        price_points: List of prices
        
    Returns:
        Dictionary with price statistics
    """
    if not price_points:
        return {}
    
    # Sort prices
    price_points.sort()
    
    # Calculate statistics
    min_price = min(price_points)
    max_price = max(price_points)
    avg_price = sum(price_points) / len(price_points)
    median_price = price_points[len(price_points) // 2]
    
    # Define price brackets
    brackets = []
    bracket_size = (max_price - min_price) / 5 if max_price > min_price else 10
    
    for i in range(5):
        lower = min_price + i * bracket_size
        upper = lower + bracket_size
        count = sum(1 for p in price_points if lower <= p < upper)
        brackets.append({
            "range": f"${lower:.2f} - ${upper:.2f}",
            "count": count,
            "percentage": (count / len(price_points)) * 100
        })
    
    return {
        "min_price": min_price,
        "max_price": max_price,
        "average_price": avg_price,
        "median_price": median_price,
        "price_brackets": brackets
    }

def _extract_visual_trends(image_features: List[Dict]) -> Dict[str, Any]:
    """
    Extract visual trends from image features.
    
    Args:
        image_features: List of image features
        
    Returns:
        Dictionary with visual trends
    """
    # This would normally analyze actual image features
    # As a placeholder, we'll return some reasonable defaults
    return {
        "dominant_colors": [
            {"color": "Blue", "frequency": "27%"},
            {"color": "White", "frequency": "22%"},
            {"color": "Black", "frequency": "18%"}
        ],
        "common_compositions": [
            {"type": "Center focus", "frequency": "45%"},
            {"type": "Rule of thirds", "frequency": "30%"},
            {"type": "Full product view", "frequency": "25%"}
        ],
        "background_types": [
            {"type": "Solid color", "frequency": "55%"},
            {"type": "Contextual", "frequency": "25%"},
            {"type": "Gradient", "frequency": "20%"}
        ]
    }

def _save_trends_to_file(trends: Dict[str, Any], base_folder: str) -> None:
    """
    Save extracted trends to file.
    
    Args:
        trends: Dictionary of trends
        base_folder: Base folder for saving
    """
    output_folder = os.path.join(base_folder, 'processed')
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"social_trends_{timestamp}.json"
    
    with open(os.path.join(output_folder, filename), 'w', encoding='utf-8') as f:
        json.dump(trends, f, indent=2)