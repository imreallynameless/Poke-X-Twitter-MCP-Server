#!/usr/bin/env python3
"""
Twitter Tweet Count Integration
Simple API to count tweets in last 24 hours and set posting reminders
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class TwitterCounter:
    """Simple Twitter API client for counting recent tweets"""
    
    def __init__(self, bearer_token: str):
        """Initialize Twitter API client"""
        self.bearer_token = bearer_token
        self.base_url = "https://api.x.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        # 2025 X API Free Tier tracking
        self.api_calls_made = 0
        self.user_id_cache = {}
    
    def _log_api_call(self, endpoint: str):
        """Log API call and warn about Free Tier limits"""
        self.api_calls_made += 1
        print(f"📊 API Call #{self.api_calls_made}: {endpoint}")
        
        if self.api_calls_made >= 90:
            print("⚠️ WARNING: Approaching 100 API call monthly limit!")
        elif self.api_calls_made >= 100:
            print("❌ CRITICAL: Exceeded 100 API call monthly limit!")
    
    def get_user_id(self, username: str) -> str:
        """Get Twitter user ID from username with caching"""
        # Check cache first (saves API calls!)
        if username in self.user_id_cache:
            print(f"💾 Cached user ID for '{username}': {self.user_id_cache[username]}")
            return self.user_id_cache[username]
            
        try:
            self._log_api_call(f"get_user_by_username('{username}')")
            
            url = f"{self.base_url}/users/by/username/{username}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    user_id = str(data['data']['id'])
                    # Cache the result to save future API calls
                    self.user_id_cache[username] = user_id
                    print(f"💾 Cached user ID for '{username}': {user_id}")
                    return user_id
                else:
                    raise Exception(f"User '{username}' not found")
            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            raise Exception(f"Error fetching user ID for '{username}': {e}")
    
    def get_tweet_count_24h(self, username: str) -> Dict[str, Any]:
        """Get count of tweets in last 24 hours using /2/tweets/counts/recent"""
        try:
            user_id = self.get_user_id(username)
            
            # Calculate time range (last 24 hours)
            # X API requires end_time to be at least 10 seconds before current time
            end_time = datetime.now().replace(microsecond=0) - timedelta(seconds=30)  # 30 seconds buffer
            start_time = end_time - timedelta(hours=24)
            
            # X API requires RFC3339 format - VERY strict!
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Build query for specific user
            query = f"from:{username}"
            
            self._log_api_call(f"tweets/counts/recent(user={username})")
            
            url = f"{self.base_url}/tweets/counts/recent"
            params = {
                'query': query,
                'start_time': start_time_str,
                'end_time': end_time_str,
                'granularity': 'day'  # Get daily count
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    # Sum up tweet counts (should be just one day)
                    total_count = sum(point['tweet_count'] for point in data['data'])
                    return {
                        'username': username,
                        'user_id': user_id,
                        'tweet_count_24h': total_count,
                        'period': '24 hours',
                        'timestamp': datetime.now().isoformat(),
                        'api_calls_used': self.api_calls_made
                    }
                else:
                    return {
                        'username': username,
                        'user_id': user_id,
                        'tweet_count_24h': 0,
                        'period': '24 hours',
                        'timestamp': datetime.now().isoformat(),
                        'api_calls_used': self.api_calls_made
                    }
            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            if "429" in str(e):
                raise Exception(f"Rate limit exceeded. Please wait 15 minutes before trying again. Error: {e}")
            else:
                raise Exception(f"Error fetching tweet count: {e}")
    
    def format_tweet_count_report(self, username: str) -> str:
        """Get formatted tweet count report"""
        try:
            count_data = self.get_tweet_count_24h(username)
            
            today = datetime.now().strftime('%Y-%m-%d')
            count = count_data['tweet_count_24h']
            
            if count == 0:
                status_emoji = "😴"
                status_text = "No tweets today"
            elif count == 1:
                status_emoji = "📝"
                status_text = "1 tweet today"
            else:
                status_emoji = "🚀"
                status_text = f"{count} tweets today"
            
            return f"""📊 Tweet Count Report - {today}
👤 @{username}
{status_emoji} {status_text}
📈 API calls used: {count_data['api_calls_used']}/100 monthly"""
            
        except Exception as e:
            return f"❌ Error generating tweet count report: {e}"


class PostingReminder:
    """Handles posting reminders and automation"""
    
    def __init__(self, poke_client=None):
        """Initialize reminder system"""
        self.poke_client = poke_client
        self.reminders = {}  # Store reminder configs
    
    def setup_daily_reminder(self, username: str, reminder_time: str, 
                           min_posts: int = 1, message: str = None) -> Dict[str, Any]:
        """Set up daily posting reminder
        
        Args:
            username: Twitter username to monitor
            reminder_time: Time to check (HH:MM format, e.g., "18:00")
            min_posts: Minimum posts required (default: 1)
            message: Custom reminder message
        """
        try:
            # Validate time format
            datetime.strptime(reminder_time, "%H:%M")
            
            reminder_id = f"daily_{username}_{reminder_time}"
            
            default_message = f"""🚨 Daily Posting Reminder

Hi! You haven't posted on Twitter today yet.

📊 Current status: 0 tweets in last 24 hours
⏰ Time: {reminder_time}
🎯 Goal: At least {min_posts} post(s) per day

Consider sharing:
• A thought or insight
• Something you're working on
• An interesting link or article
• Engagement with your community

Keep that posting streak alive! 🚀"""

            self.reminders[reminder_id] = {
                'username': username,
                'reminder_time': reminder_time,
                'min_posts': min_posts,
                'message': message or default_message,
                'active': True,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'reminder_id': reminder_id,
                'config': self.reminders[reminder_id],
                'message': f"✅ Daily reminder set for @{username} at {reminder_time}"
            }
            
        except ValueError:
            return {
                'success': False,
                'error': 'Invalid time format. Use HH:MM (e.g., "18:00")'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error setting up reminder: {e}"
            }
    
    def check_and_send_reminders(self, twitter_counter: TwitterCounter) -> Dict[str, Any]:
        """Check if reminders should be sent and send them
        
        This would typically be called by a scheduled job
        """
        results = []
        current_time = datetime.now().strftime("%H:%M")
        
        for reminder_id, config in self.reminders.items():
            if not config['active'] or config['reminder_time'] != current_time:
                continue
                
            try:
                # Check tweet count
                count_data = twitter_counter.get_tweet_count_24h(config['username'])
                
                if count_data['tweet_count_24h'] < config['min_posts']:
                    # Send reminder
                    if self.poke_client:
                        response = self.poke_client.send_message(config['message'])
                        results.append({
                            'reminder_id': reminder_id,
                            'username': config['username'],
                            'sent': True,
                            'tweet_count': count_data['tweet_count_24h'],
                            'poke_response': response
                        })
                    else:
                        results.append({
                            'reminder_id': reminder_id,
                            'username': config['username'],
                            'sent': False,
                            'tweet_count': count_data['tweet_count_24h'],
                            'error': 'No Poke client configured'
                        })
                else:
                    results.append({
                        'reminder_id': reminder_id,
                        'username': config['username'],
                        'sent': False,
                        'tweet_count': count_data['tweet_count_24h'],
                        'reason': 'Tweet goal already met'
                    })
                    
            except Exception as e:
                results.append({
                    'reminder_id': reminder_id,
                    'username': config['username'],
                    'sent': False,
                    'error': str(e)
                })
        
        return {
            'check_time': current_time,
            'results': results,
            'total_reminders': len(self.reminders),
            'checked': len([r for r in results if 'error' not in r])
        }
    
    def list_reminders(self) -> Dict[str, Any]:
        """List all configured reminders"""
        return {
            'total_reminders': len(self.reminders),
            'reminders': self.reminders
        }
    
    def disable_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Disable a specific reminder"""
        if reminder_id in self.reminders:
            self.reminders[reminder_id]['active'] = False
            return {
                'success': True,
                'message': f"Reminder {reminder_id} disabled"
            }
        else:
            return {
                'success': False,
                'error': f"Reminder {reminder_id} not found"
            }


def get_usage_info() -> str:
    """Get information about the simplified API usage"""
    return """📊 SIMPLIFIED TWITTER API USAGE (2025 FREE TIER)

✅ OPTIMIZED APPROACH:
• Using /2/tweets/counts/recent endpoint
• Only counts tweets, doesn't fetch full data
• Much more efficient than previous approach
• Perfect for daily monitoring

🎯 API CALLS PER OPERATION:
1️⃣ Tweet Count Check:
   • 1 call for user lookup (cached)
   • 1 call for tweet count
   • Total: 2 calls (1 call after first lookup)

2️⃣ Daily Reminder Check:
   • 1 call for tweet count (user ID cached)
   • Perfect for automation

📈 SUSTAINABILITY:
• 100 API calls per month (Free Tier)
• ~45-50 daily checks possible per month
• Ideal for daily posting reminders
• User ID caching saves significant quota

🔧 TOOLS PROVIDED:
1. get_tweet_count_24h() - Check tweet count
2. setup_daily_reminder() - Set posting reminders
3. check_and_send_reminders() - Automated checks
"""


if __name__ == "__main__":
    # Quick test
    import os
    
    twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not twitter_token:
        print("❌ TWITTER_BEARER_TOKEN not set")
        exit(1)
    
    # Test the tweet counter
    counter = TwitterCounter(twitter_token)
    username = "ujustgotleid"  # Replace with actual username
    
    print("🧪 Testing Tweet Counter...")
    try:
        count_report = counter.format_tweet_count_report(username)
        print(count_report)
    except Exception as e:
        print(f"❌ Error: {e}")