# Environment Variable Recovery Guide

If your `.env` file was accidentally overwritten or lost, follow these steps to recover your values.

## Quick Recovery Steps

1. **Check VSCode/Cursor Local History** (BEST CHANCE)
   - Open `.env` or `.env.save` in your editor
   - Use Timeline/Local History feature (usually in sidebar or right-click menu)
   - Restore a previous version that still has your values

2. **Check Terminal History**
   ```bash
   # Search for exported environment variables
   history | grep -i "export.*NOTION\|export.*META\|export.*CAPTION"
   
   # Or check your shell history file directly
   cat ~/.zsh_history | grep -i "NOTION\|META\|CAPTION"
   ```

3. **Check Time Machine** (macOS)
   - Open Time Machine
   - Navigate to your project directory
   - Find `.env` or `.env.save` from before the loss
   - Restore the file

4. **Check Deployed Server**
   - SSH into your VPS/deployed environment
   - Check the `.env` file there:
     ```bash
     cat /path/to/project/.env
     ```
   - Or check systemd service environment:
     ```bash
     systemctl show your-service-name | grep Environment
     ```

5. **Check Other Machines**
   - If you've run this project on other computers, check their `.env` files

## Recovery File Template

Use `RECOVERED_ENV_VALUES.txt` to collect values as you find them. Once you have all values:

1. Copy `.env.example` to `.env`:
   ```bash
   cp domain_expansion/.env.example domain_expansion/.env
   ```

2. Fill in values from `RECOVERED_ENV_VALUES.txt`

3. Run the environment check:
   ```bash
   python domain_expansion/scripts/check_env.py
   ```

## What to Look For

### Notion Integration
- `NOTION_TOKEN` - Integration token from notion.so/my-integrations
- `NOTION_ACCOUNTS_DB_ID` - Database ID (UUID format)
- `NOTION_BUSINESSES_DB_ID` - Database ID
- `NOTION_CAPTION_DB_ID` - Database ID
- `NOTION_POSTS_DB_ID` - Database ID

### Captorator v2
- `CAPTION_BUILDER_DB_ID` - Notion database ID for caption builder
- Alternative names: `CAPTIONATOR_DB_ID`, `CAPTION_BUILDER_DATABASE_ID`

### Businesses Database
- `BUSINESSES_DB_ID` - Notion database ID
- Alternative: `BUSINESSES_DATABASE_ID`

### Meta Graph API
- `META_ACCESS_TOKEN` - Facebook/Instagram API access token

### Critical (Must Change)
- `SECRET_KEY` - Must be at least 32 characters, random
- `ADMIN_PASSWORD` - Must be changed from default

## Prevention

To prevent this from happening again:

1. **Never use automated tools to edit `.env`** - Always edit manually
2. **Use `.env.example` as template** - Never commit `.env` to git
3. **Backup important values** - Store in a secure password manager
4. **Use the preflight check** - `run_dev.sh` now checks environment before starting

## Database ID Format

Notion database IDs are UUIDs like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

You can find them in:
- Notion database URL: `https://www.notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- The ID is the part after the last `/` (with dashes removed in URL, but use with dashes in .env)
