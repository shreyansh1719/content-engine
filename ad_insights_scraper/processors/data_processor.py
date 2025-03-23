"""
Data processing for ad insights system
"""
import os
import re
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from collections import defaultdict

class DataProcessor:
    """
    Process and normalize data from different scraping sources.
    
    Features:
    - Cleans and standardizes ad data from multiple sources
    - Merges related data for comprehensive analysis
    - Handles different data structures and formats
    - Prepares data for insight extraction and LLM training
    """
    
    def __init__(
        self,
        input_dir: str = 'data/raw',
        output_dir: str = 'data/processed',
        log_level: int = logging.INFO
    ):
        """
        Initialize data processor.
        
        Args:
            input_dir: Directory containing raw data files
            output_dir: Directory to save processed data
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger('DataProcessor')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Create handlers
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                os.path.join(output_dir, 'data_processor.log'),
                encoding='utf-8'
            )
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Set formatters
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        
        # Directories
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Source-specific processors
        self.source_processors = {
            'facebook': self._process_facebook_data,
            'reddit': self._process_reddit_data,
            'adspy': self._process_adspy_data
        }
        
        # File patterns for different sources
        self.file_patterns = {
            'facebook': r'fb_ads_.*\.json',
            'reddit': r'reddit_(posts|post_comments).*\.json',
            'adspy': r'adspy_.*\.json'
        }
    
    def process_all(self) -> Dict[str, int]:
        """
        Process all available data files from all sources.
        
        Returns:
            Dictionary with count of processed files per source
        """
        processed_counts = {
            'facebook': 0,
            'reddit': 0,
            'adspy': 0,
            'other': 0
        }
        
        try:
            # Process each source
            for source, pattern in self.file_patterns.items():
                processed = self._process_source_files(source, pattern)
                processed_counts[source] = processed
            
            # Process any remaining files
            files = [f for f in os.listdir(self.input_dir) 
                    if os.path.isfile(os.path.join(self.input_dir, f)) 
                    and f.endswith('.json')]
            
            # Check for files that weren't matched by patterns
            for file in files:
                matched = False
                for pattern in self.file_patterns.values():
                    if re.match(pattern, file):
                        matched = True
                        break
                
                if not matched:
                    self.logger.info(f"Processing unmatched file: {file}")
                    self._process_generic_file(os.path.join(self.input_dir, file))
                    processed_counts['other'] += 1
            
            # Merge all processed data
            self.merge_all_processed()
            
            return processed_counts
            
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return processed_counts
    
    def _process_source_files(self, source: str, pattern: str) -> int:
        """
        Process files from a specific source.
        
        Args:
            source: Source name ('facebook', 'reddit', 'adspy')
            pattern: Regex pattern to match filenames
            
        Returns:
            Count of processed files
        """
        processed_count = 0
        
        # Get all matching files
        files = [f for f in os.listdir(self.input_dir) 
                if os.path.isfile(os.path.join(self.input_dir, f)) 
                and re.match(pattern, f)]
        
        # Process each file
        for file in files:
            try:
                self.logger.info(f"Processing {source} file: {file}")
                filepath = os.path.join(self.input_dir, file)
                
                # Call source-specific processor
                if source in self.source_processors:
                    self.source_processors[source](filepath)
                else:
                    self._process_generic_file(filepath)
                
                processed_count += 1
                
            except Exception as e:
                self.logger.error(f"Error processing file {file}: {str(e)}")
        
        self.logger.info(f"Processed {processed_count} {source} files")
        return processed_count
    
    def _process_facebook_data(self, filepath: str) -> None:
        """
        Process Facebook ads data.
        
        Args:
            filepath: Path to raw Facebook ads JSON file
        """
        try:
            # Load JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ads = data.get('ads', [])
            if not ads:
                self.logger.warning(f"No ads found in {filepath}")
                return
            
            # Normalize data
            normalized_ads = []
            
            for ad in ads:
                normalized_ad = {
                    "source": "facebook",
                    "id": ad.get('ad_id', ''),
                    "platform": "facebook",
                    "advertiser_name": ad.get('page_name', ''),
                    "advertiser_id": ad.get('page_id', ''),
                    "text": ad.get('ad_text', ''),
                    "headline": ad.get('ad_creative', {}).get('title', ''),
                    "cta": ad.get('cta_text', ''),
                    "landing_page": ad.get('link_url', ''),
                    "media_urls": ad.get('image_urls', []) + ad.get('video_urls', []),
                    "media_type": ad.get('ad_format', 'image'),
                    "first_seen": ad.get('start_date', ''),
                    "last_seen": ad.get('end_date', ''),
                    "status": ad.get('status', ''),
                    "engagement": {},
                    "targeting": {},
                    "metadata": {
                        "search_keyword": ad.get('search_keyword', ''),
                        "search_country": ad.get('search_country', ''),
                        "scrape_time": ad.get('scrape_time', '')
                    }
                }
                
                normalized_ads.append(normalized_ad)
            
            # Save normalized data
            output_filename = os.path.basename(filepath).replace('.json', '_normalized.json')
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "source": "facebook",
                        "processing_time": datetime.now().isoformat(),
                        "count": len(normalized_ads)
                    },
                    "ads": normalized_ads
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(normalized_ads)} normalized Facebook ads to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing Facebook data {filepath}: {str(e)}")
            raise
    
    def _process_reddit_data(self, filepath: str) -> None:
        """
        Process Reddit data.
        
        Args:
            filepath: Path to raw Reddit JSON file
        """
        try:
            # Load JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's posts or comments
            if 'posts' in data:
                self._process_reddit_posts(data, filepath)
            elif 'post' in data:
                self._process_reddit_post_comments(data, filepath)
            else:
                self.logger.warning(f"Unknown Reddit data format in {filepath}")
        
        except Exception as e:
            self.logger.error(f"Error processing Reddit data {filepath}: {str(e)}")
            raise
    
    def _process_reddit_posts(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Process Reddit posts data.
        
        Args:
            data: Reddit posts data dictionary
            filepath: Original file path
        """
        posts = data.get('posts', [])
        if not posts:
            self.logger.warning(f"No posts found in {filepath}")
            return
        
        # Normalize data
        normalized_posts = []
        
        for post in posts:
            normalized_post = {
                "source": "reddit",
                "id": post.get('id', ''),
                "platform": "reddit",
                "advertiser_name": post.get('author', ''),
                "subreddit": post.get('subreddit', ''),
                "title": post.get('title', ''),
                "text": post.get('selftext', ''),
                "url": post.get('permalink', ''),
                "external_url": post.get('url', ''),
                "created_date": post.get('created_date', ''),
                "engagement": {
                    "score": post.get('score', 0),
                    "upvote_ratio": post.get('upvote_ratio', 0),
                    "comments": post.get('num_comments', 0)
                },
                "sentiment": post.get('sentiment', {}),
                "keywords": post.get('keywords', []),
                "metadata": {
                    "query": post.get('query', ''),
                    "is_self": post.get('is_self', True),
                    "flair": post.get('link_flair_text', '')
                }
            }
            
            normalized_posts.append(normalized_post)
        
        # Save normalized data
        output_filename = os.path.basename(filepath).replace('.json', '_normalized.json')
        output_path = os.path.join(self.output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "source": "reddit",
                    "type": "posts",
                    "processing_time": datetime.now().isoformat(),
                    "count": len(normalized_posts)
                },
                "posts": normalized_posts
            }, f, indent=2)
        
        self.logger.info(f"Saved {len(normalized_posts)} normalized Reddit posts to {output_path}")
    
    def _process_reddit_post_comments(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Process Reddit post with comments data.
        
        Args:
            data: Reddit post with comments data dictionary
            filepath: Original file path
        """
        post = data.get('post', {})
        comments = post.get('comments', [])
        
        if not post or not comments:
            self.logger.warning(f"No valid post or comments found in {filepath}")
            return
        
        # Normalize post data (same as in _process_reddit_posts)
        normalized_post = {
            "source": "reddit",
            "id": post.get('id', ''),
            "platform": "reddit",
            "advertiser_name": post.get('author', ''),
            "subreddit": post.get('subreddit', ''),
            "title": post.get('title', ''),
            "text": post.get('selftext', ''),
            "url": post.get('permalink', ''),
            "external_url": post.get('url', ''),
            "created_date": post.get('created_date', ''),
            "engagement": {
                "score": post.get('score', 0),
                "upvote_ratio": post.get('upvote_ratio', 0),
                "comments": post.get('num_comments', 0)
            }
        }
        
        # Normalize comments
        normalized_comments = []
        
        for comment in comments:
            normalized_comment = {
                "source": "reddit",
                "id": comment.get('id', ''),
                "parent_id": comment.get('parent_id', ''),
                "post_id": comment.get('parent_submission_id', ''),
                "author": comment.get('author', ''),
                "text": comment.get('body', ''),
                "created_date": comment.get('created_date', ''),
                "score": comment.get('score', 0),
                "is_submitter": comment.get('is_submitter', False),
                "sentiment": comment.get('sentiment', {}),
                "keywords": comment.get('keywords', []),
                "metadata": {
                    "query": comment.get('query', '')
                }
            }
            
            normalized_comments.append(normalized_comment)
        
        # Save normalized data
        output_filename = os.path.basename(filepath).replace('.json', '_normalized.json')
        output_path = os.path.join(self.output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "source": "reddit",
                    "type": "post_with_comments",
                    "processing_time": datetime.now().isoformat(),
                    "count": len(normalized_comments)
                },
                "post": normalized_post,
                "comments": normalized_comments
            }, f, indent=2)
        
        self.logger.info(f"Saved normalized Reddit post with {len(normalized_comments)} comments to {output_path}")
    
    def _process_adspy_data(self, filepath: str) -> None:
        """
        Process AdSpy data.
        
        Args:
            filepath: Path to raw AdSpy JSON file
        """
        try:
            # Load JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ads = data.get('ads', [])
            if not ads:
                self.logger.warning(f"No ads found in {filepath}")
                return
            
            # Normalize data
            normalized_ads = []
            
            for ad in ads:
                normalized_ad = {
                    "source": "adspy",
                    "id": ad.get('ad_id', ''),
                    "platform": ad.get('platform', ''),
                    "advertiser_name": ad.get('advertiser_name', ''),
                    "advertiser_url": ad.get('advertiser_url', ''),
                    "text": ad.get('ad_text', ''),
                    "headline": ad.get('headline', ''),
                    "cta": ad.get('cta', ''),
                    "landing_page": ad.get('landing_page', ''),
                    "media_urls": ad.get('image_urls', []) + ad.get('video_urls', []),
                    "media_type": "video" if ad.get('video_urls') else "image",
                    "first_seen": ad.get('first_seen', ''),
                    "last_seen": ad.get('last_seen', ''),
                    "engagement": ad.get('engagement', {}),
                    "targeting": ad.get('targeting', {}),
                    "metadata": {
                        "search_keyword": ad.get('search_keyword', ''),
                        "search_platforms": ad.get('search_platforms', []),
                        "scrape_time": ad.get('scrape_time', '')
                    }
                }
                
                normalized_ads.append(normalized_ad)
            
            # Save normalized data
            output_filename = os.path.basename(filepath).replace('.json', '_normalized.json')
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "source": "adspy",
                        "processing_time": datetime.now().isoformat(),
                        "count": len(normalized_ads)
                    },
                    "ads": normalized_ads
                }, f, indent=2)
            
            self.logger.info(f"Saved {len(normalized_ads)} normalized AdSpy ads to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing AdSpy data {filepath}: {str(e)}")
            raise
    
    def _process_generic_file(self, filepath: str) -> None:
        """
        Process generic JSON file.
        
        Args:
            filepath: Path to JSON file
        """
        try:
            # Load JSON data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Try to detect the data type
            if 'ads' in data:
                ads = data.get('ads', [])
                if ads and isinstance(ads, list):
                    # Determine the source based on content
                    first_ad = ads[0]
                    if 'page_name' in first_ad:
                        self._process_facebook_data(filepath)
                    elif 'advertiser_name' in first_ad:
                        self._process_adspy_data(filepath)
                    else:
                        self.logger.warning(f"Unknown ad format in {filepath}")
            elif 'posts' in data:
                self._process_reddit_data(filepath)
            elif 'post' in data and 'comments' in data.get('post', {}):
                self._process_reddit_data(filepath)
            else:
                self.logger.warning(f"Unknown data format in {filepath}")
                
        except Exception as e:
            self.logger.error(f"Error processing generic file {filepath}: {str(e)}")
    
    def clean_data(self) -> None:
        """
        Clean and normalize data in the output directory.
        """
        try:
            # Get all JSON files in the output directory
            files = [f for f in os.listdir(self.output_dir) 
                    if os.path.isfile(os.path.join(self.output_dir, f)) 
                    and f.endswith('.json')]
            
            for file in files:
                try:
                    self.logger.info(f"Cleaning file: {file}")
                    filepath = os.path.join(self.output_dir, file)
                    
                    # Load the data
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Clean the data based on its type
                    if 'ads' in data:
                        self._clean_ads_data(data, filepath)
                    elif 'posts' in data:
                        self._clean_posts_data(data, filepath)
                    elif 'post' in data and 'comments' in data:
                        self._clean_post_comments_data(data, filepath)
                    else:
                        self.logger.warning(f"Unknown data format in {file}")
                
                except Exception as e:
                    self.logger.error(f"Error cleaning file {file}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error during data cleaning: {str(e)}")
    
    def _clean_ads_data(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Clean and standardize ads data.
        
        Args:
            data: Ads data dictionary
            filepath: File path for saving cleaned data
        """
        ads = data.get('ads', [])
        if not ads:
            return
        
        # Clean each ad
        for ad in ads:
            # Standardize dates
            for date_field in ['first_seen', 'last_seen', 'created_date', 'scrape_time']:
                if date_field in ad and ad[date_field]:
                    try:
                        # Parse and standardize date format
                        date_obj = pd.to_datetime(ad[date_field])
                        ad[date_field] = date_obj.isoformat()
                    except:
                        pass
            
            # Clean and validate URLs
            for url_field in ['landing_page', 'url', 'external_url', 'advertiser_url']:
                if url_field in ad and ad[url_field]:
                    url = ad[url_field]
                    # Ensure URL has a scheme
                    if url and not (url.startswith('http://') or url.startswith('https://')):
                        ad[url_field] = 'https://' + url
            
            # Ensure text fields are strings
            for text_field in ['text', 'headline', 'cta', 'advertiser_name']:
                if text_field in ad and ad[text_field] is not None:
                    ad[text_field] = str(ad[text_field])
        
        # Save cleaned data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _clean_posts_data(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Clean and standardize Reddit posts data.
        
        Args:
            data: Posts data dictionary
            filepath: File path for saving cleaned data
        """
        posts = data.get('posts', [])
        if not posts:
            return
        
        # Clean each post
        for post in posts:
            # Standardize dates
            if 'created_date' in post and post['created_date']:
                try:
                    date_obj = pd.to_datetime(post['created_date'])
                    post['created_date'] = date_obj.isoformat()
                except:
                    pass
            
            # Ensure engagement metrics are numeric
            engagement = post.get('engagement', {})
            for metric in engagement:
                try:
                    engagement[metric] = float(engagement[metric])
                except (ValueError, TypeError):
                    engagement[metric] = 0
            
            # Ensure text fields are strings
            for text_field in ['title', 'text', 'subreddit', 'advertiser_name']:
                if text_field in post and post[text_field] is not None:
                    post[text_field] = str(post[text_field])
        
        # Save cleaned data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _clean_post_comments_data(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Clean and standardize Reddit post with comments data.
        
        Args:
            data: Post with comments data dictionary
            filepath: File path for saving cleaned data
        """
        post = data.get('post', {})
        comments = data.get('comments', [])
        
        # Clean post data (similar to _clean_posts_data)
        if post:
            # Standardize dates
            if 'created_date' in post and post['created_date']:
                try:
                    date_obj = pd.to_datetime(post['created_date'])
                    post['created_date'] = date_obj.isoformat()
                except:
                    pass
            
            # Ensure engagement metrics are numeric
            engagement = post.get('engagement', {})
            for metric in engagement:
                try:
                    engagement[metric] = float(engagement[metric])
                except (ValueError, TypeError):
                    engagement[metric] = 0
        
        # Clean comments
        for comment in comments:
            # Standardize dates
            if 'created_date' in comment and comment['created_date']:
                try:
                    date_obj = pd.to_datetime(comment['created_date'])
                    comment['created_date'] = date_obj.isoformat()
                except:
                    pass
            
            # Ensure score is numeric
            if 'score' in comment:
                try:
                    comment['score'] = float(comment['score'])
                except (ValueError, TypeError):
                    comment['score'] = 0
            
            # Ensure text fields are strings
            for text_field in ['text', 'author']:
                if text_field in comment and comment[text_field] is not None:
                    comment[text_field] = str(comment[text_field])
        
        # Save cleaned data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def merge_sources(self) -> None:
        """
        Merge data from different sources for combined analysis.
        """
        try:
            # Get all normalized JSON files
            files = [f for f in os.listdir(self.output_dir) 
                    if os.path.isfile(os.path.join(self.output_dir, f)) 
                    and f.endswith('_normalized.json')]
            
            # Collect data by type
            ads_data = []
            reddit_posts = []
            reddit_comments = []
            
            # Process each file
            for file in files:
                filepath = os.path.join(self.output_dir, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Determine the data type and collect
                if 'ads' in data:
                    ads_data.extend(data['ads'])
                elif 'posts' in data:
                    reddit_posts.extend(data['posts'])
                elif 'post' in data and 'comments' in data:
                    # Add the post
                    reddit_posts.append(data['post'])
                    # Add the comments
                    reddit_comments.extend(data['comments'])
            
            # Save merged data
            self._save_merged_data(ads_data, reddit_posts, reddit_comments)
            
        except Exception as e:
            self.logger.error(f"Error merging sources: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _save_merged_data(
        self, 
        ads: List[Dict[str, Any]], 
        posts: List[Dict[str, Any]], 
        comments: List[Dict[str, Any]]
    ) -> None:
        """
        Save merged data to separate files by type.
        
        Args:
            ads: List of normalized ad dictionaries
            posts: List of normalized Reddit post dictionaries
            comments: List of normalized Reddit comment dictionaries
        """
        # Save merged ads
        if ads:
            ad_filepath = os.path.join(self.output_dir, f"merged_ads_{datetime.now().strftime('%Y%m%d')}.json")
            with open(ad_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "type": "merged_ads",
                        "processing_time": datetime.now().isoformat(),
                        "count": len(ads)
                    },
                    "ads": ads
                }, f, indent=2)
            self.logger.info(f"Saved {len(ads)} merged ads to {ad_filepath}")
        
        # Save merged Reddit posts
        if posts:
            post_filepath = os.path.join(self.output_dir, f"merged_reddit_posts_{datetime.now().strftime('%Y%m%d')}.json")
            with open(post_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "type": "merged_reddit_posts",
                        "processing_time": datetime.now().isoformat(),
                        "count": len(posts)
                    },
                    "posts": posts
                }, f, indent=2)
            self.logger.info(f"Saved {len(posts)} merged Reddit posts to {post_filepath}")
        
        # Save merged Reddit comments
        if comments:
            comment_filepath = os.path.join(self.output_dir, f"merged_reddit_comments_{datetime.now().strftime('%Y%m%d')}.json")
            with open(comment_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "type": "merged_reddit_comments",
                        "processing_time": datetime.now().isoformat(),
                        "count": len(comments)
                    },
                    "comments": comments
                }, f, indent=2)
            self.logger.info(f"Saved {len(comments)} merged Reddit comments to {comment_filepath}")
    
    def merge_all_processed(self) -> None:
        """
        Merge all processed data by keywords and brands.
        """
        try:
            # Get all normalized JSON files
            files = [f for f in os.listdir(self.output_dir) 
                    if os.path.isfile(os.path.join(self.output_dir, f)) 
                    and f.endswith('_normalized.json')]
            
            # Collect data by keywords and brands
            keyword_data = defaultdict(list)
            brand_data = defaultdict(list)
            
            # Process each file
            for file in files:
                filepath = os.path.join(self.output_dir, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process ads
                if 'ads' in data:
                    for ad in data['ads']:
                        # Extract keyword
                        keyword = ad.get('metadata', {}).get('search_keyword', '')
                        if keyword:
                            keyword_data[keyword].append(ad)
                        
                        # Extract brand/advertiser
                        brand = ad.get('advertiser_name', '')
                        if brand:
                            brand_data[brand].append(ad)
                
                # Process Reddit posts
                elif 'posts' in data:
                    for post in data['posts']:
                        # Extract keyword
                        keyword = post.get('metadata', {}).get('query', '')
                        if keyword:
                            keyword_data[keyword].append(post)
            
            # Save merged data by keyword
            for keyword, items in keyword_data.items():
                if not items:
                    continue
                
                # Clean the keyword for filename
                clean_keyword = re.sub(r'[^\w\s]', '', keyword).strip().replace(' ', '_').lower()
                
                # Create output filepath
                keyword_filepath = os.path.join(
                    self.output_dir, 
                    f"keyword_{clean_keyword}_{datetime.now().strftime('%Y%m%d')}.json"
                )
                
                # Save the data
                with open(keyword_filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": {
                            "type": "keyword_data",
                            "keyword": keyword,
                            "processing_time": datetime.now().isoformat(),
                            "count": len(items)
                        },
                        "items": items
                    }, f, indent=2)
                
                self.logger.info(f"Saved {len(items)} items for keyword '{keyword}' to {keyword_filepath}")
            
            # Save merged data by brand
            for brand, items in brand_data.items():
                if not items or len(items) < 3:  # Skip brands with very few items
                    continue
                
                # Clean the brand for filename
                clean_brand = re.sub(r'[^\w\s]', '', brand).strip().replace(' ', '_').lower()
                
                # Create output filepath
                brand_filepath = os.path.join(
                    self.output_dir, 
                    f"brand_{clean_brand}_{datetime.now().strftime('%Y%m%d')}.json"
                )
                
                # Save the data
                with open(brand_filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": {
                            "type": "brand_data",
                            "brand": brand,
                            "processing_time": datetime.now().isoformat(),
                            "count": len(items)
                        },
                        "items": items
                    }, f, indent=2)
                
                self.logger.info(f"Saved {len(items)} items for brand '{brand}' to {brand_filepath}")
            
        except Exception as e:
            self.logger.error(f"Error merging all processed data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Example usage
    processor = DataProcessor(
        input_dir='data/raw',
        output_dir='data/processed'
    )
    
    # Process all data
    processor.process_all()
    
    # Clean the data
    processor.clean_data()
    
    # Merge data from different sources
    processor.merge_sources()