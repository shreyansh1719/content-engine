"""
New Product Dataset Generator
Creates diverse product datasets for batch ad testing
"""
import json
import uuid
from datetime import datetime

def generate_new_product_dataset():
    """Generate a diverse set of new product categories for batch testing"""
    
    products = [
        # Tech Wearables Category
        {
            "product_id": f"smartwatch_{uuid.uuid4().hex[:6]}",
            "product_name": "QuantumWatch X1",
            "brand_name": "NexTech",
            "description": "health-focused smartwatch with ECG monitoring, sleep tracking and 7-day battery life",
            "tone": "professional",
            "visual_style": "sleek",
            "platform": "LinkedIn",
            "industry": "health technology",
            "principle": "Credible",
            "target_audience": "health-conscious professionals aged 30-55",
            "key_benefits": [
                "continuous health monitoring",
                "professional design",
                "week-long battery life"
            ]
        },
        
        # Sustainable Products Category
        {
            "product_id": f"eco_bottle_{uuid.uuid4().hex[:6]}",
            "product_name": "EverGreen Thermal Bottle",
            "brand_name": "EcoFlow",
            "description": "plant-based thermal bottle that maintains temperature for 24 hours and biodegrades after disposal",
            "tone": "conscious",
            "visual_style": "minimalist",
            "platform": "Instagram",
            "industry": "sustainable products",
            "principle": "Unexpected",
            "target_audience": "environmentally conscious consumers aged 18-40",
            "key_benefits": [
                "zero plastic footprint",
                "24-hour temperature retention",
                "biodegradable materials"
            ]
        },
        
        # Luxury Fragrance Category
        {
            "product_id": f"fragrance_{uuid.uuid4().hex[:6]}",
            "product_name": "Lumière Noire",
            "brand_name": "Maison Laurent",
            "description": "premium unisex fragrance with notes of sandalwood, bergamot and vanilla in a handcrafted glass bottle",
            "tone": "luxurious",
            "visual_style": "elegant",
            "platform": "Facebook",
            "industry": "luxury beauty",
            "principle": "Emotional",
            "target_audience": "luxury shoppers and fragrance enthusiasts",
            "key_benefits": [
                "signature scent composition",
                "artisanal craftsmanship",
                "long-lasting formula"
            ]
        },
        
        # SaaS Product Category
        {
            "product_id": f"saas_tool_{uuid.uuid4().hex[:6]}",
            "product_name": "DataSync Pro",
            "brand_name": "CloudWorks",
            "description": "cloud-based productivity suite with real-time collaboration, automated workflows and advanced data security",
            "tone": "authoritative",
            "visual_style": "modern",
            "platform": "Google",
            "industry": "B2B software",
            "principle": "Simple",
            "target_audience": "small to medium businesses and remote teams",
            "key_benefits": [
                "seamless team collaboration",
                "workflow automation",
                "enterprise-grade security"
            ]
        },
        
        # Plant-Based Food Category
        {
            "product_id": f"plant_protein_{uuid.uuid4().hex[:6]}",
            "product_name": "GreenProtein Complete",
            "brand_name": "VitalHarvest",
            "description": "organic plant-based protein powder with complete amino acid profile, probiotics and zero sugar",
            "tone": "energetic",
            "visual_style": "vibrant",
            "platform": "TikTok",
            "industry": "health food",
            "principle": "Concrete",
            "target_audience": "fitness enthusiasts and health-conscious consumers",
            "key_benefits": [
                "complete plant protein",
                "gut-friendly probiotics",
                "clean ingredient list"
            ]
        },
        
        # Home Decor Category
        {
            "product_id": f"smart_lighting_{uuid.uuid4().hex[:6]}",
            "product_name": "LumenArt Smart Lighting",
            "brand_name": "HomeCanvas",
            "description": "artistic smart lighting system with customizable colors, schedules and voice control integration",
            "tone": "inspirational",
            "visual_style": "artistic",
            "platform": "Pinterest",
            "industry": "home decor",
            "principle": "Emotional",
            "target_audience": "home design enthusiasts and tech-savvy homeowners",
            "key_benefits": [
                "mood-enhancing lighting",
                "artistic design statement",
                "smart home integration"
            ]
        }
    ]
    
    # Create the dataset structure
    dataset = {
        "products": products,
        "metadata": {
            "count": len(products),
            "categories": ["tech wearables", "sustainable products", "luxury fragrance", 
                           "SaaS", "plant-based food", "home decor"],
            "created_at": datetime.now().isoformat(),
            "version": "2.0"
        }
    }
    
    # Save to JSON file
    output_path = "new_product_dataset.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Created new dataset with {len(products)} diverse products at {output_path}")
    return output_path

if __name__ == "__main__":
    generate_new_product_dataset()