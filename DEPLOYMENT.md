# Rabbi Bot - Deployment Guide

## ✅ Code Portability

**Yes, this code will work in any repository!** The bot is designed to be completely portable and self-contained.

## Required Files for New Repository

### Core Files (Required)
```
├── main.py                     # Main entry point
├── pyproject.toml             # Dependencies
├── .env.example              # Environment template
├── .gitignore               # Git exclusions
├── README.md                # Documentation
├── bot/                     # Main bot package
│   ├── __init__.py
│   ├── discord_bot.py       # Core bot class
│   ├── streamlined_commands.py  # Optimized commands
│   ├── sefaria_client.py    # Sefaria API
│   ├── hebcal_client.py     # Jewish calendar API
│   ├── nli_client.py        # National Library API
│   ├── chabad_client.py     # Chabad.org API
│   ├── dicta_client.py      # Dicta AI books API
│   ├── ai_client.py         # OpenAI integration
│   └── utils.py             # Utility functions
```

### Optional Files (Enhanced Features)
```
├── bot/
│   ├── command_groups.py    # Interactive menu commands
│   ├── ai_message_handler.py # AI conversations
│   ├── opentorah_client.py  # Additional APIs
│   ├── torahcalc_client.py
│   ├── orayta_client.py
│   ├── opensiddur_client.py
│   └── pninim_client.py
```

## Environment Variables Required

Create `.env` file in root directory:
```env
# Required for Discord functionality
DISCORD_TOKEN=your_discord_bot_token_here

# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional APIs (bot works without these)
NLI_API_KEY=your_nli_api_key_here
```

## Platform-Specific Setup

### 1. Replit
```bash
# Dependencies auto-install from pyproject.toml
# Add secrets in Replit Secrets panel:
# DISCORD_TOKEN, OPENAI_API_KEY
python main.py
```

### 2. Fly.io
```bash
# Deploy with fly.toml
flyctl deploy
flyctl secrets set DISCORD_TOKEN="your_token"
flyctl secrets set OPENAI_API_KEY="your_key"
```

### 3. Heroku
```bash
# Use Procfile: web: python main.py
heroku create your-bot-name
heroku config:set DISCORD_TOKEN="your_token"
heroku config:set OPENAI_API_KEY="your_key"
git push heroku main
```

### 4. Railway
```bash
# Auto-deploys from GitHub
# Set environment variables in Railway dashboard
```

### 5. Local Development
```bash
pip install -e .
# Create .env file with tokens
python main.py
```

## Dependencies

All dependencies are managed through `pyproject.toml`:
- **discord.py** - Discord API wrapper
- **aiohttp** - Async HTTP client
- **openai** - OpenAI API client
- **python-dotenv** - Environment variables
- **deep-translator** - Translation service

## Bot Permissions Required

When creating Discord application, enable these permissions:
- Send Messages
- Use Slash Commands
- Read Message History
- Add Reactions
- Embed Links

## API Keys Setup

### Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Create new application
3. Go to "Bot" section
4. Copy token to `DISCORD_TOKEN`

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `OPENAI_API_KEY`

### Optional APIs
- **NLI_API_KEY**: Guest key included, or get your own from National Library of Israel
- Others: Bot gracefully handles missing API keys

## Architecture Benefits

### Self-Contained
- No external database required
- All state managed in memory
- No file system dependencies

### Graceful Degradation
- Missing API keys don't break core functionality
- Timeout handling prevents Discord API violations
- Fallback responses for service outages

### Scalable Design
- Async/await throughout
- Rate limiting implemented
- Memory efficient

## Quick Deployment Checklist

- [ ] Copy all required files to new repository
- [ ] Install dependencies: `pip install -e .`
- [ ] Set environment variables
- [ ] Create Discord application and bot
- [ ] Get Discord bot token
- [ ] Get OpenAI API key (optional but recommended)
- [ ] Run `python main.py`
- [ ] Invite bot to Discord server
- [ ] Test with `/ping` command

## Command Structure

The bot uses a streamlined command structure for optimal Discord integration:
- `/ping` - Test response
- `/study` - Interactive study menu
- `/search` - Text search
- `/shabbat` - Shabbat times
- `/calendar` - Hebrew calendar
- `/help` - Complete guide

## Support

The bot connects to 10+ Jewish institutions and provides 50+ functions through an intuitive interface. All functionality is preserved when deploying to any platform.