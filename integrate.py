"""
Integration script for complete ad generation pipeline
"""
import os
import logging
import argparse
from datetime import datetime
import traceback

def setup_logging():
    """Set up logging configuration"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"integration_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_full_pipeline(args):
    """Run the full pipeline from scraping to ad generation"""
    logger = setup_logging()
    logger.info("Starting full ad generation pipeline")
    
    try:
        # Step 1: Import necessary components
        from ad_insights_scraper.scraper_controller import ScraperController
        from ad_insights_scraper.training_pipeline import TrainingPipeline
        from ad_generator import AdGenerator
        from utils.excel_utils import save_ad_to_excel
        
        # Create necessary directories
        dirs = ['data/raw', 'data/processed', 'data/insights', 'data/training', 
                'data/models', 'output/images', 'output/excel']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        
        # Step 2: Run data collection
        print("===== STEP 1: COLLECTING AD DATA =====")
        controller = ScraperController()
        
        keywords = args.keywords
        if not keywords:
            keywords_input = input("Enter keywords to search (comma-separated): ")
            keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        
        if not keywords:
            print("No keywords provided. Exiting.")
            return
        
        print(f"Collecting ads for: {', '.join(keywords)}")
        
        # Facebook scraping
        if args.facebook or args.all_platforms:
            facebook_ads = controller.run_facebook_scraper(
                keywords=keywords, 
                countries=args.countries or ['US'],
                max_ads=args.limit or 100
            )
            print(f"Collected {len(facebook_ads)} Facebook ads")
        
        # Reddit scraping
        if args.reddit or args.all_platforms:
            reddit_posts, reddit_comments = controller.run_reddit_scraper(
                keywords=keywords,
                limit=args.limit or 100
            )
            print(f"Collected {len(reddit_posts)} Reddit posts and {len(reddit_comments)} comments")
        
        # AdSpy scraping
        if args.adspy or args.all_platforms:
            # Ask for credentials if not provided
            adspy_username = args.adspy_username
            adspy_password = args.adspy_password
            
            if not adspy_username or not adspy_password:
                print("\nAdSpy credentials required for scraping:")
                adspy_username = input("AdSpy Username: ")
                adspy_password = input("AdSpy Password: ")
            
            if adspy_username and adspy_password:
                controller.set_adspy_credentials(adspy_username, adspy_password)
                adspy_ads, _ = controller.run_adspy_scraper(
                    keywords=keywords,
                    limit=args.limit or 100
                )
                print(f"Collected {len(adspy_ads)} ads from AdSpy")
        
        # Step 3: Process all data
        print("\n===== STEP 2: PROCESSING DATA =====")
        processing_results = controller.process_all_data()
        
        # Step 4: Extract insights
        print("\n===== STEP 3: EXTRACTING INSIGHTS =====")
        insights = controller.extract_insights()
        print(f"Extracted {len(insights)} insights")
        
        # Step 5: Prepare training data and train model
        if not args.skip_training:
            print("\n===== STEP 4: TRAINING MODEL =====")
            training_pipeline = TrainingPipeline(model_type=args.model_type or 'gpt')
            training_results = training_pipeline.run_full_pipeline()
            
            if not training_results:
                print("Training failed. Using default model instead.")
        else:
            print("\n===== STEP 4: TRAINING (SKIPPED) =====")
        
        # Step 6: Generate ads
        print("\n===== STEP 5: GENERATING ADS =====")
        generator = AdGenerator()
        
        # Get generation prompts
        prompts = args.prompts
        if not prompts:
            print("\nWhat would you like to create ads for?")
            print("You can enter multiple prompts separated by semicolons (;)")
            prompts_input = input("\nPrompts: ")
            prompts = [p.strip() for p in prompts_input.split(';') if p.strip()]
        
        if not prompts:
            print("No prompts provided. Skipping ad generation.")
            return
        
        # Generate ads for each prompt
        for i, prompt in enumerate(prompts):
            print(f"\nGenerating ad {i+1}/{len(prompts)}: {prompt}")
            
            # Generate the ad
            ad_data = generator.create_ad(prompt)
            
            # Save to Excel if requested
            excel_path = save_ad_to_excel(ad_data)
            ad_data['excel_path'] = excel_path
            
            # Display results
            print(f"\n--- Ad {i+1} Results ---")
            print(f"Headline: {ad_data['headline']}")
            print(f"Subheadline: {ad_data.get('subheadline', 'N/A')}")
            print(f"Call to Action: {ad_data.get('call_to_action', 'N/A')}")
            print(f"Image saved at: {ad_data['image_path']}")
            print(f"Excel report: {excel_path}")
        
        print("\n===== PIPELINE COMPLETE =====")
        print("All steps completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"An error occurred: {str(e)}")
        print("Please check the logs for details.")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ad Generation Pipeline")
    parser.add_argument("--keywords", nargs="+", help="Keywords to search for")
    parser.add_argument("--prompts", nargs="+", help="Prompts for ad generation")
    parser.add_argument("--facebook", action="store_true", help="Scrape Facebook ads")
    parser.add_argument("--reddit", action="store_true", help="Scrape Reddit content")
    parser.add_argument("--adspy", action="store_true", help="Scrape AdSpy data")
    parser.add_argument("--all-platforms", action="store_true", help="Scrape all platforms")
    parser.add_argument("--limit", type=int, help="Maximum items to collect per source")
    parser.add_argument("--countries", nargs="+", default=["US"], help="Countries to target")
    parser.add_argument("--adspy-username", help="AdSpy username")
    parser.add_argument("--adspy-password", help="AdSpy password")
    parser.add_argument("--skip-training", action="store_true", help="Skip model training")
    parser.add_argument("--model-type", choices=["gpt", "llama", "custom"], 
                       default="gpt", help="Model type to train")
    
    args = parser.parse_args()
    
    # If no platform specified, use all
    if not (args.facebook or args.reddit or args.adspy):
        args.all_platforms = True
    
    # Run the pipeline
    run_full_pipeline(args)

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     PROFESSIONAL AD GENERATION SYSTEM     ║
    ║     Complete Pipeline                     ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    main()