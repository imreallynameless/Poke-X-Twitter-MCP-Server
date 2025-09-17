# Twitter MCP Server with Poke Integration

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides Twitter metrics and automated posting reminders with Poke.com integration. Built with [FastMCP](https://github.com/jlowin/fastmcp) for easy deployment on Render.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/imreallynameless/Poke-X-Twitter-MCP-Server)

## Features

### 🐦 Twitter Metrics
- **Tweet Count Tracking**: Get the number of tweets posted by any user in the last 24 hours
- **Formatted Reports**: Generate beautiful, emoji-rich tweet count reports
- **API Optimization**: Uses Twitter's `/2/tweets/counts/recent` endpoint for efficient counting
- **User ID Caching**: Saves API quota by caching user lookups

### ⏰ Automated Reminders
- **Daily Posting Reminders**: Set up automated reminders to encourage consistent posting
- **Customizable Thresholds**: Define minimum daily post requirements
- **Smart Scheduling**: Reminders sent at specified times via Poke.com
- **Goal Tracking**: Only sends reminders when posting goals aren't met

### 📱 Poke Integration
- **Seamless Messaging**: Send reminders and reports directly through Poke.com
- **Bulk Messaging**: Support for sending multiple messages at once
- **Connection Testing**: Built-in API connectivity verification

## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `greet` | Welcome message from the MCP server | `name` (string) |
| `test_connection` | Test server connectivity and health | None |
| `debug_request` | Debug MCP protocol functionality | None |
| `get_server_info` | Get server information and available tools | None |
| `get_tweet_count_24h` | Get tweet count for last 24 hours | `username` (string) |
| `get_tweet_count_report` | Get formatted tweet count report | `username` (string) |
| `setup_posting_reminder` | Set up daily posting reminder | `username`, `reminder_time`, `min_posts`, `custom_message` |
| `check_posting_reminders` | Check and send reminders if needed | None |

## Setup

### Prerequisites
- Python 3.13+
- Twitter API Bearer Token (X API v2)
- Poke.com API Key

### Environment Variables
```bash
# Required
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
POKE_API_KEY=your_poke_api_key

# Optional
ENVIRONMENT=production
```

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imreallynameless/Poke-X-Twitter-MCP-Server.git
   cd Poke-X-Twitter-MCP-Server
   ```

2. **Set up Python environment**:
   ```bash
   conda create -n twitter-mcp python=3.13
   conda activate twitter-mcp
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
   export POKE_API_KEY="your_poke_api_key"
   ```

4. **Run the server**:
   ```bash
   python src/server.py
   ```

5. **Test with MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
   Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.

## Deployment

### Option 1: One-Click Deploy
Click the "Deploy to Render" button above.

### Option 2: Manual Deployment
1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Add environment variables in Render dashboard
6. Deploy

Your server will be available at `https://your-service-name.onrender.com/mcp`

**Note**: The root URL (`https://your-service-name.onrender.com`) automatically redirects to this GitHub repository.

## Poke.com Integration

### Setup
1. Get your API key from [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add it as the `POKE_API_KEY` environment variable
3. Test the connection with the `test_connection` tool

### Usage
- **Posting Reminders**: Set up daily reminders that automatically check tweet counts and send alerts via Poke
- **Custom Messages**: Create personalized reminder messages
- **Scheduled Checks**: Use `check_posting_reminders` in a cron job for automated monitoring

### Example Reminder Setup
```python
# Set up a daily reminder for 6 PM
setup_posting_reminder(
    username="your_username",
    reminder_time="18:00",
    min_posts=1,
    custom_message="Time to share something with your followers! 🚀"
)
```

## API Usage & Limits

### Twitter API (Free Tier)
- **Monthly Limit**: 100 API calls
- **Efficiency**: ~45-50 daily checks possible per month
- **Optimization**: User ID caching reduces API calls by 50%
- **Endpoint**: Uses `/2/tweets/counts/recent` for efficient counting

### Rate Limiting
- Built-in API call tracking and warnings
- Automatic rate limit detection
- Graceful error handling for quota exceeded scenarios

## Example Usage

### Get Tweet Count
```python
# Get raw tweet count data
result = get_tweet_count_24h("username")
print(f"@{result['username']} posted {result['tweet_count_24h']} tweets in 24h")

# Get formatted report
report = get_tweet_count_report("username")
print(report)
# Output: 📊 Tweet Count Report - 2025-01-XX
#         👤 @username
#         🚀 3 tweets today
#         📈 API calls used: 2/100 monthly
```

### Set Up Reminders
```python
# Basic reminder
setup_posting_reminder("username", "18:00")

# Custom reminder with goal
setup_posting_reminder(
    username="username",
    reminder_time="09:00",
    min_posts=2,
    custom_message="Good morning! Ready to share your daily insights? 🌅"
)
```

## Architecture

- **FastMCP**: HTTP transport for web deployment
- **Twitter API v2**: Modern, efficient tweet counting
- **Poke.com API**: Reliable messaging and notifications
- **Render**: Zero-config deployment platform
- **Python 3.13**: Latest Python features and performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

- **Issues**: [GitHub Issues](https://github.com/imreallynameless/Poke-X-Twitter-MCP-Server/issues)
- **Documentation**: [MCP Protocol](https://modelcontextprotocol.io/)
- **Twitter API**: [X Developer Portal](https://developer.x.com/)
- **Poke.com**: [Poke Documentation](https://poke.com/docs)