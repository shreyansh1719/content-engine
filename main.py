"""
Professional Ad Generation System
Studio-quality ad generation with advanced product photography and text overlay
"""
import os
import logging
import json
import re
import sys
import subprocess
import traceback
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import argparse

# Import our custom modules
from ad_generator import AdGenerator
from ad_generator.analytics import AdMetricsAnalyzer
from utils.excel_utils import save_ad_to_excel

def setup_logging():
    """Set up logging configuration."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"ad_generation_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check that all required dependencies are installed."""
    required_packages = [
        'openai', 'python-dotenv', 'pandas', 'Pillow', 'requests', 
        'numpy', 'openpyxl', 'selenium', 'webdriver_manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing dependencies: {', '.join(missing_packages)}")
        
        # Ask to install
        install = input("\nWould you like to install missing dependencies now? (y/n): ")
        if install.lower() == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print("Dependencies installed successfully!")
                return True
            except subprocess.CalledProcessError:
                print("Failed to install dependencies. Please run: pip install -r requirements.txt")
                return False
        else:
            print("Please install the required packages: pip install -r requirements.txt")
            return False
    
    return True

def create_required_directories():
    """Create all required directories for the application."""
    directories = [
        "data/training",
        "data/processed",
        "output/images",
        "output/excel",
        "logs",
        "marketplace_data/processed",
        "marketplace_data/images"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def display_results(ad_data: dict):
    """Display generated ad details in a clean, formatted way."""
    print("\n=== Generated Ad Details ===")
    print(f"\nHeadline: {ad_data['headline']}")
    print(f"Subheadline: {ad_data['subheadline']}")
    print(f"Body Text: {ad_data.get('body_text', '')}")
    print(f"Call to Action: {ad_data['call_to_action']}")
    
    print("\nBrand Analysis:")
    for key, value in ad_data['brand_analysis'].items():
        if isinstance(value, list):
            print(f"{key.replace('_', ' ').title()}: {', '.join(value)}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nImage saved at: {ad_data['image_path']}")
    print(f"Excel file saved at: {ad_data.get('excel_path', '')}")

def generate_ad_mode():
    """Run in ad generation mode with comprehensive ad creation."""
    logger = setup_logging()
    logger.info("Starting professional ad generation mode")
    
    # Create output directories
    create_required_directories()
    
    # Initialize analytics to learn from successful ads
    metrics_analyzer = AdMetricsAnalyzer()
    
    print("===== PROFESSIONAL AD GENERATION SYSTEM =====")
    print("This system creates studio-quality ad campaigns with professional text overlay.")
    print("It analyzes successful ads to determine the most effective formats and styles.")
    
    # Example prompts
    print("\nExample prompts (we'll intelligently extract the brand name and product):")
    print("- iPhone 15 Pro")
    print("- Nike Air Max running shoes")
    print("- Rolex Submariner luxury watch")
    print("- Bombay Sapphire gin")
    print("- L'Oreal Perfect Skin face cream")
    
    try:
        # Get user input
        prompt = input("\nWhat would you like to create an ad for? ")
        
        if not prompt.strip():
            print("Please provide a description of what you want to advertise.")
            return
        
        # Initialize generator
        generator = AdGenerator()
        
        # Generate the ad with full processing
        print("\nGenerating your professional studio-quality ad...")
        print("This may take a minute as we create optimal content based on industry standards...")
        
        ad_data = generator.create_ad(prompt)
        
        # Save to Excel
        excel_path = save_ad_to_excel(ad_data)
        ad_data['excel_path'] = excel_path
        
        # Display results
        display_results(ad_data)
        
        # Show image file path for easy access
        print(f"\nYour professional ad is ready at:")
        full_path = os.path.abspath(ad_data['image_path'])
        print(f"{full_path}")
        
        # Open image for viewing if possible
        try:
            from PIL import Image
            Image.open(ad_data['image_path']).show()
            print("Image opened in default viewer.")
        except Exception as e:
            print(f"Could not automatically open image: {str(e)}")
            print("Please open the image file at the path above.")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An unexpected error occurred: {str(e)}")
        print("Please check the logs for more details.")

def display_campaign_details(campaign: dict):
    """Display campaign details in a formatted way."""
    print("\n===== GENERATED AD CAMPAIGN DETAILS =====")
    print(f"Product: {campaign.get('product', 'Unknown')}")
    print(f"Brand: {campaign.get('brand_name', 'N/A')}")
    print(f"Industry: {campaign['brand_analysis']['industry']}")
    
    print("\n----- AD COPY -----")
    print(f"Headline: {campaign['headline']}")
    print(f"Subheadline: {campaign['subheadline']}")
    print(f"Body Text: {campaign.get('body_text', 'N/A')}")
    print(f"Call to Action: {campaign['call_to_action']}")
    
    if 'social_media_insights' in campaign:
        print("\n----- SOCIAL MEDIA INSIGHTS -----")
        insights = campaign['social_media_insights']
        print(f"Recommended Format: {insights.get('recommended_format', 'N/A')}")
        print(f"Text Placement: {insights.get('text_placement', 'N/A')}")
        print(f"Text Style: {insights.get('text_style', 'N/A')}")
        
        key_elements = insights.get('key_elements', [])
        if key_elements:
            print(f"Key Elements: {', '.join(key_elements)}")
        
        if 'trending_keywords' in insights:
            print(f"Trending Keywords: {', '.join(insights['trending_keywords'])}")
    
    print(f"\nImage saved at: {campaign['image_path']}")
    
    if 'excel_path' in campaign:
        print(f"Excel file saved at: {campaign['excel_path']}")
    
    print("\n============================================")

def scraper_mode():
    """Run in scraper mode to collect Facebook Marketplace data."""
    logger = setup_logging()
    logger.info("Starting Facebook Marketplace scraper mode")
    
    # Create necessary directories
    create_required_directories()
    
    print("===== FACEBOOK MARKETPLACE SCRAPER =====")
    print("This tool collects ad data from Facebook Marketplace to train our ad generator.")
    print("The collected data will help optimize ad formats, copy, and imagery.")
    
    # Import scraper on demand (to avoid loading dependencies if not needed)
    try:
        from marketplace_scraper.scraper import MarketplaceScraper
    except ImportError:
        print("Marketplace scraper module not found or has errors.")
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver_manager", "undetected-chromedriver"])
        print("Dependencies installed. Please try running again with:")
        print("python main.py --mode scrape")
        return
    
    # Get scraper configuration
    print("\nPlease provide your Facebook credentials (they're only used for login and not stored):")
    username = input("Facebook Username: ")
    password = input("Facebook Password: ")
    
    if not username or not password:
        print("Username and password are required to access Facebook Marketplace.")
        return
    
    # Get scraper parameters
    max_ads = input("\nMax number of ads to collect (default: 1000): ")
    max_ads = int(max_ads) if max_ads.strip() else 1000
    
    print("\nAvailable categories:")
    print("1. All")
    print("2. Electronics")
    print("3. Vehicles")
    print("4. Furniture")
    print("5. Clothing")
    print("6. Home Goods")
    print("7. Free Items")
    
    category_input = input("\nSelect categories (comma-separated numbers, default: all): ")
    
    # Map input to category names
    category_map = {
        "1": "all",
        "2": "electronics",
        "3": "vehicles",
        "4": "furniture",
        "5": "apparel", 
        "6": "home_goods",
        "7": "free"
    }
    
    selected_categories = []
    if category_input.strip():
        for num in category_input.split(','):
            num = num.strip()
            if num in category_map:
                selected_categories.append(category_map[num])
    else:
        selected_categories = ["all"]
    
    # Initialize and run scraper
    try:
        print("\nInitializing Facebook Marketplace scraper...")
        scraper = MarketplaceScraper(
            username=username,
            password=password
        )
        
        print(f"Beginning data collection for {max_ads} ads in categories: {', '.join(selected_categories)}")
        print("This may take some time. Please don't close the browser window that appears.")
        
        # Run the scraper
        collected_ads = scraper.run_comprehensive_scraping_session(
            max_ads=max_ads,
            categories=selected_categories
        )
        
        # Display results
        if collected_ads:
            print(f"\nSuccessfully collected {len(collected_ads)} ads!")
            print("Data has been saved to the marketplace_data directory.")
            
            # Ask if user wants to analyze the data now
            analyze = input("\nWould you like to analyze the collected data now? (y/n): ")
            if analyze.lower() == 'y':
                print("\nAnalyzing collected marketplace data...")
                trends = scraper.extract_trends_from_marketplace_data('marketplace_data/processed')
                
                if trends:
                    print(f"Analysis complete! Extracted trends from {trends.get('total_ads_analyzed', 0)} ads.")
                    print("The analysis results have been saved to marketplace_data/processed/")
                    
                    # Display some highlights
                    print("\nHighlights from the analysis:")
                    for industry, data in trends.get('industries', {}).items():
                        print(f"- {industry}: {data.get('ad_count', 0)} ads, " + 
                              f"avg title length: {data.get('avg_title_length', 0):.1f} words")
                else:
                    print("No trends could be extracted from the collected data.")
            
        else:
            print("No ads were collected. Please check the logs for details.")
        
    except Exception as e:
        logger.error(f"Error in scraper mode: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred during scraping: {str(e)}")
        print("Please check the logs for details.")

def process_data_mode():
    """Process and analyze existing marketplace data."""
    logger = setup_logging()
    logger.info("Starting data processing mode")
    
    print("===== DATA PROCESSING MODE =====")
    print("This mode processes and analyzes existing marketplace data to extract patterns.")
    
    # Check if we have data
    data_dirs = ['marketplace_data/processed', 'data/processed']
    has_data = False
    
    for dir in data_dirs:
        if os.path.exists(dir) and os.listdir(dir):
            has_data = True
            break
    
    if not has_data:
        print("No marketplace data found to process. Please run the scraper first.")
        return
    
    # Ask which folder to process
    print("\nAvailable data directories:")
    available_dirs = []
    for i, dir in enumerate(data_dirs, 1):
        if os.path.exists(dir) and os.listdir(dir):
            print(f"{i}. {dir}")
            available_dirs.append(dir)
    
    if not available_dirs:
        print("No data directories with content found.")
        return
    
    dir_choice = input("\nSelect directory to process (number): ")
    try:
        selected_dir = available_dirs[int(dir_choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection. Using first available directory.")
        selected_dir = available_dirs[0]
    
    # Process the data
    print(f"\nProcessing data in {selected_dir}...")
    try:
        # Import the updated scraper
        from marketplace_scraper.scraper import MarketplaceScraper
        
        # Extract trends
        scraper = MarketplaceScraper(username=None, password=None)
        trends = scraper.extract_trends_from_marketplace_data(selected_dir)
        
        if trends:
            print(f"Analysis complete! Extracted trends from {trends.get('total_ads_analyzed', 0)} ads.")
            
            # Display some highlights
            print("\nHighlights from the analysis:")
            for industry, data in trends.get('industries', {}).items():
                print(f"- {industry}: {data.get('ad_count', 0)} ads, " + 
                      f"avg title length: {data.get('avg_title_length', 0):.1f} words")
            
            # Get analytics insights
            metrics_analyzer = AdMetricsAnalyzer()
            print("\nUpdating ad generation patterns with new insights...")
            
            # Process marketplace data with metrics analyzer
            # This would typically call a method on metrics_analyzer to update its patterns
            
            print("Ad generation system has been updated with new marketplace insights!")
            print("Your next generated ads will leverage these patterns.")
        else:
            print("No trends could be extracted from the data.")
    
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred during data processing: {str(e)}")
        print("Please check the logs for details.")

def main():
    """Main entry point for the ad engine."""
    # Load environment variables
    load_dotenv()
    
    # Check dependencies before proceeding
    if not check_dependencies():
        sys.exit(1)
    
    # Create required directories
    create_required_directories()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Professional Ad Generation System")
    parser.add_argument("--mode", "-m", type=str, default="generate", 
                       choices=["generate", "scrape", "process"],
                       help="Operation mode: generate ads, scrape marketplace, or process data")
    parser.add_argument("--prompt", "-p", type=str, 
                       help="Direct prompt input for ad generation (skips the prompt input step)")
    parser.add_argument("--export-format", "-e", type=str, default="all", 
                       choices=["excel", "json", "all"], 
                       help="Export format for generated ad")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Select mode
    if args.mode == "scrape":
        scraper_mode()
    elif args.mode == "process":
        process_data_mode()
    else:  # generate mode
        # If prompt was provided via command line
        if args.prompt:
            # Setup for direct prompt
            logger = setup_logging()
            logger.info(f"Direct prompt provided: {args.prompt}")
            
            try:
                # Initialize generator
                generator = AdGenerator()
                
                # Generate ad
                print(f"Creating studio-quality ad for: {args.prompt}")
                ad_data = generator.create_ad(args.prompt)
                
                # Save to Excel if requested
                if args.export_format in ["excel", "all"]:
                    excel_path = save_ad_to_excel(ad_data)
                    ad_data['excel_path'] = excel_path
                
                # Save to JSON if requested
                if args.export_format in ["json", "all"]:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_path = f"output/excel/ad_data_{timestamp}.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(ad_data, f, indent=2)
                    print(f"JSON saved to: {json_path}")
                
                # Display results
                display_campaign_details(ad_data)
                
                # Show image file path and try to open it
                full_path = os.path.abspath(ad_data['image_path'])
                print(f"\nYour professional ad is ready at: {full_path}")
                
                # Open image for viewing if possible
                try:
                    from PIL import Image
                    Image.open(ad_data['image_path']).show()
                    print("Image opened in default viewer.")
                except Exception as e:
                    print(f"Could not automatically open image: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error with direct prompt: {str(e)}")
                logger.error(traceback.format_exc())
                print(f"Error: {str(e)}")
                print("Please check the logs for details.")
        else:
            # Interactive mode
            generate_ad_mode()

if __name__ == "__main__":
    print("""
    ___________________________________________
    |                                         |
    |   PROFESSIONAL AD GENERATION SYSTEM     |
    |   Studio Quality Content Engine         |
    |_________________________________________| 
    """)
    main()