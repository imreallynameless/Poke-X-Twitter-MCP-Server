#!/usr/bin/env python3
"""
Twitter Metrics Integration
Fetches Twitter/X API metrics and sends daily reports via Poke
"""

# Python 3.12+ compatibility fix for removed imghdr module
try:
    import imghdr
except ImportError:
    # imghdr was removed in Python 3.13, create a minimal fallback
    import sys
    import types
    
    # Create a fake imghdr module
    fake_imghdr = types.ModuleType('imghdr')
    fake_imghdr.what = lambda f: None
    sys.modules['imghdr'] = fake_imghdr

import os
import tweepy
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import time

class TwitterMetrics:
    """Twitter API client for fetching engagement metrics"""
    
    def __init__(self, bearer_token: str):
        """Initialize Twitter API client"""
        self.bearer_token = bearer_token
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.api_calls_made = 0  # Track API usage
        self.user_id_cache = {}  # Cache user IDs to save API calls
        
    def _log_api_call(self, endpoint: str):
        """Log API call for tracking usage"""
        self.api_calls_made += 1
        print(f"📊 API Call #{self.api_calls_made}: {endpoint}")
        if self.api_calls_made >= 90:  # Warn at 90% of 100 limit
            print(f"⚠️  WARNING: {self.api_calls_made}/100 monthly API calls used!")
        
    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username - CACHES to save API calls!"""
        # Check cache first to save precious API calls
        if username in self.user_id_cache:
            print(f"💾 Using cached user ID for '{username}': {self.user_id_cache[username]}")
            return self.user_id_cache[username]
            
        try:
            self._log_api_call(f"get_user('{username}')")
            user = self.client.get_user(username=username)
            user_id = user.data.id if user.data else None
            
            # Cache the result for future use
            if user_id:
                self.user_id_cache[username] = user_id
                print(f"💾 Cached user ID for '{username}': {user_id}")
                
            return user_id
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    def get_recent_tweets(self, user_id: str, days: int = 1, max_results: int = 5) -> List[Dict]:
        """
        Get recent tweets with public metrics
        ⚠️  FREE TIER WARNING (2025): Check current X API limits!
        Conserving API quota by limiting results
        """
        try:
            # Calculate date range (last N days)
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Get tweets with public metrics - COUNTS TOWARD 100/month limit!
            self._log_api_call(f"get_users_tweets(user_id={user_id}, max={max_results})")
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 5),  # FREE TIER: Minimum allowed by X API is 5
                tweet_fields=['public_metrics', 'created_at'],  # Removed context_annotations to reduce data
                start_time=start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                end_time=end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            )
            
            if not tweets.data:
                return []
            
            tweet_metrics = []
            for tweet in tweets.data:
                metrics = {
                    'id': tweet.id,
                    'text': tweet.text[:100] + '...' if len(tweet.text) > 100 else tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'metrics': {
                        'retweets': tweet.public_metrics['retweet_count'],
                        'likes': tweet.public_metrics['like_count'],
                        'replies': tweet.public_metrics['reply_count'],
                        'quotes': tweet.public_metrics['quote_count']
                    }
                }
                tweet_metrics.append(metrics)
            
            return tweet_metrics
            
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def get_daily_summary(self, username: str) -> Dict[str, Any]:
        """Get daily metrics summary for a user - OPTIMIZED for Free tier (100 calls/month)"""
        
        # WARNING: Free tier only allows 100 API calls per month!
        # We must minimize calls - try to cache user_id if possible
        
        user_id = self.get_user_id(username)
        if not user_id:
            return {"error": f"User '{username}' not found or API limit reached"}
        
        # REDUCED: Only get 5 tweets (minimum allowed) to conserve API quota
        tweets = self.get_recent_tweets(user_id, days=1, max_results=5)
        
        if not tweets:
            return {
                "username": username,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tweet_count": 0,
                "total_engagement": 0,
                "message": "No tweets found in the last 24 hours"
            }
        
        # Calculate totals
        total_retweets = sum(t['metrics']['retweets'] for t in tweets)
        total_likes = sum(t['metrics']['likes'] for t in tweets)
        total_replies = sum(t['metrics']['replies'] for t in tweets)
        total_quotes = sum(t['metrics']['quotes'] for t in tweets)
        total_engagement = total_retweets + total_likes + total_replies + total_quotes
        
        return {
            "username": username,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tweet_count": len(tweets),
            "metrics": {
                "total_retweets": total_retweets,
                "total_likes": total_likes,
                "total_replies": total_replies,
                "total_quotes": total_quotes,
                "total_engagement": total_engagement
            },
            "top_tweet": max(tweets, key=lambda t: sum(t['metrics'].values())) if tweets else None,
            "tweets": tweets
        }

def get_usage_recommendations() -> str:
    """Get usage recommendations for 2025 X API Free Tier"""
    return """
📊 2025 X API FREE TIER USAGE RECOMMENDATIONS:

⚠️  DAILY REPORTS LIMITATIONS:
• 100 API calls per month total
• Each daily report = 2 API calls (user lookup + tweets)
• Maximum 50 reports per month
• TRUE daily (30 reports) = 60 API calls, leaving only 40 for other usage

🎯 RECOMMENDED USAGE PATTERNS:

1️⃣ WEEKLY REPORTS (Sustainable):
   • 4 reports per month = 8 API calls
   • Plenty of buffer for other usage
   • Run every Sunday for weekly summary

2️⃣ BI-WEEKLY REPORTS (Moderate):
   • 2 reports per month = 4 API calls  
   • Very conservative usage
   • Good for occasional monitoring

3️⃣ MONTHLY REPORTS (Ultra-conservative):
   • 1 report per month = 2 API calls
   • Maximum API quota preservation

❌ NOT RECOMMENDED:
   • True daily automation (30+ reports/month)
   • Multiple users without caching
   • Testing without API call tracking

💡 OPTIMIZATION TIPS:
   • User IDs are cached after first lookup
   • Subsequent reports for same user = 1 API call only
   • Use sparingly and strategically
"""

def format_metrics_message(summary: Dict[str, Any]) -> str:
    """Format metrics summary into a readable message"""
    if "error" in summary:
        return f"❌ Error: {summary['error']}"
    
    if summary['tweet_count'] == 0:
        return f"📊 Daily Twitter Report - {summary['date']}\n\n📝 No tweets posted in the last 24 hours"
    
    metrics = summary['metrics']
    top_tweet = summary.get('top_tweet', {})
    
    message = f"""📊 Daily Twitter Report - {summary['date']}

👤 @{summary['username']}
📝 Tweets: {summary['tweet_count']}

📈 Total Engagement: {metrics['total_engagement']}
❤️ Likes: {metrics['total_likes']}
🔄 Retweets: {metrics['total_retweets']}
💬 Replies: {metrics['total_replies']}
💭 Quotes: {metrics['total_quotes']}"""

    if top_tweet:
        top_engagement = sum(top_tweet['metrics'].values())
        message += f"""

🏆 Top Tweet ({top_engagement} engagements):
"{top_tweet['text']}"
❤️{top_tweet['metrics']['likes']} 🔄{top_tweet['metrics']['retweets']} 💬{top_tweet['metrics']['replies']}"""

    return message

def send_daily_twitter_report(username: str, poke_client) -> Dict[str, Any]:
    """Send daily Twitter metrics report via Poke"""
    try:
        # Get Twitter bearer token
        twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not twitter_token:
            return {"error": "TWITTER_BEARER_TOKEN not configured"}
        
        # Initialize Twitter client
        twitter = TwitterMetrics(twitter_token)
        
        # Get daily summary
        summary = twitter.get_daily_summary(username)
        
        # Format message
        message = format_metrics_message(summary)
        
        # Send via Poke
        response = poke_client.send_message(message)
        
        return {
            "success": True,
            "summary": summary,
            "poke_response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"❌ Daily Twitter Report Failed\n\nError: {str(e)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Try to send error notification
        try:
            poke_client.send_message(error_msg)
        except:
            pass
            
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Quick test
    from python_example import PokeAPI
    
    poke_api_key = os.getenv('POKE_API_KEY')
    twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not poke_api_key:
        print("❌ POKE_API_KEY not set")
        exit(1)
        
    if not twitter_token:
        print("❌ TWITTER_BEARER_TOKEN not set")
        exit(1)
    
    # Test the integration
    poke_client = PokeAPI(poke_api_key)
    username = "your_twitter_username"  # Replace with actual username
    
    print("🧪 Testing Twitter metrics integration...")
    result = send_daily_twitter_report(username, poke_client)
    
    if result['success']:
        print("✅ Daily report sent successfully!")
    else:
        print(f"❌ Error: {result['error']}")
