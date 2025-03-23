"""
Ad insights extraction module for generating advertising recommendations
"""
import os
import re
import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from collections import Counter, defaultdict

class InsightExtractor:
    """
    Extract actionable advertising insights from processed data.
    
    Features:
    - Analyzes ad creative elements across platforms
    - Identifies high-performance patterns in ad campaigns
    - Generates ad format and creative recommendations
    - Extracts audience targeting insights
    - Compiles brand and product perception data
    """
    
    def __init__(
        self,
        input_dir: str = 'data/processed',
        output_dir: str = 'data/insights',
        log_level: int = logging.INFO
    ):
        """
        Initialize insight extractor.
        
        Args:
            input_dir: Directory containing processed data
            output_dir: Directory to save insights
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger('InsightExtractor')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Create handlers
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                os.path.join(output_dir, 'insight_extractor.log'),
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
    
    def extract_all_insights(self) -> List[Dict[str, Any]]:
        """
        Extract insights from all available data.
        
        Returns:
            List of insight dictionaries
        """
        all_insights = []
        
        try:
            # Get all JSON files with keyword or brand data
            keyword_files = [f for f in os.listdir(self.input_dir) 
                          if os.path.isfile(os.path.join(self.input_dir, f)) 
                          and f.startswith('keyword_') and f.endswith('.json')]
            
            brand_files = [f for f in os.listdir(self.input_dir) 
                          if os.path.isfile(os.path.join(self.input_dir, f)) 
                          and f.startswith('brand_') and f.endswith('.json')]
            
            # Process each keyword file
            for file in keyword_files:
                try:
                    self.logger.info(f"Extracting insights from keyword file: {file}")
                    filepath = os.path.join(self.input_dir, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    keyword = data.get('metadata', {}).get('keyword', 'unknown')
                    items = data.get('items', [])
                    
                    if not items:
                        continue
                    
                    # Extract insights for this keyword
                    insights = self._extract_keyword_insights(keyword, items)
                    
                    if insights:
                        all_insights.append(insights)
                        
                        # Save individual insights file
                        clean_keyword = re.sub(r'[^\w\s]', '', keyword).strip().replace(' ', '_').lower()
                        output_path = os.path.join(
                            self.output_dir, 
                            f"{clean_keyword}_insights_{datetime.now().strftime('%Y%m%d')}.json"
                        )
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(insights, f, indent=2)
                        
                        self.logger.info(f"Saved insights for keyword '{keyword}' to {output_path}")
                
                except Exception as e:
                    self.logger.error(f"Error processing file {file}: {str(e)}")
            
            # Process each brand file
            for file in brand_files:
                try:
                    self.logger.info(f"Extracting insights from brand file: {file}")
                    filepath = os.path.join(self.input_dir, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    brand = data.get('metadata', {}).get('brand', 'unknown')
                    items = data.get('items', [])
                    
                    if not items:
                        continue
                    
                    # Extract insights for this brand
                    insights = self._extract_brand_insights(brand, items)
                    
                    if insights:
                        all_insights.append(insights)
                        
                        # Save individual insights file
                        clean_brand = re.sub(r'[^\w\s]', '', brand).strip().replace(' ', '_').lower()
                        output_path = os.path.join(
                            self.output_dir, 
                            f"{clean_brand}_insights_{datetime.now().strftime('%Y%m%d')}.json"
                        )
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(insights, f, indent=2)
                        
                        self.logger.info(f"Saved insights for brand '{brand}' to {output_path}")
                
                except Exception as e:
                    self.logger.error(f"Error processing file {file}: {str(e)}")
            
            # Save all insights to a single file
            if all_insights:
                all_insights_path = os.path.join(
                    self.output_dir, 
                    f"all_insights_{datetime.now().strftime('%Y%m%d')}.json"
                )
                
                with open(all_insights_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": {
                            "processing_time": datetime.now().isoformat(),
                            "insights_count": len(all_insights)
                        },
                        "insights": all_insights
                    }, f, indent=2)
                
                self.logger.info(f"Saved {len(all_insights)} total insights to {all_insights_path}")
            
            return all_insights
            
        except Exception as e:
            self.logger.error(f"Error extracting all insights: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def extract_combined_insights(
        self,
        product: str,
        brand: str,
        industry: str = "general",
        product_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract combined insights for a specific product and brand.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            product_type: Product type
            
        Returns:
            Combined insights dictionary
        """
        try:
            # Search for relevant files
            all_files = os.listdir(self.input_dir)
            
            # Look for exact matches for brand and product
            brand_pattern = re.compile(f"brand_{re.escape(brand.lower().replace(' ', '_'))}.*\\.json")
            product_pattern = re.compile(f"keyword_{re.escape(product.lower().replace(' ', '_'))}.*\\.json")
            
            brand_files = [f for f in all_files if brand_pattern.match(f.lower())]
            product_files = [f for f in all_files if product_pattern.match(f.lower())]
            
            # If no exact matches, look for partial matches
            if not brand_files:
                brand_files = [f for f in all_files 
                               if f.startswith('brand_') and brand.lower() in f.lower()]
            
            if not product_files:
                product_files = [f for f in all_files 
                                if f.startswith('keyword_') and product.lower() in f.lower()]
            
            # Collect all items
            all_items = []
            
            # Process brand files
            for file in brand_files:
                filepath = os.path.join(self.input_dir, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_items.extend(data.get('items', []))
            
            # Process product files
            for file in product_files:
                filepath = os.path.join(self.input_dir, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_items.extend(data.get('items', []))
            
            # If no specific files found, search in merged files
            if not all_items:
                merged_files = [f for f in all_files 
                              if f.startswith('merged_') and f.endswith('.json')]
                
                for file in merged_files:
                    filepath = os.path.join(self.input_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Look for items matching brand or product
                        if 'ads' in data:
                            for ad in data['ads']:
                                if (brand.lower() in ad.get('advertiser_name', '').lower() or
                                    product.lower() in ad.get('text', '').lower() or
                                    product.lower() in ad.get('headline', '').lower()):
                                    all_items.append(ad)
                        
                        elif 'posts' in data:
                            for post in data['posts']:
                                if (brand.lower() in post.get('text', '').lower() or
                                    product.lower() in post.get('text', '').lower() or
                                    brand.lower() in post.get('title', '').lower() or
                                    product.lower() in post.get('title', '').lower()):
                                    all_items.append(post)
            
            # If we still have no items, return a minimal insights object
            if not all_items:
                self.logger.warning(f"No data found for product '{product}' and brand '{brand}'")
                return self._generate_minimal_insights(product, brand, industry, product_type)
            
            # Generate comprehensive insights
            insights = self._generate_comprehensive_insights(
                product, brand, industry, product_type, all_items
            )
            
            # Save insights to file
            clean_name = f"{brand}_{product}".lower().replace(' ', '_')
            clean_name = re.sub(r'[^\w]', '', clean_name)
            
            output_path = os.path.join(
                self.output_dir, 
                f"{clean_name}_insights_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)
            
            self.logger.info(f"Saved combined insights for {brand} {product} to {output_path}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting combined insights: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return self._generate_minimal_insights(product, brand, industry, product_type)
    
    def _extract_keyword_insights(self, keyword: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract insights for a specific keyword.
        
        Args:
            keyword: Keyword/product name
            items: List of items related to the keyword
            
        Returns:
            Insights dictionary
        """
        insights = {
            "type": "keyword_insights",
            "keyword": keyword,
            "item_count": len(items),
            "sources": self._get_unique_sources(items),
            "platforms": self._get_unique_platforms(items),
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract content insights
        content_insights = self._extract_content_insights(items)
        insights["content_insights"] = content_insights
        
        # Extract format insights
        format_insights = self._extract_format_insights(items)
        insights["format_insights"] = format_insights
        
        # Extract engagement insights
        engagement_insights = self._extract_engagement_insights(items)
        insights["engagement_insights"] = engagement_insights
        
        # Extract sentiment analysis
        sentiment_analysis = self._extract_sentiment_analysis(items)
        insights["sentiment_analysis"] = sentiment_analysis
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            keyword=keyword, 
            items=items,
            content_insights=content_insights,
            format_insights=format_insights,
            engagement_insights=engagement_insights,
            sentiment_analysis=sentiment_analysis
        )
        insights["recommendations"] = recommendations
        
        return insights
    
    def _extract_brand_insights(self, brand: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract insights for a specific brand.
        
        Args:
            brand: Brand name
            items: List of items related to the brand
            
        Returns:
            Insights dictionary
        """
        insights = {
            "type": "brand_insights",
            "brand": brand,
            "item_count": len(items),
            "sources": self._get_unique_sources(items),
            "platforms": self._get_unique_platforms(items),
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract brand perception
        insights["brand_perception"] = self._extract_brand_perception(brand, items)
        
        # Extract content insights
        content_insights = self._extract_content_insights(items)
        insights["content_insights"] = content_insights
        
        # Extract format insights
        format_insights = self._extract_format_insights(items)
        insights["format_insights"] = format_insights
        
        # Extract engagement insights
        engagement_insights = self._extract_engagement_insights(items)
        insights["engagement_insights"] = engagement_insights
        
        # Extract sentiment analysis
        sentiment_analysis = self._extract_sentiment_analysis(items)
        insights["sentiment_analysis"] = sentiment_analysis
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            brand=brand, 
            items=items,
            content_insights=content_insights,
            format_insights=format_insights,
            engagement_insights=engagement_insights,
            sentiment_analysis=sentiment_analysis
        )
        insights["recommendations"] = recommendations
        
        return insights
    
    def _get_unique_sources(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        Get unique data sources from items.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List of unique sources
        """
        sources = set()
        for item in items:
            source = item.get('source', '')
            if source:
                sources.add(source)
        return list(sources)
    
    def _get_unique_platforms(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        Get unique platforms from items.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List of unique platforms
        """
        platforms = set()
        for item in items:
            platform = item.get('platform', '')
            if platform:
                platforms.add(platform)
        return list(platforms)
    
    def _extract_content_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract insights about ad content and copy.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Content insights dictionary
        """
        # Collect all text content
        all_text = ""
        headlines = []
        cta_buttons = []
        
        for item in items:
            if 'text' in item and item['text']:
                all_text += " " + item['text']
            
            if 'headline' in item and item['headline']:
                headlines.append(item['headline'])
            elif 'title' in item and item['title']:
                headlines.append(item['title'])
            
            if 'cta' in item and item['cta']:
                cta_buttons.append(item['cta'])
        
        # Word count analysis
        words = all_text.split()
        avg_word_count = len(words) / len(items) if items and all_text else 0
        
        # Extract most common phrases (2-3 words)
        phrases = []
        words = all_text.lower().split()
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        
        # Extract 3-word phrases
        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Count phrase frequencies
        phrase_counter = Counter(phrases)
        top_phrases = phrase_counter.most_common(8)
        
        # Analyze CTA buttons
        cta_counter = Counter(cta_buttons)
        top_ctas = cta_counter.most_common(5)
        
        # Analyze headline patterns
        headline_patterns = {
            "question": 0,
            "number": 0,
            "how_to": 0,
            "benefit": 0,
            "offer": 0
        }
        
        for headline in headlines:
            headline_lower = headline.lower()
            
            if "?" in headline:
                headline_patterns["question"] += 1
            
            if re.search(r'\d+', headline):
                headline_patterns["number"] += 1
            
            if "how to" in headline_lower or "how-to" in headline_lower:
                headline_patterns["how_to"] += 1
            
            benefit_keywords = ["improve", "better", "best", "free", "save", "boost", "increase"]
            if any(keyword in headline_lower for keyword in benefit_keywords):
                headline_patterns["benefit"] += 1
            
            offer_keywords = ["discount", "sale", "off", "limited", "exclusive", "today", "now"]
            if any(keyword in headline_lower for keyword in offer_keywords):
                headline_patterns["offer"] += 1
        
        # Calculate headline pattern percentages
        headline_pattern_percentages = {}
        total_headlines = len(headlines) if headlines else 1
        
        for pattern, count in headline_patterns.items():
            headline_pattern_percentages[pattern] = (count / total_headlines) * 100
        
        # Extract keywords
        keywords = self._extract_keywords(all_text)
        
        return {
            "avg_word_count": avg_word_count,
            "top_phrases": [{"phrase": phrase, "count": count} for phrase, count in top_phrases],
            "top_ctas": [{"cta": cta, "count": count} for cta, count in top_ctas],
            "headline_patterns": headline_patterns,
            "headline_pattern_percentages": headline_pattern_percentages,
            "keywords": keywords
        }
    
    def _extract_format_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract insights about ad formats.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Format insights dictionary
        """
        formats = {
            "image": 0,
            "video": 0,
            "carousel": 0,
            "text_only": 0
        }
        
        landing_pages = []
        
        for item in items:
            # Determine format
            if 'media_type' in item:
                media_type = item['media_type'].lower()
                if media_type == 'carousel':
                    formats['carousel'] += 1
                elif media_type == 'video':
                    formats['video'] += 1
                elif media_type == 'image':
                    formats['image'] += 1
                elif media_type == 'text':
                    formats['text_only'] += 1
            elif 'media_urls' in item and item['media_urls']:
                if len(item['media_urls']) > 1:
                    formats['carousel'] += 1
                else:
                    # Try to determine if it's a video or image
                    url = item['media_urls'][0]
                    if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', 'video']):
                        formats['video'] += 1
                    else:
                        formats['image'] += 1
            elif 'image_urls' in item and item['image_urls']:
                if len(item['image_urls']) > 1:
                    formats['carousel'] += 1
                else:
                    formats['image'] += 1
            elif 'video_urls' in item and item['video_urls']:
                formats['video'] += 1
            else:
                formats['text_only'] += 1
            
            # Collect landing pages
            if 'landing_page' in item and item['landing_page']:
                landing_pages.append(item['landing_page'])
        
        # Calculate percentages
        total = sum(formats.values())
        format_percentages = {
            format_type: (count / total) * 100 if total > 0 else 0
            for format_type, count in formats.items()
        }
        
        # Get dominant format
        dominant_format = max(formats.items(), key=lambda x: x[1])[0] if total > 0 else "unknown"
        
        # Analyze landing pages
        landing_page_counter = Counter(landing_pages)
        top_landing_pages = landing_page_counter.most_common(5)
        
        return {
            "format_counts": formats,
            "format_percentages": format_percentages,
            "dominant_format": dominant_format,
            "top_landing_pages": [{"url": url, "count": count} for url, count in top_landing_pages]
        }
    
    def _extract_engagement_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract insights about engagement metrics.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Engagement insights dictionary
        """
        # Extract engagement metrics by format
        format_engagement = defaultdict(list)
        
        for item in items:
            # Skip items without engagement data
            if 'engagement' not in item:
                continue
            
            # Determine format (similar to _extract_format_insights)
            if 'media_type' in item:
                format_type = item['media_type'].lower()
            elif 'media_urls' in item and item['media_urls']:
                if len(item['media_urls']) > 1:
                    format_type = 'carousel'
                else:
                    url = item['media_urls'][0]
                    format_type = 'video' if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', 'video']) else 'image'
            elif 'image_urls' in item and item['image_urls']:
                format_type = 'carousel' if len(item['image_urls']) > 1 else 'image'
            elif 'video_urls' in item and item['video_urls']:
                format_type = 'video'
            else:
                format_type = 'text_only'
            
            # Normalize format type to one of our standard categories
            if format_type not in ['image', 'video', 'carousel', 'text_only']:
                format_type = 'other'
            
            # Calculate engagement score
            engagement = item['engagement']
            
            # Handle different engagement metric formats
            if isinstance(engagement, dict):
                # Calculate a simple engagement score
                score = 0
                
                # Facebook/Instagram style metrics
                if 'likes' in engagement:
                    score += engagement['likes'] * 1
                if 'comments' in engagement:
                    score += engagement['comments'] * 3
                if 'shares' in engagement:
                    score += engagement['shares'] * 5
                if 'reactions' in engagement:
                    score += engagement['reactions'] * 1
                
                # Reddit style metrics
                if 'score' in engagement:
                    score += engagement['score'] * 1
                if 'upvote_ratio' in engagement:
                    score *= engagement['upvote_ratio']
                if 'comments' in engagement:
                    score += engagement['comments'] * 3
            else:
                # Handle simple numeric engagement scores
                try:
                    score = float(engagement)
                except (ValueError, TypeError):
                    score = 0
            
            # Add to format engagement data
            format_engagement[format_type].append(score)
        
        # Calculate average engagement by format
        avg_engagement_by_format = {}
        for format_type, scores in format_engagement.items():
            if scores:
                avg_engagement_by_format[format_type] = sum(scores) / len(scores)
            else:
                avg_engagement_by_format[format_type] = 0
        
        # Determine top performing format
        if avg_engagement_by_format:
            top_format = max(avg_engagement_by_format.items(), key=lambda x: x[1])[0]
        else:
            top_format = "unknown"
        
        # Compare format performance (relative to average)
        avg_overall = sum(sum(scores) for scores in format_engagement.values()) / max(sum(len(scores) for scores in format_engagement.values()), 1)
        relative_performance = {}
        
        for format_type, avg in avg_engagement_by_format.items():
            if avg_overall > 0:
                relative_performance[format_type] = (avg / avg_overall) * 100
            else:
                relative_performance[format_type] = 0
        
        return {
            "avg_engagement_by_format": avg_engagement_by_format,
            "relative_performance": relative_performance,
            "top_performing_format": top_format
        }
    
    def _extract_sentiment_analysis(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract sentiment analysis from items.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Sentiment analysis dictionary
        """
        # Count sentiment labels
        sentiment_labels = []
        sentiment_scores = []
        
        for item in items:
            # Check for direct sentiment label
            if 'sentiment_label' in item:
                sentiment_labels.append(item['sentiment_label'])
            
            # Check for sentiment object
            elif 'sentiment' in item and isinstance(item['sentiment'], dict):
                sentiment = item['sentiment']
                
                # Add compound score
                if 'compound' in sentiment:
                    sentiment_scores.append(sentiment['compound'])
                
                # Determine label from compound score
                if 'compound' in sentiment:
                    if sentiment['compound'] >= 0.05:
                        sentiment_labels.append('positive')
                    elif sentiment['compound'] <= -0.05:
                        sentiment_labels.append('negative')
                    else:
                        sentiment_labels.append('neutral')
                
                # If no compound but has positive/negative values
                elif 'positive' in sentiment and 'negative' in sentiment:
                    if sentiment['positive'] > sentiment['negative']:
                        sentiment_labels.append('positive')
                    elif sentiment['negative'] > sentiment['positive']:
                        sentiment_labels.append('negative')
                    else:
                        sentiment_labels.append('neutral')
        
        # Calculate sentiment distribution
        sentiment_counter = Counter(sentiment_labels)
        total_sentiments = len(sentiment_labels) if sentiment_labels else 1
        
        sentiment_distribution = {
            'positive': (sentiment_counter.get('positive', 0) / total_sentiments) * 100,
            'neutral': (sentiment_counter.get('neutral', 0) / total_sentiments) * 100,
            'negative': (sentiment_counter.get('negative', 0) / total_sentiments) * 100
        }
        
        # Calculate average sentiment score
        avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Determine overall sentiment
        overall_sentiment = max(sentiment_distribution.items(), key=lambda x: x[1])[0]
        
        return {
            "sentiment_distribution": sentiment_distribution,
            "overall_sentiment": overall_sentiment,
            "avg_sentiment_score": avg_sentiment_score,
            "sentiment_counts": dict(sentiment_counter)
        }
    
    def _extract_brand_perception(self, brand: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract brand perception insights.
        
        Args:
            brand: Brand name
            items: List of item dictionaries
            
        Returns:
            Brand perception dictionary
        """
        # Extract sentiment associated with brand mentions
        sentiment_labels = []
        
        # Collect all text content that mentions the brand
        brand_mentions = []
        
        for item in items:
            # Check if this item mentions the brand
            mentions_brand = False
            
            if 'advertiser_name' in item and brand.lower() in item['advertiser_name'].lower():
                mentions_brand = True
            
            if 'text' in item and item['text'] and brand.lower() in item['text'].lower():
                mentions_brand = True
                brand_mentions.append(item['text'])
            
            if 'headline' in item and item['headline'] and brand.lower() in item['headline'].lower():
                mentions_brand = True
                brand_mentions.append(item['headline'])
            
            if 'title' in item and item['title'] and brand.lower() in item['title'].lower():
                mentions_brand = True
                brand_mentions.append(item['title'])
            
            # If this item mentions the brand, add its sentiment
            if mentions_brand:
                if 'sentiment_label' in item:
                    sentiment_labels.append(item['sentiment_label'])
                elif 'sentiment' in item and isinstance(item['sentiment'], dict):
                    sentiment = item['sentiment']
                    
                    # Determine label from compound score
                    if 'compound' in sentiment:
                        if sentiment['compound'] >= 0.05:
                            sentiment_labels.append('positive')
                        elif sentiment['compound'] <= -0.05:
                            sentiment_labels.append('negative')
                        else:
                            sentiment_labels.append('neutral')
                    
                    # If no compound but has positive/negative values
                    elif 'positive' in sentiment and 'negative' in sentiment:
                        if sentiment['positive'] > sentiment['negative']:
                            sentiment_labels.append('positive')
                        elif sentiment['negative'] > sentiment['positive']:
                            sentiment_labels.append('negative')
                        else:
                            sentiment_labels.append('neutral')
        
        # Calculate sentiment distribution
        sentiment_counter = Counter(sentiment_labels)
        total_sentiments = len(sentiment_labels) if sentiment_labels else 1
        
        sentiment_distribution = {
            'positive': (sentiment_counter.get('positive', 0) / total_sentiments) * 100,
            'neutral': (sentiment_counter.get('neutral', 0) / total_sentiments) * 100,
            'negative': (sentiment_counter.get('negative', 0) / total_sentiments) * 100
        }
        
        # Determine overall sentiment
        overall_sentiment = max(sentiment_distribution.items(), key=lambda x: x[1])[0]
        
        # Extract brand attributes
        brand_attributes = self._extract_brand_attributes(brand_mentions)
        
        return {
            "brand": brand,
            "mention_count": len(brand_mentions),
            "sentiment_distribution": sentiment_distribution,
            "overall_sentiment": overall_sentiment,
            "attributes": brand_attributes
        }
    
    def _extract_brand_attributes(self, brand_mentions: List[str]) -> List[Dict[str, Any]]:
        """
        Extract key attributes mentioned about a brand.
        
        Args:
            brand_mentions: List of text mentioning the brand
            
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
        
        # Count attribute mentions
        attribute_counts = defaultdict(int)
        
        for text in brand_mentions:
            if not text:
                continue
                
            text_lower = text.lower()
            
            for attribute, pattern in attribute_patterns.items():
                if re.search(pattern, text_lower, re.IGNORECASE):
                    attribute_counts[attribute] += 1
        
        # Create attribute list
        attributes = []
        for attribute, count in attribute_counts.items():
            if count > 0:
                attributes.append({
                    'attribute': attribute,
                    'mentions': count
                })
        
        # Sort by mention count
        return sorted(attributes, key=lambda a: a['mentions'], reverse=True)
    
    def _extract_keywords(self, text: str, max_keywords: int = 15) -> List[Dict[str, Any]]:
        """
        Extract most significant keywords from text.
        
        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keyword dictionaries
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
        keywords = [
            {"keyword": word, "count": count} 
            for word, count in word_counts.most_common(max_keywords)
        ]
        
        return keywords
    
    def _generate_recommendations(
        self,
        items: List[Dict[str, Any]],
        content_insights: Dict[str, Any],
        format_insights: Dict[str, Any],
        engagement_insights: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        keyword: Optional[str] = None,
        brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ad recommendations based on insights.
        
        Args:
            items: List of item dictionaries
            content_insights: Content insights dictionary
            format_insights: Format insights dictionary
            engagement_insights: Engagement insights dictionary
            sentiment_analysis: Sentiment analysis dictionary
            keyword: Keyword/product (optional)
            brand: Brand name (optional)
            
        Returns:
            Recommendations dictionary
        """
        # Determine target (keyword or brand)
        target = keyword or brand or "product"
        
        # Recommended format based on engagement
        recommended_format = engagement_insights.get('top_performing_format', 'image')
        
        # Recommended content elements
        content_elements = []
        
        # Extract recommended phrases
        top_phrases = [item['phrase'] for item in content_insights.get('top_phrases', [])]
        if top_phrases:
            content_elements.append(f"Include phrases like: '{', '.join(top_phrases[:3])}'")
        
        # Recommended headline pattern
        headline_patterns = content_insights.get('headline_pattern_percentages', {})
        if headline_patterns:
            top_pattern = max(headline_patterns.items(), key=lambda x: x[1])[0]
            
            if top_pattern == 'question':
                content_elements.append("Use question format in headlines")
            elif top_pattern == 'number':
                content_elements.append("Include numbers in headlines")
            elif top_pattern == 'how_to':
                content_elements.append("Use 'How to' format in headlines")
            elif top_pattern == 'benefit':
                content_elements.append("Emphasize benefits in headlines")
            elif top_pattern == 'offer':
                content_elements.append("Highlight special offers in headlines")
        
        # Recommended CTA
        top_ctas = [item['cta'] for item in content_insights.get('top_ctas', [])]
        recommended_cta = top_ctas[0] if top_ctas else "Learn More"
        
        # Recommended word count
        avg_word_count = content_insights.get('avg_word_count', 0)
        recommended_word_count = int(avg_word_count) if avg_word_count > 0 else 50
        
        # Recommended tone based on sentiment
        overall_sentiment = sentiment_analysis.get('overall_sentiment', 'neutral')
        if overall_sentiment == 'positive':
            tone = "positive and upbeat"
        elif overall_sentiment == 'negative':
            tone = "solution-oriented and reassuring"
        else:
            tone = "informative and balanced"
        
        # Generate headline suggestions
        headline_suggestions = self._generate_headline_suggestions(
            target=target,
            content_insights=content_insights,
            top_pattern=top_pattern if headline_patterns else 'benefit'
        )
        
        # Generate copy suggestions
        copy_suggestions = self._generate_copy_suggestions(
            target=target,
            content_insights=content_insights,
            tone=tone,
            recommended_word_count=recommended_word_count
        )
        
        return {
            "recommended_format": recommended_format,
            "content_elements": content_elements,
            "recommended_cta": recommended_cta,
            "recommended_word_count": recommended_word_count,
            "recommended_tone": tone,
            "headline_suggestions": headline_suggestions,
            "copy_suggestions": copy_suggestions
        }
    
    def _generate_headline_suggestions(
        self,
        target: str,
        content_insights: Dict[str, Any],
        top_pattern: str
    ) -> List[str]:
        """
        Generate headline suggestions based on insights.
        
        Args:
            target: Target keyword or brand
            content_insights: Content insights dictionary
            top_pattern: Top headline pattern
            
        Returns:
            List of headline suggestions
        """
        suggestions = []
        
        # Get keywords for use in headlines
        keywords = [item['keyword'] for item in content_insights.get('keywords', [])]
        top_keywords = keywords[:5] if keywords else []
        
        # Get phrases for use in headlines
        phrases = [item['phrase'] for item in content_insights.get('top_phrases', [])]
        top_phrases = phrases[:3] if phrases else []
        
        # Generate based on pattern
        if top_pattern == 'question':
            suggestions.append(f"Why is {target} the Best Choice for {random.choice(top_keywords) if top_keywords else 'You'}?")
            suggestions.append(f"Looking for {random.choice(top_keywords) if top_keywords else 'Better Results'}? Try {target}")
            suggestions.append(f"What Makes {target} Different from Everything Else?")
            
        elif top_pattern == 'number':
            suggestions.append(f"{random.randint(3, 7)} Ways {target} Can Transform Your {random.choice(top_keywords) if top_keywords else 'Experience'}")
            suggestions.append(f"Get {random.randint(20, 60)}% More {random.choice(top_keywords) if top_keywords else 'Performance'} with {target}")
            suggestions.append(f"{random.randint(3, 5)} Reasons to Choose {target} Today")
            
        elif top_pattern == 'how_to':
            suggestions.append(f"How to {random.choice(top_phrases) if top_phrases else 'Get Better Results'} with {target}")
            suggestions.append(f"How {target} Helps You {random.choice(top_keywords) if top_keywords else 'Succeed'}")
            suggestions.append(f"How to Transform Your {random.choice(top_keywords) if top_keywords else 'Life'} Using {target}")
            
        elif top_pattern == 'benefit':
            suggestions.append(f"Experience {random.choice(top_keywords).title() if top_keywords else 'Superior'} Results with {target}")
            suggestions.append(f"{target}: {random.choice(top_keywords).title() if top_keywords else 'Better'} Than Ever Before")
            suggestions.append(f"Unlock {random.choice(top_keywords).title() if top_keywords else 'Amazing'} Potential with {target}")
            
        elif top_pattern == 'offer':
            suggestions.append(f"Special Offer: Try {target} Today")
            suggestions.append(f"Limited Time: Get {target} with {random.choice(top_keywords) if top_keywords else 'Extra Benefits'}")
            suggestions.append(f"Exclusive Deal on {target} - Act Now")
            
        else:
            # Default suggestions
            suggestions.append(f"Introducing {target}: The Future of {random.choice(top_keywords) if top_keywords else 'Innovation'}")
            suggestions.append(f"{target}: Designed for {random.choice(top_keywords) if top_keywords else 'Performance'}")
            suggestions.append(f"Choose {target} for {random.choice(top_keywords).title() if top_keywords else 'Superior'} Results")
        
        # Add additional headline options using a mix of patterns
        suggestions.append(f"Discover What Makes {target} Different")
        suggestions.append(f"The {target} Advantage: {random.choice(top_keywords).title() if top_keywords else 'Excellence'} Redefined")
        
        return suggestions
    
    def _generate_copy_suggestions(
        self,
        target: str,
        content_insights: Dict[str, Any],
        tone: str,
        recommended_word_count: int
    ) -> List[str]:
        """
        Generate ad copy suggestions based on insights.
        
        Args:
            target: Target keyword or brand
            content_insights: Content insights dictionary
            tone: Recommended tone
            recommended_word_count: Recommended word count
            
        Returns:
            List of copy suggestions
        """
        suggestions = []
        
        # Get keywords for use in copy
        keywords = [item['keyword'] for item in content_insights.get('keywords', [])]
        top_keywords = keywords[:8] if keywords else []
        
        # Get phrases for use in copy
        phrases = [item['phrase'] for item in content_insights.get('top_phrases', [])]
        top_phrases = phrases[:5] if phrases else []
        
        # Generate based on tone
        if tone == "positive and upbeat":
            suggestion1 = f"Experience the difference with {target}. "
            suggestion1 += f"Our {random.choice(top_keywords) if top_keywords else 'innovative'} approach ensures you'll enjoy "
            suggestion1 += f"{random.choice(top_keywords) if top_keywords else 'superior'} results. "
            suggestion1 += f"Join thousands of satisfied customers who've discovered the {target} advantage."
            
            suggestion2 = f"Elevate your {random.choice(top_keywords) if top_keywords else 'experience'} with {target}. "
            suggestion2 += f"Designed for {random.choice(top_keywords) if top_keywords else 'performance'}, "
            suggestion2 += f"our solution delivers the {random.choice(top_keywords) if top_keywords else 'quality'} you deserve. "
            suggestion2 += f"Make the smart choice today!"
            
        elif tone == "solution-oriented and reassuring":
            suggestion1 = f"Tired of {random.choice(top_keywords) if top_keywords else 'ordinary'} results? "
            suggestion1 += f"{target} offers a proven solution to your {random.choice(top_keywords) if top_keywords else 'challenges'}. "
            suggestion1 += f"Our approach ensures reliable performance and lasting satisfaction. "
            suggestion1 += f"See the difference for yourself."
            
            suggestion2 = f"Don't settle for less when it comes to {random.choice(top_keywords) if top_keywords else 'quality'}. "
            suggestion2 += f"{target} provides the solution you've been looking for. "
            suggestion2 += f"With our {random.choice(top_keywords) if top_keywords else 'trusted'} technology, "
            suggestion2 += f"you'll finally get the results you need."
            
        else:  # informative and balanced
            suggestion1 = f"{target} offers a comprehensive solution for your {random.choice(top_keywords) if top_keywords else 'needs'}. "
            suggestion1 += f"With advanced {random.choice(top_keywords) if top_keywords else 'features'} and intelligent design, "
            suggestion1 += f"our product delivers consistent performance for a variety of applications. "
            suggestion1 += f"Learn more about how we can help you achieve your goals."
            
            suggestion2 = f"Looking for a better approach to {random.choice(top_keywords) if top_keywords else 'your challenges'}? "
            suggestion2 += f"{target} combines {random.choice(top_keywords) if top_keywords else 'innovation'} with reliability. "
            suggestion2 += f"Our solution is designed to meet the demands of {random.choice(top_keywords) if top_keywords else 'modern'} users. "
            suggestion2 += f"Discover the full range of benefits today."
        
        # Add suggestions
        suggestions.append(suggestion1)
        suggestions.append(suggestion2)
        
        # Add a suggestion using top phrases
        if top_phrases:
            phrase_suggestion = f"With {target}, you'll experience {random.choice(top_phrases)}. "
            phrase_suggestion += f"Our commitment to {random.choice(top_keywords) if top_keywords else 'excellence'} means "
            phrase_suggestion += f"you can count on {random.choice(top_phrases) if len(top_phrases) > 1 else 'superior results'}. "
            phrase_suggestion += f"Why wait? Take your {random.choice(top_keywords) if top_keywords else 'experience'} to the next level!"
            suggestions.append(phrase_suggestion)
        
        return suggestions
    
    def _generate_minimal_insights(
        self,
        product: str,
        brand: str,
        industry: str = "general",
        product_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate minimal insights when no data is available.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            product_type: Product type
            
        Returns:
            Minimal insights dictionary
        """
        # Format recommendations based on industry
        format_by_industry = {
            "technology": "video",
            "fashion": "image",
            "beauty": "carousel",
            "food": "image",
            "health": "video",
            "fitness": "video",
            "automotive": "carousel",
            "real estate": "carousel",
            "finance": "image",
            "education": "video",
            "entertainment": "video",
            "travel": "carousel"
        }
        
        # Default to image if industry not recognized
        recommended_format = format_by_industry.get(industry.lower(), "image")
        
        # Generate minimal recommendations
        return {
            "type": "minimal_insights",
            "product": product,
            "brand": brand,
            "industry": industry,
            "product_type": product_type,
            "timestamp": datetime.now().isoformat(),
            "message": "Limited data available for comprehensive insights",
            "recommendations": {
                "recommended_format": recommended_format,
                "content_elements": [
                    "Focus on key product benefits",
                    "Use clear, direct calls-to-action",
                    "Include the brand prominently"
                ],
                "headline_suggestions": [
                    f"Introducing {brand} {product}",
                    f"Discover the {brand} Difference",
                    f"Experience {product} Like Never Before"
                ],
                "copy_suggestions": [
                    f"Experience the innovation of {brand} {product}. Designed with you in mind, our solution delivers the performance and reliability you've been looking for. Join thousands of satisfied customers today.",
                    f"Looking for a better approach? {brand} {product} combines cutting-edge technology with user-friendly design. Our commitment to excellence ensures you'll get the results you need. Discover the difference today."
                ],
                "recommended_cta": "Learn More",
                "recommended_tone": "informative and balanced"
            }
        }
    
    def _generate_comprehensive_insights(
        self,
        product: str,
        brand: str,
        industry: str,
        product_type: str,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights from collected data.
        
        Args:
            product: Product name
            brand: Brand name
            industry: Industry category
            product_type: Product type
            items: List of items related to the product/brand
            
        Returns:
            Comprehensive insights dictionary
        """
        insights = {
            "type": "comprehensive_insights",
            "product": product,
            "brand": brand,
            "industry": industry,
            "product_type": product_type,
            "item_count": len(items),
            "sources": self._get_unique_sources(items),
            "platforms": self._get_unique_platforms(items),
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract brand perception
        brand_perception = self._extract_brand_perception(brand, items)
        insights["brand_perception"] = brand_perception
        
        # Extract content insights
        content_insights = self._extract_content_insights(items)
        insights["content_insights"] = content_insights
        
        # Extract format insights
        format_insights = self._extract_format_insights(items)
        insights["format_insights"] = format_insights
        
        # Extract engagement insights
        engagement_insights = self._extract_engagement_insights(items)
        insights["engagement_insights"] = engagement_insights
        
        # Extract sentiment analysis
        sentiment_analysis = self._extract_sentiment_analysis(items)
        insights["sentiment_analysis"] = sentiment_analysis
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            keyword=product,
            brand=brand,
            items=items,
            content_insights=content_insights,
            format_insights=format_insights,
            engagement_insights=engagement_insights,
            sentiment_analysis=sentiment_analysis
        )
        insights["recommendations"] = recommendations
        
        # Add industry-specific insights
        industry_insights = self._generate_industry_insights(
            industry, product_type, items, recommendations
        )
        insights["industry_insights"] = industry_insights
        
        return insights
    
    def _generate_industry_insights(
        self,
        industry: str,
        product_type: str,
        items: List[Dict[str, Any]],
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate industry-specific insights.
        
        Args:
            industry: Industry category
            product_type: Product type
            items: List of item dictionaries
            recommendations: General recommendations dictionary
            
        Returns:
            Industry-specific insights dictionary
        """
        # Default industry insights
        industry_insights = {
            "industry": industry,
            "product_type": product_type,
            "specific_recommendations": []
        }
        
        # Industry-specific recommendations
        industry_specific = []
        
        # Technology industry
        if industry.lower() == "technology":
            industry_specific.extend([
                "Emphasize product specifications and technical features",
                "Include comparison with competing technologies",
                "Focus on innovation and future-proof aspects"
            ])
            
            # Product type specific
            if "software" in product_type.lower():
                industry_specific.append("Highlight ease of use and integration")
            elif "hardware" in product_type.lower():
                industry_specific.append("Showcase physical design and durability")
                
        # Fashion industry
        elif industry.lower() == "fashion":
            industry_specific.extend([
                "Focus on visual presentation and styling",
                "Emphasize material quality and craftsmanship",
                "Consider seasonal trends in messaging"
            ])
            
            # Product type specific
            if "apparel" in product_type.lower():
                industry_specific.append("Show products being worn in lifestyle contexts")
            elif "accessories" in product_type.lower():
                industry_specific.append("Demonstrate versatility and styling options")
                
        # Beauty industry
        elif industry.lower() == "beauty":
            industry_specific.extend([
                "Consider before/after demonstrations",
                "Highlight ingredients and benefits",
                "Use close-up detailed shots of products"
            ])
            
        # Food industry
        elif industry.lower() == "food":
            industry_specific.extend([
                "Use vibrant, appetizing imagery",
                "Emphasize taste, quality, or health benefits",
                "Show food in authentic consumption settings"
            ])
            
        # Health industry
        elif industry.lower() == "health" or industry.lower() == "fitness":
            industry_specific.extend([
                "Include educational content about benefits",
                "Feature testimonials or expert endorsements",
                "Balance aspirational imagery with authenticity"
            ])
            
        # Automotive industry
        elif industry.lower() == "automotive":
            industry_specific.extend([
                "Showcase vehicle in dynamic environments",
                "Highlight key features and innovations",
                "Include pricing or financing options"
            ])
            
        # Add to insights
        industry_insights["specific_recommendations"] = industry_specific
        
        # Add industry-specific format recommendation
        if recommendations.get("recommended_format") == "image":
            if industry.lower() in ["technology", "health", "fitness", "education"]:
                industry_insights["format_suggestion"] = "Consider video format to better demonstrate product functionality"
        elif recommendations.get("recommended_format") == "video":
            if industry.lower() in ["fashion", "beauty"]:
                industry_insights["format_suggestion"] = "Consider carousel format to show multiple styles or applications"
                
        return industry_insights


if __name__ == "__main__":
    # Example usage
    extractor = InsightExtractor(
        input_dir='data/processed',
        output_dir='data/insights'
    )
    
    # Extract all insights
    insights = extractor.extract_all_insights()
    print(f"Extracted {len(insights)} insight sets")
    
    # Extract combined insights for a specific product and brand
    combined_insights = extractor.extract_combined_insights(
        product="Smartphone",
        brand="TechBrand",
        industry="Technology",
        product_type="Mobile Devices"
    )
    print(f"Generated combined insights for {combined_insights['brand']} {combined_insights['product']}")