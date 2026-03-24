# Discord Integration Setup Guide

## Prerequisites
1. A Discord server where you want to receive notifications
2. Administrator permissions on that Discord server

## Step 1: Create a Discord Webhook

1. Open your Discord server
2. Go to **Server Settings** (click on server name → Server Settings)
3. Navigate to **Integrations** → **Webhooks**
4. Click **Create Webhook**
5. Configure the webhook:
   - **Name**: `Honeypot Security`
   - **Channel**: Choose the channel where you want attack notifications
   - **Avatar**: Optional - you can upload a security-themed icon
6. Click **Copy Webhook URL**
7. Save this URL - you'll need it for configuration

## Step 2: Configure Your Honeypot

### Option A: Environment Variable (Recommended)
```bash
# Windows (PowerShell)
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

# Windows (Command Prompt)
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Linux/Mac
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

### Option B: Direct Configuration
Edit `app.py` and replace the empty string:
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

## Step 3: Test the Integration

1. Start your honeypot application
2. Login as admin (username: `admin`, password: `admin`)
3. Go to the admin panel
4. Click **Test Discord Notification** to verify the webhook is working

## Features

### Real-time Attack Notifications
- **SQL Injection** attempts
- **XSS/Intrusion** attempts  
- **Path Traversal/LFI** attempts
- **Command Injection** attempts
- **Phishing** attempts
- **Brute Force** attempts
- **Malicious File Upload** attempts

### Notification Details
Each Discord alert includes:
- Attack type and severity
- Attacker's IP address
- Username (if available)
- Timestamp
- Attack payload/details
- User agent information
- Rich formatting with colors and icons

### Daily Summary Reports
- Total attacks for the day
- Breakdown by attack type
- Top attacking IP addresses
- Can be triggered manually from admin panel

## Security Notes

- Keep your webhook URL secret - anyone with it can send messages to your Discord channel
- Consider using a dedicated Discord channel for security alerts
- The webhook URL contains sensitive information - don't commit it to version control
- Use environment variables for production deployments

## Troubleshooting

### No Notifications Appearing
1. Check that `DISCORD_WEBHOOK_URL` is set correctly
2. Verify the webhook URL is valid and active
3. Check the console output for error messages
4. Test the webhook manually using the admin panel

### Permission Errors
- Ensure the webhook has permission to send messages in the target channel
- Check that the bot has the necessary permissions in Discord

### Rate Limiting
- Discord has rate limits for webhooks (30 requests per minute)
- The system includes error handling for rate limit scenarios
