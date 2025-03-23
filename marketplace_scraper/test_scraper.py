# test_scraper.py - Run this to test your scraper
from marketplace_scraper.scraper import MarketplaceScraper

def run_test():
    print("Testing Facebook Marketplace Scraper")
    
    username = input("Facebook Username: ")
    password = input("Facebook Password: ")
    
    if not username or not password:
        print("Username and password required")
        return
    
    scraper = MarketplaceScraper(username=username, password=password)
    
    try:
        print("Initializing scraper and logging in...")
        ads = scraper.run_comprehensive_scraping_session(max_ads=20)
        
        print(f"Collected {len(ads)} ads!")
        if ads:
            print("\nSample of collected ads:")
            for ad in ads[:3]:
                print(f"- {ad.get('title', 'No title')} | {ad.get('price', 'No price')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_test()