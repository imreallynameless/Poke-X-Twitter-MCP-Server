#!/usr/bin/env python3
"""
Twitter MCP Server with Poke Integration
A Model Context Protocol server for Twitter metrics that can send reports via Poke
Based on the MCP server template: https://github.com/InteractionCo/mcp-server-template
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Add current directory to path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python_example import PokeAPI
from twitter_metrics import TwitterCounter, PostingReminder, get_usage_info
from fastmcp import FastMCP
import logging

# Initialize the MCP server
mcp = FastMCP("Twitter MCP Server with Poke Integration")

# Note: FastMCP handles HTTP transport internally
# The 406 error suggests the client is making GET requests when MCP expects POST

# Global Poke client instance
poke_client: Optional[PokeAPI] = None

def get_poke_client() -> PokeAPI:
    """Get or create a Poke API client instance"""
    global poke_client
    
    if poke_client is None:
        api_key = os.getenv('POKE_API_KEY')
        if not api_key:
            raise ValueError("POKE_API_KEY environment variable is required")
        poke_client = PokeAPI(api_key)
    
    return poke_client

@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Welcome to our Twitter MCP server!"

@mcp.tool(description="Test connectivity and server status - returns server health information")
def test_connection() -> dict:
    """Test MCP server connectivity"""
    return {
        "status": "ok",
        "server": "Twitter MCP Server with Poke Integration",
        "timestamp": datetime.now().isoformat(),
        "health": "healthy",
        "endpoints": {
            "tweet_count": "available",
            "posting_reminders": "available",
            "poke_integration": "available"
        },
        "message": "MCP server is responding correctly"
    }

@mcp.tool(description="Get information about the MCP server including name, version, environment, and available tools")
def get_server_info() -> dict:
    """Get server information"""
    return {
        "server_name": "Twitter MCP Server with Poke Integration",
        "version": "2.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": sys.version.split()[0],
        "available_tools": [
            "greet",
            "test_connection",
            "get_server_info", 
            "get_tweet_count_24h",
            "get_tweet_count_report",
            "setup_posting_reminder",
            "check_posting_reminders"
        ]
    }

@mcp.tool(description="Get count of tweets posted in the last 24 hours for a specific user")
def get_tweet_count_24h(username: str) -> dict:
    """Get tweet count for last 24 hours"""
    try:
        # Clean and validate username
        if not username or not isinstance(username, str):
            return {"error": "Username is required and must be a string"}
        
        clean_username = username.strip().lstrip('@').lower()
        if not clean_username:
            return {"error": "Invalid username provided"}
        
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            return {"error": "TWITTER_BEARER_TOKEN not configured"}
        
        counter = TwitterCounter(bearer_token)
        result = counter.get_tweet_count_24h(clean_username)
        
        # Add debug info for troubleshooting
        result["debug_info"] = {
            "original_username": username,
            "cleaned_username": clean_username,
            "server_timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        return {
            "error": f"Failed to get tweet count: {error_msg}",
            "debug_info": {
                "original_username": username if 'username' in locals() else "N/A",
                "cleaned_username": clean_username if 'clean_username' in locals() else "N/A",
                "error_type": type(e).__name__,
                "server_timestamp": datetime.now().isoformat()
            }
        }

@mcp.tool(description="Get formatted tweet count report for the last 24 hours")
def get_tweet_count_report(username: str) -> str:
    """Get formatted tweet count report"""
    try:
        # Clean and validate username
        if not username or not isinstance(username, str):
            return "❌ Error: Username is required and must be a string"
        
        clean_username = username.strip().lstrip('@').lower()
        if not clean_username:
            return "❌ Error: Invalid username provided"
        
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            return "❌ Error: TWITTER_BEARER_TOKEN not configured"
        
        counter = TwitterCounter(bearer_token)
        return counter.format_tweet_count_report(clean_username)
        
    except Exception as e:
        return f"❌ Error generating tweet count report: {str(e)}"

@mcp.tool(description="Set up daily posting reminder - sends alert via Poke if tweet count is below threshold at specified time")
def setup_posting_reminder(username: str, reminder_time: str, min_posts: int = 1, custom_message: str = None) -> dict:
    """Set up daily posting reminder
    
    Args:
        username: Twitter username to monitor
        reminder_time: Time to check in HH:MM format (e.g., "18:00")  
        min_posts: Minimum posts required (default: 1)
        custom_message: Optional custom reminder message
    """
    try:
        # Clean and validate username
        if not username or not isinstance(username, str):
            return {"error": "Username is required and must be a string"}
        
        clean_username = username.strip().lstrip('@').lower()
        if not clean_username:
            return {"error": "Invalid username provided"}
        
        poke_client = get_poke_client()
        if not poke_client:
            return {"error": "POKE_API_KEY not configured"}
            
        reminder = PostingReminder(poke_client)
        return reminder.setup_daily_reminder(clean_username, reminder_time, min_posts, custom_message)
        
    except Exception as e:
        return {"error": f"Failed to setup posting reminder: {str(e)}"}

@mcp.tool(description="Check posting reminders and send alerts if needed - typically called by scheduled job")
def check_posting_reminders() -> dict:
    """Check all configured reminders and send alerts if needed"""
    try:
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            return {"error": "TWITTER_BEARER_TOKEN not configured"}
            
        poke_client = get_poke_client()
        if not poke_client:
            return {"error": "POKE_API_KEY not configured"}
            
        counter = TwitterCounter(bearer_token)
        reminder = PostingReminder(poke_client)
        
        return reminder.check_and_send_reminders(counter)
        
    except Exception as e:
        return {"error": f"Failed to check reminders: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print("🚀 Starting Twitter Tweet Counter MCP Server with Poke Integration")
    print("📊 Tweet counting tools loaded (using /2/tweets/counts/recent)")
    print("⏰ Posting reminder system loaded")
    print("📤 Poke messaging integration loaded")
    print("📡 Server will be available at /mcp endpoint")
    print("🔧 Input validation and error handling enabled")
    print("")
    print("🔍 DEBUGGING HTTP 406 ERRORS:")
    print("   • MCP protocol requires POST requests to /mcp")
    print("   • Client making GET requests will receive 406 errors")
    print("   • Ensure MCP client is configured for HTTP transport")
    print("   • Server URL should be: https://your-domain.com/mcp")
    print("   • Required headers: Content-Type: application/json")
    
    # Check for API keys
    poke_api_key = os.getenv('POKE_API_KEY')
    twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not poke_api_key:
        print("⚠️  WARNING: POKE_API_KEY environment variable not set")
        print("   Poke functionality will be unavailable")
    else:
        print(f"✅ Poke API key configured: {poke_api_key[:10]}...")
    
    if not twitter_token:
        print("⚠️  WARNING: TWITTER_BEARER_TOKEN environment variable not set")
        print("   Twitter functionality will be unavailable")
    else:
        print(f"✅ Twitter API token configured: {twitter_token[:10]}...")
    
    print(f"🌐 Starting FastMCP server on {host}:{port}")
    
    # FastMCP HTTP transport - using stateless HTTP for Render deployment
    try:
        print(f"🔧 Starting FastMCP HTTP server...")
        print(f"   Transport: HTTP (stateless)")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Endpoint: /mcp")
        
        mcp.run(
            transport="http",
            host=host,
            port=port,
            stateless_http=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   FastMCP version: Check compatibility with deployment platform")
        sys.exit(1)