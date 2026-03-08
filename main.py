"""
Professional Ad Generation System
Studio-quality ad generation with advanced product photography and text overlay,
powered by data-driven insights from high-performing ads
"""
import os
import logging
import json
import argparse
import sys
import subprocess
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add debug print at the top
print("Starting Professional Ad Generation System...")

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
        'numpy', 'openpyxl', 'selenium', 'webdriver-manager',
        'undetected-chromedriver', 'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
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
        "data/raw",
        "data/insights",
        "output/images",
        "output/excel",
        "logs",
        "marketplace_data/processed",
        "marketplace_data/images"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def display_results(ad_data: Dict[str, Any]):
    """Display generated ad details in a clean, formatted way."""
    print("\n=== Generated Ad Details ===")
    print(f"\nHeadline: {ad_data['headline']}")
    print(f"Subheadline: {ad_data.get('subheadline', 'N/A')}")
    print(f"Body Text: {ad_data.get('body_text', 'N/A')}")
    print(f"Call to Action: {ad_data.get('call_to_action', 'N/A')}")
    
    if 'brand_analysis' in ad_data:
        print("\nBrand Analysis:")
        for key, value in ad_data['brand_analysis'].items():
            if isinstance(value, list):
                print(f"{key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nImage saved at: {ad_data.get('image_path', 'N/A')}")
    print(f"Excel file saved at: {ad_data.get('excel_path', 'N/A')}")

def generate_ad_mode(args):
    """Run in ad generation mode with comprehensive ad creation."""
    # Import format_exc directly to avoid issues with module name
    from traceback import format_exc
    
    logger = setup_logging()
    logger.info("Starting professional ad generation mode")
    
    # Create output directories
    create_required_directories()
    
    try:
        # Import here to avoid loading until needed
        from ad_generator import AdGenerator
        from ad_generator.analytics import AdMetricsAnalyzer
        from utils.excel_utils import save_ad_to_excel
        
        # Initialize analytics to learn from successful ads
        metrics_analyzer = AdMetricsAnalyzer()
        
        print("===== PROFESSIONAL AD GENERATION SYSTEM =====")
        print("This system creates studio-quality ad campaigns with professional text overlay.")
        print("It analyzes successful ads to determine the most effective formats and styles.")
        
        # Example prompts
        print("\nExample prompts:")
        print("- iPhone 15 Pro with stunning camera capabilities")
        print("- Nike Air Max running shoes for professional athletes")
        print("- L'Oreal Perfect Skin face cream with hyaluronic acid")
        print("- Eco-friendly bamboo water bottle by GreenLife")
        print("- Wireless noise-cancelling headphones by Sony")
        
        # Get user input - from args or interactive prompt
        prompt = args.prompt if hasattr(args, 'prompt') and args.prompt else input("\nWhat would you like to create an ad for? ")
        
        if not prompt.strip():
            print("Please provide a description of what you want to advertise.")
            return
        
        # Check for product image path
        product_image_path = None
        if hasattr(args, 'product_image') and args.product_image:
            product_image_path = args.product_image
            if not os.path.exists(product_image_path):
                print(f"Warning: Product image not found at {product_image_path}")
                use_image_anyway = input("Do you want to continue without the product image? (y/n): ")
                if use_image_anyway.lower() != 'y':
                    return
                product_image_path = None
            else:
                print(f"Using product image: {product_image_path}")
                # Basic image validation
                try:
                    from PIL import Image
                    img = Image.open(product_image_path)
                    img.verify()  # Verify it's a valid image
                    # Check image size
                    img = Image.open(product_image_path)  # Need to reopen after verify
                    if img.width < 300 or img.height < 300:
                        print(f"Warning: Image is small ({img.width}x{img.height}). Results may be lower quality.")
                    print(f"Image dimensions: {img.width}x{img.height}, format: {img.format}")
                except Exception as e:
                    print(f"Error validating image: {e}")
                    use_anyway = input("Image may be invalid. Continue anyway? (y/n): ")
                    if use_anyway.lower() != 'y':
                        return
        else:
            # If no image provided via args, ask if user wants to provide one
            use_product_image = input("\nWould you like to use your own product image for the ad? (y/n): ")
            if use_product_image.lower() == 'y':
                product_image_path = input("Enter the path to your product image: ")
                if not os.path.exists(product_image_path):
                    print(f"Image not found at {product_image_path}. Continuing without product image.")
                    product_image_path = None
                else:
                    print(f"Using product image: {product_image_path}")
        
        # Initialize generator
        generator = AdGenerator()
        
        # Enhance the typography system with the improved version
        try:
            from ad_generator.typography.typography_integration import integrate_enhanced_typography
            logger.info("Enhancing typography system for better text placement and effects")
            if hasattr(generator, 'image_generator'):
                generator.image_generator = integrate_enhanced_typography(generator.image_generator)
                logger.info("Typography system enhanced successfully")
            else:
                logger.warning("Could not enhance typography system - image_generator not found")
        except Exception as e:
            logger.warning(f"Could not enhance typography system: {str(e)}")
            logger.debug(format_exc())
        
        # Generate the ad with full processing
        print("\nGenerating your professional studio-quality ad...")
        
        if product_image_path:
            print("Processing your product image:")
            print("1. Removing background from product")
            print("2. Enhancing product image quality")
            print("3. Generating context-aware background")
            print("4. Integrating product with background")
            print("5. Applying professional typography")
            print("\nThis process may take a few minutes. Please be patient...")
        else:
            print("Creating a complete AI-generated ad based on your description...")
            print("This may take a minute as we create optimal content based on industry standards...")
        
        # Generate ad with the product image if provided
        ad_data = generator.create_ad(prompt, product_image_path)
        
        # Save to Excel if requested
        if hasattr(args, 'export_format') and args.export_format in ["excel", "all"]:
            excel_path = save_ad_to_excel(ad_data)
            ad_data['excel_path'] = excel_path
        
        # Save to JSON if requested
        if hasattr(args, 'export_format') and args.export_format in ["json", "all"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"output/excel/ad_data_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(ad_data, f, indent=2)
            print(f"JSON saved to: {json_path}")
        
        # Display results
        display_results(ad_data)
        
        # If product image was used, include additional information
        if product_image_path and 'used_product_image' in ad_data and ad_data['used_product_image']:
            print("\nProduct Image Processing:")
            print(f"Original image: {product_image_path}")
            if 'enhanced_product_path' in ad_data:
                print(f"Enhanced product: {ad_data['enhanced_product_path']}")
            if 'background_path' in ad_data:
                print(f"Generated background: {ad_data['background_path']}")
        
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
            logger.warning(f"Could not automatically open image: {str(e)}")
            print(f"Could not automatically open image: {str(e)}")
            print("Please open the image file at the path above.")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        logger.error(format_exc())
        print(f"An unexpected error occurred: {str(e)}")
        print("Please check the logs for more details.")



def run_ad_insights_scraper(args):
    """Run the comprehensive ad insights scraper to collect high-performing ads."""
    logger = setup_logging()
    logger.info("Starting Ad Insights Scraper mode")
    
    # Create required directories
    create_required_directories()
    
    print("===== AD INSIGHTS SCRAPER =====")
    print("This system collects high-performing ads from multiple platforms for analysis and training.")
    
    try:
        # Import ScraperController
        from ad_insights_scraper.scraper_controller import ScraperController
        
        # Initialize the controller
        controller = ScraperController(output_dir='data')
        
        # Get keywords to search for
        keywords = args.keywords if hasattr(args, 'keywords') else None
        if not keywords:
            print("\nEnter keywords to search for (brands, products, industries):")
            print("Examples: iPhone, Nike shoes, skincare products, protein supplements")
            keywords_input = input("\nKeywords (comma-separated): ")
            keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        
        if not keywords:
            print("No keywords provided. Exiting.")
            return
        
        # Determine which platforms to scrape
        platforms = []
        if (hasattr(args, 'all_platforms') and args.all_platforms) or (hasattr(args, 'facebook') and args.facebook):
            platforms.append("facebook")
        if (hasattr(args, 'all_platforms') and args.all_platforms) or (hasattr(args, 'reddit') and args.reddit):
            platforms.append("reddit")
        if (hasattr(args, 'all_platforms') and args.all_platforms) or (hasattr(args, 'adspy') and args.adspy):
            platforms.append("adspy")
            
        # If no platforms specified, ask user
        if not platforms:
            print("\nWhich platforms would you like to scrape?")
            print("1. Facebook Ads")
            print("2. Reddit Content")
            print("3. AdSpy (requires credentials)")
            print("4. All available platforms")
            
            platform_input = input("\nEnter platform numbers (comma-separated): ")
            platform_nums = [num.strip() for num in platform_input.split(',') if num.strip()]
            
            if '1' in platform_nums or '4' in platform_nums:
                platforms.append("facebook")
            if '2' in platform_nums or '4' in platform_nums:
                platforms.append("reddit")
            if '3' in platform_nums or '4' in platform_nums:
                platforms.append("adspy")
        
        # Get limit parameter
        limit = args.limit if hasattr(args, 'limit') else 100
        
        # Scrape from specified platforms
        all_data = {}
        
        # Facebook scraping
        if "facebook" in platforms:
            print(f"\nScraping Facebook Ads for: {', '.join(keywords)}")
            print("This can take some time. Please be patient...")
            
            facebook_ads = controller.run_facebook_scraper(
                keywords=keywords,
                countries=args.countries if hasattr(args, 'countries') else ['US'],
                max_ads=limit
            )
            
            all_data['facebook'] = facebook_ads
            print(f"Collected {len(facebook_ads)} Facebook ads")
        
        # Reddit scraping
        if "reddit" in platforms:
            print(f"\nScraping Reddit for: {', '.join(keywords)}")
            
            subreddits = args.subreddits if hasattr(args, 'subreddits') else None
            if not subreddits:
                print("Finding relevant subreddits...")
                # Controller will find relevant subreddits automatically
            
            reddit_posts, reddit_comments = controller.run_reddit_scraper(
                keywords=keywords,
                subreddits=subreddits,
                limit=limit
            )
            
            all_data['reddit_posts'] = reddit_posts
            all_data['reddit_comments'] = reddit_comments
            
            print(f"Collected {len(reddit_posts)} Reddit posts and {len(reddit_comments)} comments")
        
        # AdSpy scraping (if credentials available)
        if "adspy" in platforms:
            adspy_username = (args.adspy_username if hasattr(args, 'adspy_username') else None) or os.getenv('ADSPY_USERNAME')
            adspy_password = (args.adspy_password if hasattr(args, 'adspy_password') else None) or os.getenv('ADSPY_PASSWORD')
            
            if not adspy_username or not adspy_password:
                print("\nAdSpy credentials required for scraping. Please provide:")
                adspy_username = input("AdSpy Username: ")
                adspy_password = input("AdSpy Password: ")
            
            if adspy_username and adspy_password:
                print(f"\nScraping AdSpy for: {', '.join(keywords)}")
                
                controller.set_adspy_credentials(adspy_username, adspy_password)
                adspy_ads, adspy_insights = controller.run_adspy_scraper(
                    keywords=keywords,
                    platforms=args.adspy_platforms if hasattr(args, 'adspy_platforms') else ['facebook', 'instagram'],
                    limit=limit
                )
                
                all_data['adspy_ads'] = adspy_ads
                all_data['adspy_insights'] = adspy_insights
                
                print(f"Collected {len(adspy_ads)} ads from AdSpy")
            else:
                print("Skipping AdSpy scraping due to missing credentials")
        
        # Process data
        if any(all_data.values()):
            print("\nProcessing collected data...")
            results = controller.process_all_data()
            
            print("\nExtracting insights from processed data...")
            insights = controller.extract_insights()
            
            print(f"\nSuccessfully processed data and extracted {len(insights)} insights")
            
            # Ask about training
            if (hasattr(args, 'auto_train') and args.auto_train) or (input("\nWould you like to prepare training data now? (y/n): ").lower() == 'y'):
                from ad_insights_scraper.training_pipeline import TrainingPipeline
                
                print("\nPreparing training data...")
                pipeline = TrainingPipeline(
                    input_dir='data',
                    output_dir='data/models',
                    model_type=args.model_type if hasattr(args, 'model_type') else 'gpt'
                )
                
                examples = pipeline.prepare_training_data()
                print(f"Generated {len(examples)} training examples")
                
                if (hasattr(args, 'auto_train') and args.auto_train) or (input("\nProceed with model training? (y/n): ").lower() == 'y'):
                    print("\nTraining model on collected data...")
                    print("This may take some time. Please be patient...")
                    
                    results = pipeline.train_model()
                    print(f"Training complete with loss: {results.get('training_loss', 'N/A')}")
        else:
            print("\nNo data was collected from any platform.")
        
    except Exception as e:
        logger.error(f"Error in ad insights scraper: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred: {str(e)}")
        print("Please check the logs for details.")


def run_marketplace_scraper(args):
    """Run the Facebook Marketplace scraper to collect ad data."""
    logger = setup_logging()
    logger.info("Starting Marketplace scraper mode")
    
    # Create necessary directories
    create_required_directories()
    
    print("===== FACEBOOK MARKETPLACE SCRAPER =====")
    print("This tool collects ad data from Facebook Marketplace to analyze effective ad patterns.")
    
    try:
        # Import marketplace scraper
        from marketplace_scraper.scraper import MarketplaceScraper
        
        # Get credentials - from args, environment, or user input
        username = (args.facebook_username if hasattr(args, 'facebook_username') else None) or os.getenv('FACEBOOK_USERNAME')
        password = (args.facebook_password if hasattr(args, 'facebook_password') else None) or os.getenv('FACEBOOK_PASSWORD')
        
        if not username or not password:
            print("\nFacebook credentials required for Marketplace access:")
            username = input("Facebook Username: ")
            password = input("Facebook Password: ")
        
        if not username or not password:
            print("Username and password are required to access Facebook Marketplace.")
            return
        
        # Get scraper parameters
        max_ads = args.limit if hasattr(args, 'limit') else 100
        
        # Get categories
        categories = args.categories if hasattr(args, 'categories') else None
        if not categories:
            print("\nAvailable categories:")
            print("1. All Products")
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
            
            if category_input.strip():
                categories = []
                for num in category_input.split(','):
                    num = num.strip()
                    if num in category_map:
                        categories.append(category_map[num])
            else:
                categories = ["all"]
        
        # Initialize and run scraper
        print("\nInitializing Facebook Marketplace scraper...")
        scraper = MarketplaceScraper(
            username=username,
            password=password,
            output_dir='marketplace_data',
            headless=not (hasattr(args, 'show_browser') and args.show_browser)
        )
        
        print(f"Beginning data collection for {max_ads} ads in categories: {', '.join(categories)}")
        print("This may take some time. Please don't close the browser window that appears.")
        
        # Run the scraper
        collected_ads = scraper.run_comprehensive_scraping_session(
            max_ads=max_ads,
            categories=categories
        )
        
        # Display results
        if collected_ads:
            print(f"\nSuccessfully collected {len(collected_ads)} ads!")
            print("Data has been saved to the marketplace_data directory.")
            
            # Analyze the collected data
            if (hasattr(args, 'auto_analyze') and args.auto_analyze) or (input("\nWould you like to analyze the collected data now? (y/n): ").lower() == 'y'):
                print("\nAnalyzing collected marketplace data...")
                trends = scraper.extract_trends_from_marketplace_data('marketplace_data/processed')
                
                if trends:
                    print(f"Analysis complete! Extracted trends from {trends.get('total_ads_analyzed', 0)} ads.")
                    print("The analysis results have been saved to marketplace_data/processed/")
                    
                    # Display highlights
                    print("\nHighlights from the analysis:")
                    for industry, data in trends.get('industries', {}).items():
                        print(f"- {industry}: {data.get('ad_count', 0)} ads, " + 
                              f"avg title length: {data.get('avg_title_length', 0):.1f} words")
                else:
                    print("No trends could be extracted from the collected data.")
        else:
            print("No ads were collected. Please check the logs for details.")
        
    except Exception as e:
        logger.error(f"Error in marketplace scraper: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred during scraping: {str(e)}")
        print("Please check the logs for details.")


def run_full_pipeline(args):
    """Run the complete pipeline from scraping to ad generation."""
    logger = setup_logging()
    logger.info("Starting the complete ad generation pipeline")
    
    # Create required directories
    create_required_directories()
    
    print("===== COMPLETE AD GENERATION PIPELINE =====")
    print("This process will:")
    print("1. Collect high-performing ads from selected platforms")
    print("2. Process and analyze the collected data")
    print("3. Extract insights and prepare training examples")
    print("4. Train the ad generation model")
    print("5. Generate professional ads based on your prompts")
    
    try:
        # Step 1: Run ad insights scraper
        print("\n----- STEP 1: COLLECTING AD DATA -----")
        run_ad_insights_scraper(args)
        
        # Step 2: Train model if requested
        if hasattr(args, 'skip_training') and args.skip_training:
            print("\n----- STEP 2: TRAINING (SKIPPED) -----")
        else:
            print("\n----- STEP 2: TRAINING MODEL -----")
            # Training is handled in run_ad_insights_scraper if auto_train is True
            # So we don't need to call anything else here
        
        # Step 3: Generate ads for requested prompts
        print("\n----- STEP 3: GENERATING ADS -----")
        
        # Get generation prompts
        prompts = args.prompts if hasattr(args, 'prompts') else None
        if not prompts:
            print("\nWhat would you like to create ads for?")
            print("You can enter multiple prompts separated by semicolons (;)")
            prompts_input = input("\nPrompts: ")
            prompts = [p.strip() for p in prompts_input.split(';') if p.strip()]
        
        if not prompts:
            print("No prompts provided. Skipping ad generation.")
            return
        
        # Import generator
        from ad_generator import AdGenerator
        generator = AdGenerator()
        
        # Generate ads for each prompt
        for i, prompt in enumerate(prompts):
            print(f"\nGenerating ad {i+1}/{len(prompts)}: {prompt}")
            
            # Create a namespace with the current prompt
            prompt_args = argparse.Namespace()
            
            # Copy args attributes to prompt_args
            if hasattr(args, '__dict__'):
                for key, value in vars(args).items():
                    setattr(prompt_args, key, value)
            
            # Set the prompt
            prompt_args.prompt = prompt
            
            # Run the ad generation
            generate_ad_mode(prompt_args)
        
        print("\n===== PIPELINE COMPLETE =====")
        print("All steps completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred: {str(e)}")
        print("Please check the logs for details.")


def main():
    """Main entry point for the ad generation system."""
    # Display welcome banner
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     PROFESSIONAL AD GENERATION SYSTEM     ║
    ║     Studio Quality Content Engine         ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    
    # Set up argument parser
    print("Setting up argument parser...")
    parser = argparse.ArgumentParser(description="Professional Ad Generation System")
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    
    # Generate ad mode
    generate_parser = subparsers.add_parser("generate", help="Generate professional ads")
    generate_parser.add_argument("--prompt", "-p", type=str, 
                              help="Direct prompt input for ad generation")
    generate_parser.add_argument("--product-image", "-i", type=str,
                          help="Path to the product image to use in the ad")
    generate_parser.add_argument("--export-format", "-e", type=str, default="all", 
                              choices=["excel", "json", "all"], 
                              help="Export format for generated ad")
    
    # Ad insights scraper mode
    scraper_parser = subparsers.add_parser("scrape", help="Scrape ads for insights")
    scraper_parser.add_argument("--keywords", type=str, nargs='+',
                             help="Keywords to search for when scraping ads")
    scraper_parser.add_argument("--facebook", action="store_true",
                             help="Scrape from Facebook Ads")
    scraper_parser.add_argument("--reddit", action="store_true",
                             help="Scrape from Reddit")
    scraper_parser.add_argument("--adspy", action="store_true",
                             help="Scrape from AdSpy")
    scraper_parser.add_argument("--all-platforms", action="store_true",
                             help="Scrape from all available platforms")
    scraper_parser.add_argument("--countries", type=str, nargs='+', default=['US'],
                             help="Countries to target for scraping (ISO codes)")
    scraper_parser.add_argument("--limit", type=int, default=100,
                             help="Maximum number of ads to collect per keyword")
    scraper_parser.add_argument("--subreddits", type=str, nargs='+',
                             help="Specific subreddits to search (for Reddit)")
    scraper_parser.add_argument("--adspy-username", type=str,
                             help="AdSpy username for authentication")
    scraper_parser.add_argument("--adspy-password", type=str,
                             help="AdSpy password for authentication")
    scraper_parser.add_argument("--adspy-platforms", type=str, nargs='+',
                             default=['facebook', 'instagram'],
                             help="Platforms to search in AdSpy")
    scraper_parser.add_argument("--auto-train", action="store_true",
                             help="Automatically train model after scraping")
    scraper_parser.add_argument("--model-type", type=str, default="gpt",
                             choices=["gpt", "llama", "custom"],
                             help="Type of model to train")
    
    # Marketplace scraper mode
    marketplace_parser = subparsers.add_parser("marketplace", help="Scrape Facebook Marketplace")
    marketplace_parser.add_argument("--facebook-username", type=str,
                                 help="Facebook username for authentication")
    marketplace_parser.add_argument("--facebook-password", type=str,
                                 help="Facebook password for authentication")
    marketplace_parser.add_argument("--categories", type=str, nargs='+',
                                 help="Categories to scrape from Marketplace")
    marketplace_parser.add_argument("--limit", type=int, default=100,
                                 help="Maximum number of ads to collect")
    marketplace_parser.add_argument("--show-browser", action="store_true",
                                 help="Show browser window during scraping")
    marketplace_parser.add_argument("--auto-analyze", action="store_true",
                                 help="Automatically analyze data after scraping")
    
    # Complete pipeline mode
    pipeline_parser = subparsers.add_parser("pipeline", help="Run complete pipeline")
    pipeline_parser.add_argument("--keywords", type=str, nargs='+',
                              help="Keywords to search for when scraping ads")
    pipeline_parser.add_argument("--prompts", type=str, nargs='+',
                              help="Prompts to generate ads for")
    pipeline_parser.add_argument("--all-platforms", action="store_true",
                              help="Scrape from all available platforms")
    pipeline_parser.add_argument("--facebook", action="store_true",
                              help="Scrape from Facebook Ads")
    pipeline_parser.add_argument("--reddit", action="store_true",
                              help="Scrape from Reddit")
    pipeline_parser.add_argument("--adspy", action="store_true",
                              help="Scrape from AdSpy")
    pipeline_parser.add_argument("--limit", type=int, default=100,
                              help="Maximum ads to collect per keyword")
    pipeline_parser.add_argument("--skip-training", action="store_true",
                              help="Skip the training step")
    pipeline_parser.add_argument("--auto-train", action="store_true",
                              help="Automatically train model after scraping")
    pipeline_parser.add_argument("--export-format", type=str, default="all",
                              choices=["excel", "json", "all"],
                              help="Export format for generated ads")
    
    # Parse arguments with error handling
    print("Parsing arguments...")
    try:
        args = parser.parse_args()
        print(f"Args parsed: {vars(args) if hasattr(args, '__dict__') else 'No args parsed'}")
    except Exception as e:
        print(f"Error parsing arguments: {e}")
        # Create default namespace
        args = argparse.Namespace()
        args.mode = None
        args.prompt = None
        args.export_format = "all"
    
    # Check dependencies before proceeding
    print("Checking dependencies...")
    if not check_dependencies():
        print("Dependency check failed.")
        sys.exit(1)
    
    # Create required directories
    print("Creating required directories...")
    create_required_directories()
    
    # Select mode based on args
    print(f"Selected mode: {getattr(args, 'mode', 'None')}")
    try:
        if hasattr(args, 'mode') and args.mode == "generate":
            generate_ad_mode(args)
        elif hasattr(args, 'mode') and args.mode == "scrape":
            run_ad_insights_scraper(args)
        elif hasattr(args, 'mode') and args.mode == "marketplace":
            run_marketplace_scraper(args)
        elif hasattr(args, 'mode') and args.mode == "pipeline":
            run_full_pipeline(args)
        else:
            # Default to ad generation if no mode specified
            print("No mode specified, defaulting to ad generation...")
            # Ensure required attributes exist
            if not hasattr(args, 'prompt'):
                args.prompt = None
            if not hasattr(args, 'export_format'):
                args.export_format = "all"
            generate_ad_mode(args)
    except Exception as e:
        print(f"Error running selected mode: {str(e)}")
        traceback.print_exc()
        print("\nPlease check the logs for more details.")


if __name__ == "__main__":
    try:
        print("Calling main function...")
        main()
        print("Main function completed.")
    except Exception as e:
        print(f"Unhandled exception in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)