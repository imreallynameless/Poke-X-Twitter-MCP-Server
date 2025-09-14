#!/usr/bin/env python3
"""
Poke API Python Implementation
A simple wrapper for interacting with the Poke.com API programmatically.
"""

import requests
import json
from typing import Dict, Any, Optional
import os
import sys
from datetime import datetime

class PokeAPI:
    """A Python client for the Poke.com API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the Poke API client
        
        Args:
            api_key: Your Poke API key
        """
        self.api_key = api_key
        self.base_url = 'https://poke.com/api/v1'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a message via the Poke API
        
        Args:
            message: The message content to send
            
        Returns:
            API response as dictionary
        """
        endpoint = f'{self.base_url}/inbound-sms/webhook'
        
        payload = {
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Request failed: {str(e)}',
                'status_code': getattr(e.response, 'status_code', None)
            }
    
    def send_bulk_messages(self, messages: list) -> list:
        """
        Send multiple messages in batch
        
        Args:
            messages: List of message strings
            
        Returns:
            List of API responses
        """
        results = []
        for message in messages:
            result = self.send_message(message)
            results.append(result)
        return results
    
    def test_connection(self) -> bool:
        """
        Test if the API connection is working
        
        Returns:
            True if connection successful, False otherwise
        """
        test_message = "Connection test from Python client"
        result = self.send_message(test_message)
        return not result.get('error', False)

def main():
    """Example usage of the Poke API client"""
    
    # Get API key from environment variable
    API_KEY = os.getenv('POKE_API_KEY')
    
    if not API_KEY:
        print("❌ Error: POKE_API_KEY environment variable not set!")
        print("Set it with: export POKE_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Initialize the client
    poke_client = PokeAPI(API_KEY)
    
    # Test connection
    print("Testing connection...")
    if poke_client.test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
        return
    
    # Send a single message
    print("\nSending single message...")
    response = poke_client.send_message("Hello from Python! 🐍")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Send multiple messages
    print("\nSending multiple messages...")
    messages = [
        "First message from batch",
        "Second message from batch",
        "Third message from batch 🚀"
    ]
    
    responses = poke_client.send_bulk_messages(messages)
    for i, response in enumerate(responses):
        print(f"Message {i+1} response: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    main()
