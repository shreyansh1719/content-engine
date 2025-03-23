"""
Advanced Reddit scraper for ad insights and trend analysis
"""
import os
import re
import time
import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Union
import praw
from praw.models import Submission, Comment
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

class RedditScraper:
    """
    Advanced Reddit scraper for advertising insights with robust error handling.
    
    Features:
    - Searches across multiple subreddits for ad-related content
    - Analyzes user sentiment about products and brands
    - Extracts trending keywords and topics
    - Identifies successful ad strategies through engagement metrics
    - Implements rate limiting to avoid API bans
    - Handles errors and retries gracefully
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        output_dir: str = 'data',
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize Reddit scraper with API credentials.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
            output_dir: Directory to save scraped data
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        # Setup logging
        self.logger = logging.getLogger('RedditScraper')
        
        # Save configuration
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Ensure output directories exist
        os.makedirs(os.path.join(output_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'processed'), exist_ok=True)
        
        # Initialize Reddit API client
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or f'AdInsightsScraper/1.0 (by u/{os.getenv("REDDIT_USERNAME", "YourUsername")})'
        
        if not self.client_id or not self.client_secret:
            self.logger.warning("Missing Reddit API credentials. Scraper will have limited functionality.")
            self.reddit = None
        else:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                self.logger.info("Reddit API client initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing Reddit client: {str(e)}")
                self.reddit = None
        
        # Initialize sentiment analyzer
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            self.logger.warning(f"Error initializing sentiment analyzer: {str(e)}")
            self.sentiment_analyzer = None
        
        # Rate limiting configuration
        self.request_tracker = {
            'count': 0,
            'last_reset': datetime.now(),
            'max_requests': 60,  # Maximum requests per minute (Reddit's limit is 60)
            'reset_interval': 60  # Reset count every 60 seconds
        }
        
        # Storage for scraped data
        self.scraped_posts = []
        self.scraped_comments = []
    
    def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limits to avoid API bans.
        Waits if necessary to stay within limits.
        """
        # Reset counter if interval has passed
        now = datetime.now()
        elapsed = (now - self.request_tracker['last_reset']).total_seconds()
        
        if elapsed > self.request_tracker['reset_interval']:
            self.request_tracker['count'] = 0
            self.request_tracker['last_reset'] = now
            return
        
        # Check if we're at the limit
        if self.request_tracker['count'] >= self.request_tracker['max_requests']:
            # Calculate sleep time required
            sleep_time = self.request_tracker['reset_interval'] - elapsed + 1  # +1 for safety buffer
            self.logger.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            
            # Reset after waiting
            self.request_tracker['count'] = 0
            self.request_tracker['last_reset'] = datetime.now()
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with automatic retries on failure.
        
        Args:
            func: Function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Function result or None if all retries fail
        """
        attempt = 0
        while attempt < self.max_retries:
            try:
                # Check rate limits before making request
                self._check_rate_limit()
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Increment request counter
                self.request_tracker['count'] += 1
                
                return result
                
            except Exception as e:
                attempt += 1
                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Attempt {attempt}/{self.max_retries} failed: {str(e)}. "
                        f"Retrying in {self.retry_delay} seconds..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed: {str(e)}")
                    return None
    
    def find_relevant_subreddits(self, keywords: List[str], limit: int = 10) -> List[str]:
        """
        Find subreddits relevant to specified keywords.
        
        Args:
            keywords: List of search keywords
            limit: Maximum number of subreddits to return
            
        Returns:
            List of relevant subreddit names
        """
        if not self.reddit:
            self.logger.warning("Reddit client not initialized, cannot search subreddits")
            return []
        
        relevant_subreddits = set()
        
        for keyword in keywords:
            try:
                # Search for subreddits using the keyword
                subreddit_search = self._execute_with_retry(
                    self.reddit.subreddits.search,
                    keyword,
                    limit=25  # Get more to filter down later
                )
                
                if subreddit_search:
                    # Extract names and add to set
                    for subreddit in subreddit_search:
                        relevant_subreddits.add(subreddit.display_name)
                
            except Exception as e:
                self.logger.warning(f"Error searching subreddits for '{keyword}': {str(e)}")
        
        # Filter and sort by relevance/subscribers
        if relevant_subreddits:
            return self._filter_subreddits(list(relevant_subreddits), keywords, limit)
        
        return []
    
    def _filter_subreddits(self, subreddit_names: List[str], keywords: List[str], limit: int) -> List[str]:
        """
        Filter and prioritize subreddits based on relevance and activity.
        
        Args:
            subreddit_names: List of subreddit names
            keywords: Original search keywords
            limit: Maximum number of subreddits to return
            
        Returns:
            Filtered list of subreddit names
        """
        if not self.reddit:
            return subreddit_names[:limit]
        
        # Create scoring dict
        scored_subreddits = {}
        
        for name in subreddit_names:
            try:
                subreddit = self._execute_with_retry(self.reddit.subreddit, name)
                
                if not subreddit:
                    continue
                
                # Get subscriber count
                subscribers = getattr(subreddit, 'subscribers', 0) or 0
                
                # Check if NSFW (we'll deprioritize these)
                is_nsfw = getattr(subreddit, 'over18', False) or False
                
                # Calculate base score from subscribers
                score = min(subscribers / 1000, 100)  # Cap at 100 to prevent domination
                
                # Reduce score for NSFW subreddits
                if is_nsfw:
                    score *= 0.5
                
                # Boost score for exact keyword matches in name
                for keyword in keywords:
                    if keyword.lower() in name.lower():
                        score *= 1.5
                
                # Boost score for active subreddits
                try:
                    new_posts = self._execute_with_retry(subreddit.new, limit=5)
                    if new_posts:
                        post_count = len(list(new_posts))
                        if post_count > 0:
                            # Check last post time
                            latest_post = next(subreddit.new(limit=1), None)
                            if latest_post:
                                post_age = datetime.now() - datetime.fromtimestamp(latest_post.created_utc)
                                if post_age < timedelta(days=1):
                                    score *= 1.2  # Boost for daily activity
                                elif post_age < timedelta(days=7):
                                    score *= 1.1  # Smaller boost for weekly activity
                except:
                    pass
                
                scored_subreddits[name] = score
                
            except Exception as e:
                self.logger.debug(f"Error scoring subreddit '{name}': {str(e)}")
        
        # Sort by score and return top 'limit' results
        sorted_subreddits = sorted(scored_subreddits.items(), key=lambda x: x[1], reverse=True)
        return [name for name, score in sorted_subreddits[:limit]]
    
    def search_posts(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        time_filter: str = 'month',
        sort_type: str = 'relevance',
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for posts across subreddits with comprehensive data extraction.
        
        Args:
            query: Search query
            subreddits: List of subreddits to search
            time_filter: Time range ('hour', 'day', 'week', 'month', 'year', 'all')
            sort_type: How to sort results ('relevance', 'hot', 'top', 'new', 'comments')
            limit: Maximum number of posts to return
            
        Returns:
            List of post dictionaries with comprehensive data
        """
        if not self.reddit:
            self.logger.warning("Reddit client not initialized, cannot search posts")
            return []
        
        collected_posts = []
        
        # If no specific subreddits provided, search across all of Reddit
        if not subreddits:
            try:
                self.logger.info(f"Searching all of Reddit for: '{query}'")
                search_results = self._execute_with_retry(
                    self.reddit.subreddit, 'all'
                )
                
                if search_results:
                    # Execute search with the appropriate sort type
                    if sort_type == 'hot':
                        submissions = self._execute_with_retry(search_results.search, query, limit=limit, sort='hot')
                    elif sort_type == 'top':
                        submissions = self._execute_with_retry(search_results.search, query, limit=limit, sort='top', time_filter=time_filter)
                    elif sort_type == 'new':
                        submissions = self._execute_with_retry(search_results.search, query, limit=limit, sort='new')
                    elif sort_type == 'comments':
                        submissions = self._execute_with_retry(search_results.search, query, limit=limit, sort='comments')
                    else:  # default to relevance
                        submissions = self._execute_with_retry(search_results.search, query, limit=limit)
                    
                    # Process submissions
                    if submissions:
                        for submission in submissions:
                            post_data = self._extract_post_data(submission, query)
                            if post_data:
                                collected_posts.append(post_data)
                
            except Exception as e:
                self.logger.error(f"Error searching all of Reddit: {str(e)}")
        
        else:
            # Search each subreddit individually
            for subreddit_name in subreddits:
                try:
                    self.logger.info(f"Searching r/{subreddit_name} for: '{query}'")
                    subreddit = self._execute_with_retry(
                        self.reddit.subreddit, subreddit_name
                    )
                    
                    if subreddit:
                        # Execute search with the appropriate sort type
                        if sort_type == 'hot':
                            submissions = self._execute_with_retry(subreddit.search, query, limit=limit, sort='hot')
                        elif sort_type == 'top':
                            submissions = self._execute_with_retry(subreddit.search, query, limit=limit, sort='top', time_filter=time_filter)
                        elif sort_type == 'new':
                            submissions = self._execute_with_retry(subreddit.search, query, limit=limit, sort='new')
                        elif sort_type == 'comments':
                            submissions = self._execute_with_retry(subreddit.search, query, limit=limit, sort='comments')
                        else:  # default to relevance
                            submissions = self._execute_with_retry(subreddit.search, query, limit=limit)
                        
                        # Process submissions
                        if submissions:
                            for submission in submissions:
                                post_data = self._extract_post_data(submission, query)
                                if post_data:
                                    collected_posts.append(post_data)
                
                except Exception as e:
                    self.logger.warning(f"Error searching r/{subreddit_name}: {str(e)}")
        
        # Store the results
        self.scraped_posts = collected_posts
        
        # Save to file
        if collected_posts:
            self._save_posts(collected_posts, query)
        
        return collected_posts
    
    def _extract_post_data(self, submission: Submission, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive data from a Reddit post/submission.
        
        Args:
            submission: PRAW Submission object
            query: Original search query
            
        Returns:
            Dictionary with post data or None if extraction failed
        """
        try:
            # Skip non-accessible or removed posts
            if not hasattr(submission, 'title') or not submission.title:
                return None
            
            # Basic post data
            post_data = {
                'id': submission.id,
                'title': submission.title,
                'author': str(submission.author) if submission.author else '[deleted]',
                'subreddit': submission.subreddit.display_name,
                'url': submission.url,
                'permalink': f"https://www.reddit.com{submission.permalink}",
                'created_utc': submission.created_utc,
                'created_date': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'is_self': submission.is_self,
                'selftext': submission.selftext if submission.is_self else '',
                'link_flair_text': submission.link_flair_text,
                'is_original_content': submission.is_original_content,
                'over_18': submission.over_18,
                'pinned': submission.pinned,
                'stickied': submission.stickied,
                'spoiler': submission.spoiler,
                'query': query
            }
            
            # Calculate engagement metrics
            post_data['engagement_score'] = self._calculate_engagement_score(submission)
            
            # Calculate text similarity to the query
            post_data['query_similarity'] = self._calculate_text_similarity(
                f"{submission.title} {submission.selftext}",
                query
            )
            
            # Analyze sentiment if available
            if self.sentiment_analyzer:
                full_text = f"{submission.title} {submission.selftext}"
                sentiment = self.sentiment_analyzer.polarity_scores(full_text)
                post_data['sentiment'] = {
                    'compound': sentiment['compound'],
                    'positive': sentiment['pos'],
                    'neutral': sentiment['neu'],
                    'negative': sentiment['neg']
                }
                
                # Simplified sentiment label
                if sentiment['compound'] >= 0.05:
                    post_data['sentiment_label'] = 'positive'
                elif sentiment['compound'] <= -0.05:
                    post_data['sentiment_label'] = 'negative'
                else:
                    post_data['sentiment_label'] = 'neutral'
            
            # Extract keywords
            post_data['keywords'] = self._extract_keywords(
                f"{submission.title} {submission.selftext}"
            )
            
            return post_data
            
        except Exception as e:
            self.logger.debug(f"Error extracting post data for submission {getattr(submission, 'id', 'unknown')}: {str(e)}")
            return None
    
    def _calculate_engagement_score(self, submission: Submission) -> float:
        """
        Calculate a normalized engagement score for a submission.
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            Engagement score (0.0-100.0)
        """
        # Base factors
        upvotes = getattr(submission, 'score', 0) or 0
        upvote_ratio = getattr(submission, 'upvote_ratio', 0.5) or 0.5
        comment_count = getattr(submission, 'num_comments', 0) or 0
        awards = len(getattr(submission, 'all_awardings', [])) if hasattr(submission, 'all_awardings') else 0
        
        # Calculate age in hours
        age_hours = (datetime.now() - datetime.fromtimestamp(submission.created_utc)).total_seconds() / 3600
        
        # Normalize by age (recent posts have fewer comments/votes)
        age_factor = max(24.0 / max(age_hours, 1.0), 1.0)  # Cap at 1.0 for posts older than 24 hours
        
        # Calculate adjusted metrics
        adjusted_upvotes = upvotes * upvote_ratio  # Net positive votes
        adjusted_comments = comment_count * age_factor
        
        # Combine factors (weights can be tuned)
        raw_score = (adjusted_upvotes * 1.0) + (adjusted_comments * 2.0) + (awards * 5.0)
        
        # Logarithmic scaling to prevent high outliers
        if raw_score > 0:
            scaled_score = min(100.0, 10.0 * (1.0 + (1.0 / 5.0) * (1.0 + 3.0 * adjusted_upvotes) ** 0.8))
        else:
            scaled_score = 0.0
        
        return scaled_score
    
    def _calculate_text_similarity(self, text: str, query: str) -> float:
        """
        Calculate simple similarity between text and query.
        
        Args:
            text: Text to compare
            query: Query to compare against
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not text or not query:
            return 0.0
        
        # Normalize
        text = text.lower()
        query = query.lower()
        
        # Split into words
        query_words = set(query.split())
        
        # Count word matches
        matches = sum(1 for word in query_words if word in text)
        
        # Calculate similarity
        if len(query_words) > 0:
            return matches / len(query_words)
        else:
            return 0.0
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract most significant keywords from text.
        
        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Normalize text
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'about', 'as', 'from', 'that', 'this', 'these', 'those', 'is', 'are', 'was', 
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'or',
            'if', 'then', 'else', 'so', 'but', 'because', 'since', 'while', 'when',
            'where', 'what', 'which', 'who', 'whom', 'how', 'why', 'you', 'your',
            'yours', 'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours', 'they',
            'them', 'their', 'theirs', 'he', 'him', 'his', 'she', 'her', 'hers',
            'it', 'its', 'itself', 'myself', 'yourself', 'himself', 'herself',
            'ourselves', 'yourselves', 'themselves', 'each', 'few', 'many',
            'some', 'any', 'all', 'most', 'more', 'less', 'other', 'another',
            'such', 'no', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
            'just', 'even', 'also', 'back'
        }
        
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get most common words
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _save_posts(self, posts: List[Dict[str, Any]], query: str) -> None:
        """
        Save collected posts to JSON file.
        
        Args:
            posts: List of post dictionaries
            query: Search query used
        """
        if not posts:
            return
        
        try:
            # Create sanitized filename from query
            sanitized_query = re.sub(r'[^\w\s]', '', query).strip().replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reddit_posts_{sanitized_query}_{timestamp}.json"
            
            # Save to file
            filepath = os.path.join(self.output_dir, 'raw', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'metadata': {
                            'query': query,
                            'timestamp': datetime.now().isoformat(),
                            'post_count': len(posts)
                        },
                        'posts': posts
                    },
                    f,
                    indent=2
                )
            
            self.logger.info(f"Saved {len(posts)} posts to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving posts: {str(e)}")
    
    def scrape_comments(
        self,
        post_ids: Optional[List[str]] = None,
        query: Optional[str] = None,
        limit_per_post: int = 50,
        sort_by: str = 'top'
    ) -> List[Dict[str, Any]]:
        """
        Scrape comments from Reddit posts with detailed analysis.
        
        Args:
            post_ids: List of Reddit post IDs to scrape comments from
            query: Optional label for the data collection
            limit_per_post: Maximum comments to scrape per post
            sort_by: How to sort comments ('top', 'best', 'new', 'controversial')
            
        Returns:
            List of comment dictionaries
        """
        if not self.reddit:
            self.logger.warning("Reddit client not initialized, cannot scrape comments")
            return []
        
        collected_comments = []
        
        # If no post IDs provided, use the most recent scraped posts
        if not post_ids and self.scraped_posts:
            post_ids = [post['id'] for post in self.scraped_posts]
        
        if not post_ids:
            self.logger.warning("No post IDs provided for comment scraping")
            return []
        
        # Process each post
        for post_id in post_ids:
            try:
                self.logger.info(f"Scraping comments from post {post_id}")
                
                # Get submission
                submission = self._execute_with_retry(
                    self.reddit.submission, id=post_id
                )
                
                if not submission:
                    continue
                
                # Sort comments
                if sort_by == 'best':
                    submission.comment_sort = 'best'
                elif sort_by == 'new':
                    submission.comment_sort = 'new'
                elif sort_by == 'controversial':
                    submission.comment_sort = 'controversial'
                else:  # default to top
                    submission.comment_sort = 'top'
                
                # Fetch comments
                self._execute_with_retry(
                    submission.comments.replace_more, limit=5
                )
                
                # Get the comments
                comments = list(submission.comments.list())[:limit_per_post]
                
                # Process comments
                post_comments = []
                for comment in comments:
                    comment_data = self._extract_comment_data(comment, submission, query)
                    if comment_data:
                        post_comments.append(comment_data)
                        collected_comments.append(comment_data)
                
                # Store metadata with the post itself
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': submission.subreddit.display_name,
                    'url': submission.url,
                    'permalink': f"https://www.reddit.com{submission.permalink}",
                    'created_utc': submission.created_utc,
                    'created_date': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'comments': post_comments
                }
                
                # Save post with its comments
                self._save_post_comments(post_data, query or 'unknown')
                
            except Exception as e:
                self.logger.warning(f"Error scraping comments from post {post_id}: {str(e)}")
        
        # Store the results
        self.scraped_comments = collected_comments
        
        return collected_comments
    
    def _extract_comment_data(
        self, 
        comment: Comment, 
        submission: Submission, 
        query: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive data from a Reddit comment.
        
        Args:
            comment: PRAW Comment object
            submission: Parent PRAW Submission object
            query: Original search query
            
        Returns:
            Dictionary with comment data or None if extraction failed
        """
        try:
            # Skip removed/deleted comments
            if not hasattr(comment, 'body') or not comment.body:
                return None
            
            # Basic comment data
            comment_data = {
                'id': comment.id,
                'body': comment.body,
                'author': str(comment.author) if comment.author else '[deleted]',
                'created_utc': comment.created_utc,
                'created_date': datetime.fromtimestamp(comment.created_utc).isoformat(),
                'score': comment.score,
                'parent_submission_id': submission.id,
                'is_submitter': comment.is_submitter,
                'permalink': f"https://www.reddit.com{comment.permalink}",
                'query': query
            }
            
            # Analyze sentiment if available
            if self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer.polarity_scores(comment.body)
                comment_data['sentiment'] = {
                    'compound': sentiment['compound'],
                    'positive': sentiment['pos'],
                    'neutral': sentiment['neu'],
                    'negative': sentiment['neg']
                }
                
                # Simplified sentiment label
                if sentiment['compound'] >= 0.05:
                    comment_data['sentiment_label'] = 'positive'
                elif sentiment['compound'] <= -0.05:
                    comment_data['sentiment_label'] = 'negative'
                else:
                    comment_data['sentiment_label'] = 'neutral'
            
            # Extract keywords
            comment_data['keywords'] = self._extract_keywords(comment.body)
            
            # Track parent comments
            if hasattr(comment, 'parent_id'):
                comment_data['parent_id'] = comment.parent_id
            
            return comment_data
            
        except Exception as e:
            self.logger.debug(f"Error extracting comment data for comment {getattr(comment, 'id', 'unknown')}: {str(e)}")
            return None
    
    def _save_post_comments(self, post_data: Dict[str, Any], query: str) -> None:
        """
        Save post with its comments to JSON file.
        
        Args:
            post_data: Post dictionary with comments
            query: Search query used
        """
        try:
            # Create sanitized filename
            post_id = post_data['id']
            sanitized_query = re.sub(r'[^\w\s]', '', query).strip().replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reddit_post_comments_{post_id}_{sanitized_query}_{timestamp}.json"
            
            # Save to file
            filepath = os.path.join(self.output_dir, 'raw', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'metadata': {
                            'post_id': post_id,
                            'query': query,
                            'timestamp': datetime.now().isoformat(),
                            'comment_count': len(post_data.get('comments', []))
                        },
                        'post': post_data
                    },
                    f,
                    indent=2
                )
            
            self.logger.info(f"Saved post {post_id} with {len(post_data.get('comments', []))} comments to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving post comments: {str(e)}")
    
    def get_product_mentions(self, product: str, subreddits: Optional[List[str]] = None, 
                          limit: int = 100) -> Dict[str, Any]:
        """
        Get comprehensive product mentions and sentiment analysis.
        
        Args:
            product: Product name
            subreddits: List of subreddits to search
            limit: Maximum posts to retrieve
            
        Returns:
            Dictionary with product mention analysis
        """
        # First search for posts about the product
        posts = self.search_posts(product, subreddits=subreddits, limit=limit)
        
        # Then collect comments from those posts
        post_ids = [post['id'] for post in posts]
        comments = self.scrape_comments(post_ids=post_ids, query=product)
        
        # Perform analysis
        return self._analyze_product_mentions(product, posts, comments)
    
    def _analyze_product_mentions(
        self, 
        product: str, 
        posts: List[Dict[str, Any]], 
        comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze product mentions in posts and comments.
        
        Args:
            product: Product name
            posts: List of post dictionaries
            comments: List of comment dictionaries
            
        Returns:
            Dictionary with product mention analysis
        """
        if not posts and not comments:
            return {
                'product': product,
                'mention_count': 0,
                'post_count': 0,
                'comment_count': 0,
                'sentiment_distribution': {},
                'trending_keywords': [],
                'engagement_stats': {}
            }
        
        # Clean product name for matching
        clean_product = product.lower()
        product_words = set(clean_product.split())
        
        # Track matching content
        matching_posts = []
        matching_comments = []
        
        # Find posts mentioning the product
        for post in posts:
            post_text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
            if clean_product in post_text or any(word in post_text for word in product_words):
                matching_posts.append(post)
        
        # Find comments mentioning the product
        for comment in comments:
            comment_text = comment.get('body', '').lower()
            if clean_product in comment_text or any(word in comment_text for word in product_words):
                matching_comments.append(comment)
        
        # Extract sentiment information
        post_sentiments = [post.get('sentiment_label', 'neutral') for post in matching_posts 
                          if 'sentiment_label' in post]
        comment_sentiments = [comment.get('sentiment_label', 'neutral') for comment in matching_comments 
                             if 'sentiment_label' in comment]
        
        # Combine sentiments
        all_sentiments = post_sentiments + comment_sentiments
        
        # Calculate sentiment distribution
        sentiment_counts = Counter(all_sentiments)
        total_sentiments = len(all_sentiments) if all_sentiments else 1  # Avoid division by zero
        
        sentiment_distribution = {
            'positive': sentiment_counts.get('positive', 0) / total_sentiments,
            'neutral': sentiment_counts.get('neutral', 0) / total_sentiments,
            'negative': sentiment_counts.get('negative', 0) / total_sentiments
        }
        
        # Extract trending keywords
        all_keywords = []
        for post in matching_posts:
            all_keywords.extend(post.get('keywords', []))
        for comment in matching_comments:
            all_keywords.extend(comment.get('keywords', []))
        
        # Remove the product name from keywords
        all_keywords = [keyword for keyword in all_keywords 
                       if keyword.lower() not in product_words]
        
        # Get top keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(15)
        
        # Calculate engagement stats
        engagement_scores = [post.get('engagement_score', 0) for post in matching_posts 
                            if 'engagement_score' in post]
        
        engagement_stats = {
            'avg_engagement': sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
            'max_engagement': max(engagement_scores) if engagement_scores else 0,
            'avg_score': sum(post.get('score', 0) for post in matching_posts) / len(matching_posts) if matching_posts else 0,
            'avg_comments': sum(post.get('num_comments', 0) for post in matching_posts) / len(matching_posts) if matching_posts else 0
        }
        
        # Include subreddit distribution
        subreddits = [post.get('subreddit', 'unknown') for post in matching_posts]
        subreddit_counts = Counter(subreddits)
        top_subreddits = subreddit_counts.most_common(10)
        
        # Return comprehensive analysis
        return {
            'product': product,
            'mention_count': len(matching_posts) + len(matching_comments),
            'post_count': len(matching_posts),
            'comment_count': len(matching_comments),
            'sentiment_distribution': sentiment_distribution,
            'sentiment_counts': dict(sentiment_counts),
            'trending_keywords': [{'keyword': kw, 'count': count} for kw, count in top_keywords],
            'engagement_stats': engagement_stats,
            'top_subreddits': [{'subreddit': sr, 'count': count} for sr, count in top_subreddits],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_competitor_comparison(
        self, 
        product: str, 
        competitors: List[str], 
        subreddits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare a product with its competitors based on Reddit data.
        
        Args:
            product: Main product name
            competitors: List of competitor product names
            subreddits: List of subreddits to search
            
        Returns:
            Dictionary with comparative analysis
        """
        # Collect data for main product
        main_product_data = self.get_product_mentions(product, subreddits)
        
        # Collect data for competitors
        competitor_data = {}
        for competitor in competitors:
            competitor_data[competitor] = self.get_product_mentions(competitor, subreddits)
        
        # Perform comparative analysis
        return self._create_comparative_analysis(product, main_product_data, competitor_data)
    
    def _create_comparative_analysis(
        self,
        main_product: str,
        main_data: Dict[str, Any],
        competitor_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create comparative analysis between products.
        
        Args:
            main_product: Main product name
            main_data: Main product analysis dictionary
            competitor_data: Dictionary mapping competitor names to their analysis
            
        Returns:
            Dictionary with comparative analysis
        """
        # Compare sentiment
        sentiment_comparison = {
            main_product: main_data.get('sentiment_distribution', {})
        }
        
        for competitor, data in competitor_data.items():
            sentiment_comparison[competitor] = data.get('sentiment_distribution', {})
        
        # Compare engagement
        engagement_comparison = {
            main_product: main_data.get('engagement_stats', {})
        }
        
        for competitor, data in competitor_data.items():
            engagement_comparison[competitor] = data.get('engagement_stats', {})
        
        # Compare mention counts
        mention_counts = {
            main_product: main_data.get('mention_count', 0)
        }
        
        for competitor, data in competitor_data.items():
            mention_counts[competitor] = data.get('mention_count', 0)
        
        # Find overlapping and unique keywords
        main_keywords = set([item['keyword'] for item in main_data.get('trending_keywords', [])])
        
        shared_keywords = {}
        unique_keywords = {
            main_product: list(main_keywords)
        }
        
        for competitor, data in competitor_data.items():
            comp_keywords = set([item['keyword'] for item in data.get('trending_keywords', [])])
            
            # Find shared keywords
            shared = main_keywords.intersection(comp_keywords)
            if shared:
                shared_keywords[competitor] = list(shared)
            
            # Find unique keywords
            unique_keywords[competitor] = list(comp_keywords.difference(main_keywords))
            unique_keywords[main_product] = list(main_keywords.difference(comp_keywords))
        
        # Calculate sentiment advantage
        sentiment_advantage = {}
        main_positive = main_data.get('sentiment_distribution', {}).get('positive', 0)
        main_negative = main_data.get('sentiment_distribution', {}).get('negative', 0)
        
        for competitor, data in competitor_data.items():
            comp_positive = data.get('sentiment_distribution', {}).get('positive', 0)
            comp_negative = data.get('sentiment_distribution', {}).get('negative', 0)
            
            # Positive sentiment advantage
            if main_positive > comp_positive:
                advantage = (main_positive - comp_positive) / max(comp_positive, 0.01)  # Avoid division by zero
                sentiment_advantage[competitor] = {
                    'advantage': 'positive',
                    'margin': advantage
                }
            elif comp_positive > main_positive:
                advantage = (comp_positive - main_positive) / max(main_positive, 0.01)
                sentiment_advantage[competitor] = {
                    'advantage': 'negative',
                    'margin': advantage
                }
            else:
                sentiment_advantage[competitor] = {
                    'advantage': 'neutral',
                    'margin': 0.0
                }
        
        # Return comparative analysis
        return {
            'main_product': main_product,
            'competitors': list(competitor_data.keys()),
            'sentiment_comparison': sentiment_comparison,
            'engagement_comparison': engagement_comparison,
            'mention_counts': mention_counts,
            'shared_keywords': shared_keywords,
            'unique_keywords': unique_keywords,
            'sentiment_advantage': sentiment_advantage,
            'timestamp': datetime.now().isoformat()
        }
    
    def extract_ad_insights(self, product: str, brand: str, industry: str) -> Dict[str, Any]:
        """
        Extract advertising insights for a product/brand combination.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            
        Returns:
            Dictionary with ad insights
        """
        # Format search queries
        product_query = product
        brand_query = brand
        combined_query = f"{brand} {product}"
        
        # Find relevant subreddits
        subreddits = self.find_relevant_subreddits(
            [product, brand, industry, f"{brand} {product}"]
        )
        
        # Collect data
        product_posts = self.search_posts(product_query, subreddits=subreddits, limit=50)
        brand_posts = self.search_posts(brand_query, subreddits=subreddits, limit=50)
        combined_posts = self.search_posts(combined_query, subreddits=subreddits, limit=50)
        
        # Get all post IDs
        all_post_ids = []
        all_post_ids.extend([post['id'] for post in product_posts])
        all_post_ids.extend([post['id'] for post in brand_posts])
        all_post_ids.extend([post['id'] for post in combined_posts])
        
        # Remove duplicates
        unique_post_ids = list(set(all_post_ids))
        
        # Collect comments
        all_comments = self.scrape_comments(post_ids=unique_post_ids, query=combined_query)
        
        # Generate insights
        return self._generate_ad_insights(product, brand, industry, 
                                        product_posts, brand_posts, 
                                        combined_posts, all_comments)
    
    def _generate_ad_insights(
        self,
        product: str,
        brand: str,
        industry: str,
        product_posts: List[Dict[str, Any]],
        brand_posts: List[Dict[str, Any]],
        combined_posts: List[Dict[str, Any]],
        comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate advertising insights from collected data.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            product_posts: Posts about the product
            brand_posts: Posts about the brand
            combined_posts: Posts about product and brand together
            comments: All collected comments
            
        Returns:
            Dictionary with ad insights
        """
        # Combine all content for full analysis
        all_posts = []
        all_posts.extend(product_posts)
        all_posts.extend(brand_posts)
        all_posts.extend(combined_posts)
        
        # Remove duplicate posts
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        # Extract sentiment data
        all_sentiment_labels = []
        all_sentiment_labels.extend([post.get('sentiment_label', 'neutral') for post in unique_posts 
                                   if 'sentiment_label' in post])
        all_sentiment_labels.extend([comment.get('sentiment_label', 'neutral') for comment in comments 
                                   if 'sentiment_label' in comment])
        
        sentiment_counts = Counter(all_sentiment_labels)
        
        # Extract all keywords
        all_keywords = []
        for post in unique_posts:
            all_keywords.extend(post.get('keywords', []))
        for comment in comments:
            all_keywords.extend(comment.get('keywords', []))
        
        keyword_counts = Counter(all_keywords)
        
        # Extract engagement patterns
        high_engagement_posts = sorted(
            [post for post in unique_posts if 'engagement_score' in post],
            key=lambda p: p.get('engagement_score', 0),
            reverse=True
        )[:10]  # Top 10 posts
        
        # Extract key elements from high engagement posts
        key_elements = self._extract_ad_elements(high_engagement_posts)
        
        # Get trending topics
        trending_keywords = [
            {'keyword': kw, 'count': count} 
            for kw, count in keyword_counts.most_common(20)
        ]
        
        # Get visual focus suggestions
        visual_focus = self._suggest_visual_focus(product, brand, key_elements)
        
        # Generate recommended formats
        recommended_formats = self._generate_ad_format_recommendations(product, brand, industry, key_elements)
        
        # Get text placements
        text_placement = self._suggest_text_placement(high_engagement_posts)
        
        # Determine brand perception
        brand_perception = self._analyze_brand_perception(brand, brand_posts, comments)
        
        # Determine product perception
        product_perception = self._analyze_product_perception(product, product_posts, comments)
        
        # Suggestions for ad copy
        ad_copy_suggestions = self._generate_ad_copy_suggestions(
            product, brand, trending_keywords, key_elements, 
            brand_perception, product_perception
        )
        
        # Compile insights
        insights = {
            'product': product,
            'brand': brand,
            'industry': industry,
            'recommended_format': recommended_formats[0] if recommended_formats else "Product-focused with clean background",
            'alternative_formats': recommended_formats[1:3] if len(recommended_formats) > 1 else [],
            'text_placement': text_placement,
            'text_style': key_elements.get('text_style', 'minimal'),
            'key_elements': key_elements.get('elements', 
                                           ['product close-up', 'brand elements', 'quality suggestion']),
            'visual_focus': visual_focus,
            'color_scheme': key_elements.get('color_scheme', 'brand colors with accent highlights'),
            'trending_keywords': [kw['keyword'] for kw in trending_keywords[:10]],
            'sentiment': {
                'positive': sentiment_counts.get('positive', 0) / max(sum(sentiment_counts.values()), 1),
                'neutral': sentiment_counts.get('neutral', 0) / max(sum(sentiment_counts.values()), 1),
                'negative': sentiment_counts.get('negative', 0) / max(sum(sentiment_counts.values()), 1)
            },
            'ad_copy_suggestions': ad_copy_suggestions,
            'brand_perception': brand_perception,
            'product_perception': product_perception,
            'data_sources': {
                'posts_analyzed': len(unique_posts),
                'comments_analyzed': len(comments),
                'subreddits': list(set(post.get('subreddit', 'unknown') for post in unique_posts))
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Save insights to file
        self._save_ad_insights(insights, product, brand)
        
        return insights
    
    def _extract_ad_elements(self, high_engagement_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract key advertising elements from high engagement posts.
        
        Args:
            high_engagement_posts: List of high engagement posts
            
        Returns:
            Dictionary with key ad elements
        """
        # Extract all text
        all_text = ""
        for post in high_engagement_posts:
            all_text += f"{post.get('title', '')} {post.get('selftext', '')} "
        
        # Look for key patterns
        patterns = {
            'minimalist': r'\b(minimal|minimalist|clean|simple|elegant)\b',
            'detailed': r'\b(detailed|comprehensive|complete|thorough)\b',
            'emotional': r'\b(emotional|feeling|touching|heartfelt|moving)\b',
            'technical': r'\b(technical|specs|detailed|performance|features)\b',
            'lifestyle': r'\b(lifestyle|life|living|everyday|daily)\b',
            'comparison': r'\b(versus|vs|compared|comparison|better than)\b',
            'testimonial': r'\b(testimonial|review|experience|tried|used)\b',
            'demo': r'\b(demonstration|demo|showing|shows|see it)\b',
            'before_after': r'\b(before|after|transformation|changed|improved)\b',
            'problem_solution': r'\b(problem|solution|resolved|fixed|solved)\b'
        }
        
        # Count pattern matches
        pattern_counts = {}
        for style, pattern in patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            pattern_counts[style] = matches
        
        # Get dominant styles
        sorted_styles = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        dominant_styles = [style for style, count in sorted_styles if count > 0][:3]
        
        # Convert styles to elements
        style_to_elements = {
            'minimalist': ['clean background', 'product focus', 'minimal text'],
            'detailed': ['product details', 'feature highlights', 'specifications'],
            'emotional': ['people using product', 'emotional expression', 'lifestyle context'],
            'technical': ['product specifications', 'technical details', 'performance metrics'],
            'lifestyle': ['product in use', 'daily context', 'lifestyle setting'],
            'comparison': ['side-by-side comparison', 'competitive advantage', 'differentiation'],
            'testimonial': ['customer quote', 'user experience', 'social proof'],
            'demo': ['product demonstration', 'usage scenario', 'functionality'],
            'before_after': ['before/after imagery', 'transformation', 'results'],
            'problem_solution': ['problem statement', 'solution presentation', 'pain point address']
        }
        
        # Map styles to text styles
        style_to_text = {
            'minimalist': 'minimal',
            'detailed': 'detailed',
            'emotional': 'emotive',
            'technical': 'technical',
            'lifestyle': 'casual',
            'comparison': 'comparative',
            'testimonial': 'testimonial',
            'demo': 'instructional',
            'before_after': 'transformative',
            'problem_solution': 'problem-solving'
        }
        
        # Map styles to color schemes
        style_to_color = {
            'minimalist': 'monochromatic with accent',
            'detailed': 'rich color palette',
            'emotional': 'warm tones with emotional cues',
            'technical': 'blue and grey professional scheme',
            'lifestyle': 'vibrant and natural colors',
            'comparison': 'contrasting dual scheme',
            'testimonial': 'trust-building blues and whites',
            'demo': 'clear instructional color scheme',
            'before_after': 'contrasting transformation colors',
            'problem_solution': 'problem/solution color contrast'
        }
        
        # Get elements for dominant styles
        elements = []
        for style in dominant_styles:
            if style in style_to_elements:
                elements.extend(style_to_elements[style])
        
        # Get text style
        text_style = style_to_text.get(dominant_styles[0], 'minimal') if dominant_styles else 'minimal'
        
        # Get color scheme
        color_scheme = style_to_color.get(dominant_styles[0], 'brand colors with accent highlights') if dominant_styles else 'brand colors with accent highlights'
        
        return {
            'elements': list(set(elements[:5])),  # Unique top 5 elements
            'dominant_styles': dominant_styles,
            'text_style': text_style,
            'color_scheme': color_scheme
        }
    
    def _suggest_visual_focus(
        self, 
        product: str, 
        brand: str, 
        key_elements: Dict[str, Any]
    ) -> str:
        """
        Suggest visual focus for the ad based on data.
        
        Args:
            product: Product name
            brand: Brand name
            key_elements: Dictionary with key ad elements
            
        Returns:
            Visual focus suggestion
        """
        # Get product type
        product_lower = product.lower()
        
        # Product-specific suggestions
        if any(tech in product_lower for tech in ['phone', 'iphone', 'smartphone']):
            return "phone screen and innovative features"
            
        elif any(term in product_lower for term in ['laptop', 'computer', 'pc', 'macbook']):
            return "sleek design and screen display"
            
        elif any(term in product_lower for term in ['car', 'vehicle', 'auto']):
            return "dramatic vehicle angle with lighting emphasis"
            
        elif any(term in product_lower for term in ['shoe', 'sneaker', 'footwear']):
            return "shoe profile with texture details"
            
        elif any(term in product_lower for term in ['watch', 'timepiece']):
            return "watch face and craftsmanship details"
            
        elif any(term in product_lower for term in ['skincare', 'cream', 'lotion']):
            return "product texture and elegant packaging"
            
        # Use key elements for generic recommendations
        dominant_styles = key_elements.get('dominant_styles', [])
        
        if 'minimalist' in dominant_styles:
            return "clean product showcase with minimal styling"
        elif 'detailed' in dominant_styles:
            return "product details and feature highlights"
        elif 'lifestyle' in dominant_styles:
            return "product in lifestyle context"
        elif 'technical' in dominant_styles:
            return "technical features and performance elements"
        elif 'emotional' in dominant_styles:
            return "emotional benefits of product usage"
        
        # Default focus
        return "product with professional lighting and staging"
    
    def _generate_ad_format_recommendations(
        self,
        product: str,
        brand: str,
        industry: str,
        key_elements: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommended ad formats based on product, brand, and industry.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            key_elements: Dictionary with key ad elements
            
        Returns:
            List of recommended ad formats
        """
        # Industry-specific formats
        industry_formats = {
            'technology': [
                "Feature showcase with clean background",
                "Lifestyle tech usage in context",
                "Comparison with competitive products"
            ],
            'fashion': [
                "Lifestyle model with product",
                "Close-up texture and details",
                "Urban setting with authentic styling"
            ],
            'automotive': [
                "Dynamic vehicle angle with motion suggestion",
                "Interior luxury details",
                "Lifestyle vehicle usage scenario"
            ],
            'beauty': [
                "Before/after transformation",
                "Product with ingredient visualization",
                "Close-up application demonstration"
            ],
            'food': [
                "Appetizing close-up with steam",
                "Lifestyle usage context",
                "Ingredient showcase with quality emphasis"
            ],
            'health': [
                "Active lifestyle with product",
                "Before/after results",
                "Scientific approach with visual data"
            ],
            'home': [
                "Product in beautiful home context",
                "Problem/solution demonstration",
                "Lifestyle improvement scenario"
            ]
        }
        
        # Clean industry string
        industry_lower = industry.lower()
        identified_industry = None
        
        # Map to specific industry
        for ind in industry_formats:
            if ind in industry_lower:
                identified_industry = ind
                break
        
        # Use key elements if no specific industry match
        if not identified_industry:
            dominant_styles = key_elements.get('dominant_styles', [])
            
            if dominant_styles:
                style_formats = {
                    'minimalist': [
                        "Clean product showcase with minimal styling",
                        "Simple background with product focus",
                        "Elegant minimal presentation"
                    ],
                    'detailed': [
                        "Detailed product feature showcase",
                        "Comprehensive benefit visualization",
                        "Detailed close-up of key features"
                    ],
                    'lifestyle': [
                        "Product in authentic lifestyle context",
                        "Daily usage scenario",
                        "Real-life benefit demonstration"
                    ],
                    'technical': [
                        "Technical specification highlight",
                        "Engineering and performance focus",
                        "Data-driven feature presentation"
                    ],
                    'emotional': [
                        "Emotional benefit storytelling",
                        "Customer relationship focus",
                        "Aspirational lifestyle imagery"
                    ]
                }
                
                for style in dominant_styles:
                    if style in style_formats:
                        return style_formats[style]
            
            # Fallback to generic recommendations
            return [
                "Product-focused with clean background",
                "Lifestyle context with product in use",
                "Feature highlight with benefit messaging"
            ]
        
        # Return industry-specific formats
        return industry_formats[identified_industry]
    
    def _suggest_text_placement(self, high_engagement_posts: List[Dict[str, Any]]) -> str:
        """
        Suggest text placement based on high engagement posts.
        
        Args:
            high_engagement_posts: List of high engagement posts
            
        Returns:
            Text placement suggestion
        """
        # Extract all text
        all_text = ""
        for post in high_engagement_posts:
            all_text += f"{post.get('title', '')} {post.get('selftext', '')} "
        
        # Look for placement cues in text
        placement_patterns = {
            'centered': r'\b(center|centered|middle|balanced)\b',
            'top': r'\b(top|header|above|headline)\b',
            'bottom': r'\b(bottom|footer|below|underneath)\b',
            'left': r'\b(left|side|margin)\b',
            'right': r'\b(right|side|margin)\b',
            'overlay': r'\b(overlay|over|superimposed|on top)\b'
        }
        
        # Count pattern matches
        placement_counts = {}
        for placement, pattern in placement_patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            placement_counts[placement] = matches
        
        # Get most mentioned placement
        if placement_counts:
            sorted_placements = sorted(placement_counts.items(), key=lambda x: x[1], reverse=True)
            top_placement = sorted_placements[0][0] if sorted_placements else 'centered'
            
            # Map to specific placement types
            placement_map = {
                'centered': 'centered',
                'top': 'top_centered',
                'bottom': 'bottom_centered',
                'left': 'left_aligned',
                'right': 'right_aligned',
                'overlay': 'overlay_centered'
            }
            
            return placement_map.get(top_placement, 'centered')
        
        # Default placement
        return 'centered'
    
    def _analyze_brand_perception(
        self,
        brand: str,
        brand_posts: List[Dict[str, Any]],
        comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze brand perception from posts and comments.
        
        Args:
            brand: Brand name
            brand_posts: Posts about the brand
            comments: All collected comments
            
        Returns:
            Brand perception analysis
        """
        # Clean brand name for matching
        clean_brand = brand.lower()
        
        # Find brand mentions
        brand_mentions = []
        for post in brand_posts:
            if 'sentiment_label' in post:
                brand_mentions.append({
                    'text': f"{post.get('title', '')} {post.get('selftext', '')}",
                    'sentiment': post.get('sentiment_label', 'neutral')
                })
        
        for comment in comments:
            comment_text = comment.get('body', '').lower()
            if clean_brand in comment_text and 'sentiment_label' in comment:
                brand_mentions.append({
                    'text': comment.get('body', ''),
                    'sentiment': comment.get('sentiment_label', 'neutral')
                })
        
        # Calculate sentiment distribution
        sentiment_counts = Counter([mention['sentiment'] for mention in brand_mentions])
        total_mentions = len(brand_mentions) if brand_mentions else 1  # Avoid division by zero
        
        sentiment_distribution = {
            'positive': sentiment_counts.get('positive', 0) / total_mentions,
            'neutral': sentiment_counts.get('neutral', 0) / total_mentions,
            'negative': sentiment_counts.get('negative', 0) / total_mentions
        }
        
        # Determine key attributes mentioned with brand
        attributes = self._extract_brand_attributes(brand_mentions)
        
        # Determine overall brand perception
        overall_sentiment = 'neutral'
        if sentiment_distribution['positive'] > sentiment_distribution['negative'] + 0.1:
            overall_sentiment = 'positive'
        elif sentiment_distribution['negative'] > sentiment_distribution['positive'] + 0.1:
            overall_sentiment = 'negative'
        
        return {
            'brand': brand,
            'mention_count': len(brand_mentions),
            'sentiment_distribution': sentiment_distribution,
            'key_attributes': attributes,
            'overall_perception': overall_sentiment
        }
    
    def _extract_brand_attributes(self, mentions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Extract key attributes mentioned about a brand.
        
        Args:
            mentions: List of brand mentions with text and sentiment
            
        Returns:
            List of brand attribute dictionaries
        """
        # Attribute patterns to look for
        attribute_patterns = {
            'quality': r'\b(quality|well-made|premium|excellent|good|great)\b',
            'price': r'\b(price|expensive|cheap|affordable|cost|value|worth)\b',
            'design': r'\b(design|look|style|aesthetic|sleek|beautiful|elegant)\b',
            'innovation': r'\b(innovative|new|novel|unique|different|fresh|revolutionary)\b',
            'reliability': r'\b(reliable|dependable|consistent|trustworthy|solid)\b',
            'performance': r'\b(performance|fast|slow|speed|efficient|powerful)\b',
            'support': r'\b(support|service|customer service|help|assistance)\b',
            'reputation': r'\b(reputation|brand|name|known for|famous|respected)\b'
        }
        
        # Count attribute mentions by sentiment
        attribute_sentiments = {}
        
        for attribute, pattern in attribute_patterns.items():
            attribute_sentiments[attribute] = {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total': 0
            }
        
        # Process each mention
        for mention in mentions:
            text = mention['text'].lower()
            sentiment = mention['sentiment']
            
            for attribute, pattern in attribute_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    attribute_sentiments[attribute][sentiment] += 1
                    attribute_sentiments[attribute]['total'] += 1
        
        # Create attribute list with sentiment
        attributes = []
        for attribute, sentiments in attribute_sentiments.items():
            if sentiments['total'] > 0:
                # Calculate dominant sentiment
                max_sentiment = max(
                    ['positive', 'neutral', 'negative'],
                    key=lambda s: sentiments[s]
                )
                
                attributes.append({
                    'attribute': attribute,
                    'mentions': sentiments['total'],
                    'dominant_sentiment': max_sentiment,
                    'sentiment_distribution': {
                        'positive': sentiments['positive'] / sentiments['total'],
                        'neutral': sentiments['neutral'] / sentiments['total'],
                        'negative': sentiments['negative'] / sentiments['total']
                    }
                })
        
        # Sort by mention count
        return sorted(attributes, key=lambda a: a['mentions'], reverse=True)
    
    def _analyze_product_perception(
        self,
        product: str,
        product_posts: List[Dict[str, Any]],
        comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze product perception from posts and comments.
        
        Args:
            product: Product name
            product_posts: Posts about the product
            comments: All collected comments
            
        Returns:
            Product perception analysis
        """
        # Similar to brand perception but focused on product
        # Clean product name for matching
        clean_product = product.lower()
        product_words = set(clean_product.split())
        
        # Find product mentions
        product_mentions = []
        for post in product_posts:
            if 'sentiment_label' in post:
                product_mentions.append({
                    'text': f"{post.get('title', '')} {post.get('selftext', '')}",
                    'sentiment': post.get('sentiment_label', 'neutral')
                })
        
        for comment in comments:
            comment_text = comment.get('body', '').lower()
            if clean_product in comment_text or any(word in comment_text for word in product_words):
                if 'sentiment_label' in comment:
                    product_mentions.append({
                        'text': comment.get('body', ''),
                        'sentiment': comment.get('sentiment_label', 'neutral')
                    })
        
        # Calculate sentiment distribution
        sentiment_counts = Counter([mention['sentiment'] for mention in product_mentions])
        total_mentions = len(product_mentions) if product_mentions else 1  # Avoid division by zero
        
        sentiment_distribution = {
            'positive': sentiment_counts.get('positive', 0) / total_mentions,
            'neutral': sentiment_counts.get('neutral', 0) / total_mentions,
            'negative': sentiment_counts.get('negative', 0) / total_mentions
        }
        
        # Extract features and benefits
        features_benefits = self._extract_product_features(product_mentions)
        
        # Determine overall product perception
        overall_sentiment = 'neutral'
        if sentiment_distribution['positive'] > sentiment_distribution['negative'] + 0.1:
            overall_sentiment = 'positive'
        elif sentiment_distribution['negative'] > sentiment_distribution['positive'] + 0.1:
            overall_sentiment = 'negative'
        
        return {
            'product': product,
            'mention_count': len(product_mentions),
            'sentiment_distribution': sentiment_distribution,
            'features_benefits': features_benefits,
            'overall_perception': overall_sentiment
        }
    
    def _extract_product_features(self, mentions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Extract key features mentioned about a product.
        
        Args:
            mentions: List of product mentions with text and sentiment
            
        Returns:
            List of product feature dictionaries
        """
        # Feature patterns to look for
        feature_patterns = {
            'design': r'\b(design|look|appearance|style|aesthetic)\b',
            'performance': r'\b(performance|speed|fast|slow|powerful|efficiency)\b',
            'quality': r'\b(quality|build|construction|material|premium)\b',
            'features': r'\b(feature|functionality|capability|option|setting)\b',
            'usability': r'\b(usability|user-friendly|intuitive|easy|simple|difficult)\b',
            'battery': r'\b(battery|charge|life|power|runtime|lasts)\b',
            'display': r'\b(display|screen|resolution|brightness|color)\b',
            'price': r'\b(price|cost|expensive|cheap|affordable|value)\b',
            'size': r'\b(size|compact|large|small|dimensions|weight)\b',
            'software': r'\b(software|app|update|interface|UI)\b',
            'sound': r'\b(sound|audio|speaker|noise|volume|bass)\b',
            'camera': r'\b(camera|photo|picture|image|video|recording)\b',
            'comfort': r'\b(comfort|comfortable|fit|wearable|ergonomic)\b',
            'durability': r'\b(durability|durable|rugged|tough|strong|fragile)\b'
        }
        
        # Count feature mentions by sentiment
        feature_sentiments = {}
        
        for feature, pattern in feature_patterns.items():
            feature_sentiments[feature] = {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total': 0
            }
        
        # Process each mention
        for mention in mentions:
            text = mention['text'].lower()
            sentiment = mention['sentiment']
            
            for feature, pattern in feature_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    feature_sentiments[feature][sentiment] += 1
                    feature_sentiments[feature]['total'] += 1
        
        # Create feature list with sentiment
        features = []
        for feature, sentiments in feature_sentiments.items():
            if sentiments['total'] > 0:
                # Calculate dominant sentiment
                max_sentiment = max(
                    ['positive', 'neutral', 'negative'],
                    key=lambda s: sentiments[s]
                )
                
                features.append({
                    'feature': feature,
                    'mentions': sentiments['total'],
                    'dominant_sentiment': max_sentiment,
                    'sentiment_distribution': {
                        'positive': sentiments['positive'] / sentiments['total'],
                        'neutral': sentiments['neutral'] / sentiments['total'],
                        'negative': sentiments['negative'] / sentiments['total']
                    }
                })
        
        # Sort by mention count
        return sorted(features, key=lambda f: f['mentions'], reverse=True)
    
    def _generate_ad_copy_suggestions(
        self,
        product: str,
        brand: str,
        trending_keywords: List[Dict[str, Any]],
        key_elements: Dict[str, Any],
        brand_perception: Dict[str, Any],
        product_perception: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate ad copy suggestions based on collected data.
        
        Args:
            product: Product name
            brand: Brand name
            trending_keywords: List of trending keywords
            key_elements: Dictionary with key ad elements
            brand_perception: Brand perception analysis
            product_perception: Product perception analysis
            
        Returns:
            Dictionary with ad copy suggestions
        """
        # Extract key insights
        keywords = [kw['keyword'] for kw in trending_keywords[:5]] if trending_keywords else []
        
        # Get positive brand attributes
        brand_attributes = []
        for attr in brand_perception.get('key_attributes', []):
            if attr.get('dominant_sentiment') == 'positive':
                brand_attributes.append(attr.get('attribute'))
        
        # Get positive product features
        product_features = []
        for feature in product_perception.get('features_benefits', []):
            if feature.get('dominant_sentiment') == 'positive':
                product_features.append(feature.get('feature'))
        
        # Generate headline suggestions
        headlines = []
        
        # Feature-focused headlines
        if product_features:
            for feature in product_features[:2]:
                headlines.append(f"Experience {feature.title()} Like Never Before")
                headlines.append(f"Introducing {brand} {product}: Redefining {feature.title()}")
        
        # Brand-focused headlines
        if brand_attributes:
            for attr in brand_attributes[:2]:
                headlines.append(f"{brand} {product}: {attr.title()} Redefined")
                headlines.append(f"The {attr.title()} of {brand} {product}")
        
        # Keyword-based headlines
        if keywords:
            for keyword in keywords[:2]:
                headlines.append(f"{keyword.title()} Meets {brand} {product}")
                headlines.append(f"{brand} {product}: {keyword.title()} Revolution")
        
        # Add generic headlines if needed
        if len(headlines) < 5:
            headlines.extend([
                f"Introducing the New {brand} {product}",
                f"Discover What Makes {brand} {product} Different",
                f"The {brand} Advantage: {product} Reimagined",
                f"Experience the {brand} {product} Difference",
                f"Meet Your New Favorite {product}"
            ])
        
        # Generate subheadline suggestions
        subheadlines = []
        
        # Feature-based subheadlines
        for i, feature in enumerate(product_features[:3]):
            if i < len(keywords) and keywords[i]:
                subheadlines.append(f"Discover {feature.title()} with {keywords[i].title()} Technology")
            else:
                subheadlines.append(f"Redefining {feature.title()} for Everyone")
        
        # Attribute-based subheadlines
        for i, attr in enumerate(brand_attributes[:3]):
            if i < len(keywords) and keywords[i]:
                subheadlines.append(f"{attr.title()} Meets {keywords[i].title()} in One Package")
            else:
                subheadlines.append(f"Experience the {attr.title()} You Deserve")
        
        # Add generic subheadlines if needed
        if len(subheadlines) < 5:
            subheadlines.extend([
                f"Discover Why Everyone's Talking About the {brand} {product}",
                f"Innovation and Quality Combined in One Premium Package",
                f"Designed for Performance, Engineered for Excellence",
                f"The Smarter Choice for Discerning Customers",
                f"Redefining the Standards in {product.title()} Technology"
            ])
        
        # Generate call-to-action suggestions
        ctas = [
            "Shop Now",
            "Learn More",
            "Discover Today",
            f"Experience {brand}",
            "See the Difference",
            "Join the Revolution",
            "Upgrade Today",
            f"Find Your {product}",
            "Explore Features",
            "Start Your Journey"
        ]
        
        return {
            'headlines': headlines[:5],  # Return top 5
            'subheadlines': subheadlines[:5],  # Return top 5
            'call_to_action': ctas
        }
    
    def _save_ad_insights(self, insights: Dict[str, Any], product: str, brand: str) -> None:
        """
        Save advertising insights to file.
        
        Args:
            insights: Insights dictionary
            product: Product name
            brand: Brand name
        """
        try:
            # Create sanitized filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sanitized_product = re.sub(r'[^\w\s]', '', product).strip().replace(' ', '_').lower()
            sanitized_brand = re.sub(r'[^\w\s]', '', brand).strip().replace(' ', '_').lower()
            
            filename = f"ad_insights_{sanitized_brand}_{sanitized_product}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, 'processed', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)
            
            self.logger.info(f"Saved ad insights to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving ad insights: {str(e)}")
    
    def generate_training_data(self, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate training data for LLM from collected insights.
        
        Args:
            output_file: Path to save training data (optional)
            
        Returns:
            List of training examples
        """
        if not self.scraped_posts and not self.scraped_comments:
            self.logger.warning("No scraped data to generate training examples")
            return []
        
        # Process posts and comments into training format
        training_examples = []
        
        # Process high engagement posts first
        high_engagement_posts = sorted(
            [post for post in self.scraped_posts if 'engagement_score' in post],
            key=lambda p: p.get('engagement_score', 0),
            reverse=True
        )[:50]  # Top 50 posts
        
        # Create examples from high engagement posts
        for post in high_engagement_posts:
            query = post.get('query', 'unknown')
            subreddit = post.get('subreddit', 'unknown')
            
            # Create training example
            example = {
                "input": f"Create an ad for {query} that would appeal to the r/{subreddit} audience",
                "output": {
                    "headline": post.get('title', ''),
                    "description": post.get('selftext', ''),
                    "format": "social media post",
                    "platform": "reddit",
                    "target_audience": f"r/{subreddit} subscribers",
                    "features_to_highlight": post.get('keywords', []),
                    "engagement_metrics": {
                        "score": post.get('score', 0),
                        "comments": post.get('num_comments', 0),
                        "upvote_ratio": post.get('upvote_ratio', 0.0)
                    }
                }
            }
            
            training_examples.append(example)
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(training_examples, f, indent=2)
                
                self.logger.info(f"Saved {len(training_examples)} training examples to {output_file}")
            except Exception as e:
                self.logger.error(f"Error saving training data: {str(e)}")
        
        return training_examples

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create Reddit scraper
    scraper = RedditScraper()
    
    # Example: Find relevant subreddits for iPhone
    subreddits = scraper.find_relevant_subreddits(['iphone', 'apple', 'smartphone'])
    print(f"Relevant subreddits: {subreddits}")
    
    # Example: Search for posts about iPhone
    posts = scraper.search_posts('iPhone 15', subreddits=subreddits, limit=20)
    print(f"Found {len(posts)} posts about iPhone 15")
    
    # Example: Generate ad insights
    insights = scraper.extract_ad_insights('iPhone 15', 'Apple', 'Technology')
    print("Ad Insights:")
    print(f"Recommended format: {insights['recommended_format']}")
    print(f"Key elements: {insights['key_elements']}")
    print(f"Visual focus: {insights['visual_focus']}")