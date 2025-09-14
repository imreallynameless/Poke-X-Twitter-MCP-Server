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
from twitter_metrics import TwitterMetrics, send_daily_twitter_report
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Twitter MCP Server with Poke Integration")

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
            "get_server_info", 
            "get_twitter_metrics",
            "send_twitter_daily_report_tool",
            "setup_twitter_automation"
        ]
    }

@mcp.tool(description="Get Twitter metrics for a specific user")
def get_twitter_metrics(username: str, days: int = 1) -> Dict[str, Any]:
    """
    Get Twitter metrics for a specific user
    
    Args:
        username: Twitter username (without @)
        days: Number of days to look back (default: 1)
        
    Returns:
        Dictionary containing Twitter metrics summary
    """
    try:
        twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not twitter_token:
            return {
                "success": False,
                "error": "TWITTER_BEARER_TOKEN environment variable not set",
                "message": "Please configure Twitter API credentials"
            }
        
        twitter = TwitterMetrics(twitter_token)
        summary = twitter.get_daily_summary(username)
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch Twitter metrics for @{username}",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool(description="Send daily Twitter metrics report via Poke")
def send_twitter_daily_report_tool(username: str) -> Dict[str, Any]:
    """
    Send daily Twitter metrics report via Poke
    
    Args:
        username: Twitter username (without @)
        
    Returns:
        Dictionary containing report status and Poke response
    """
    try:
        client = get_poke_client()
        result = send_daily_twitter_report(username, client)
        
        return {
            "success": result.get('success', False),
            "message": "Daily Twitter report sent via Poke successfully" if result.get('success') else "Failed to send report",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to send daily report for @{username} via Poke",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool(description="Set up automated daily Twitter metrics reports")
def setup_twitter_automation(username: str, time_hour: int = 21) -> Dict[str, Any]:
    """
    Set up automated daily Twitter metrics reports
    
    Args:
        username: Twitter username (without @)
        time_hour: Hour to send report (24-hour format, default: 21 for 9 PM)
        
    Returns:
        Dictionary containing automation setup status
    """
    try:
        # Note: This is a placeholder for automation setup
        # In a real deployment, you'd set up a cron job or scheduler
        
        return {
            "success": True,
            "message": f"Automation configured for @{username} at {time_hour}:00",
            "setup": {
                "username": username,
                "daily_time": f"{time_hour}:00",
                "timezone": "Server timezone",
                "note": "Automation requires deployment with scheduler (cron job or similar)"
            },
            "next_steps": [
                "Deploy server to production",
                "Set TWITTER_BEARER_TOKEN environment variable",
                "Configure cron job for daily execution",
                f"Schedule: 0 {time_hour} * * * python -c \"from twitter_metrics import *; from python_example import *; send_daily_twitter_report('{username}', PokeAPI(os.getenv('POKE_API_KEY')))\""
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to set up Twitter automation",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print("🚀 Starting Twitter MCP Server with Poke Integration")
    print("🐦 Twitter metrics tools loaded")
    print("📤 Poke messaging integration loaded")
    print("📡 Server will be available at /mcp endpoint")
    
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
    
    # FastMCP automatically supports HTTP transport for web deployment
    try:
        mcp.run(
            transport="http",
            host=host,
            port=port,
            stateless_http=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)