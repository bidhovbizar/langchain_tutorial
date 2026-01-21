# Intelligent OAuth Token Management

## Overview

The system now implements intelligent OAuth token management to avoid unnecessary token generation while ensuring the token is always valid.

## How It Works

### 1. **Token Caching**
- Tokens are cached in memory for their full lifetime (1 hour = 3600 seconds)
- Cache includes the token and expiration timestamp
- Only one token is generated per hour, reused across all requests

### 2. **Automatic Token Validation**
- Before each analysis, the system tests if the current token is valid
- Sends a simple "Hi" message to the AI to verify authentication
- If token is expired (401 error), automatically gets a new one

### 3. **Automatic Retry on Expiry**
- If analysis fails with authentication error (401/Token Expired):
  - System automatically refreshes the token
  - Retries the analysis with the new token
  - Maximum 2 attempts to handle transient issues

### 4. **Smart Token Refresh**
- Tokens are cached with a 60-second buffer (expire at 3540 seconds)
- This prevents using a token that's about to expire
- New tokens are only generated when:
  - No cached token exists
  - Cached token has expired
  - Force refresh is requested
  - Authentication fails with current token

## Configuration

The OAuth credentials are configured in `circuit_langchain_summarizer.py`:

```python
CLIENT_ID = '0oasijtht0KJw99dW5d7'
CLIENT_SECRET = 'T3Pe7CWYpM2DSadIfVOYhQykxGG-Mz-fR_EKTGzTwBwFB1Fy0u_HaknaSudq9E5D'
```

## Token Response Format

When a new token is generated, the response looks like:

```json
{
  "token_type": "Bearer",
  "expires_in": 3600,
  "access_token": "eyJraWQiOiI5NGU4cmxzTzUy...",
  "scope": "customscope"
}
```

The system extracts and caches the `access_token` value.

## Usage Flow

### First Request
```
User → Analyze Report
  ↓
No cached token exists
  ↓
Generate new OAuth token
  ↓
Cache token (valid for 1 hour)
  ↓
Test token validity
  ↓
Initialize AI model
  ↓
Analyze report
```

### Subsequent Requests (Within 1 Hour)
```
User → Analyze Report
  ↓
Check cached token
  ↓
Token still valid (e.g., 45 mins left)
  ↓
Use cached token
  ↓
Test token validity
  ↓
Analyze report (no new token generated!)
```

### Request After Token Expiry
```
User → Analyze Report
  ↓
Check cached token
  ↓
Token expired (> 1 hour old)
  ↓
Generate new OAuth token
  ↓
Cache new token
  ↓
Initialize AI model with new token
  ↓
Analyze report
```

### Handling Mid-Analysis Expiry
```
User → Analyze Report
  ↓
Use cached token
  ↓
Start analysis
  ↓
Token expires during analysis (rare)
  ↓
Catch 401 AuthenticationError
  ↓
Automatically generate new token
  ↓
Retry analysis with new token
  ↓
Success!
```

## Benefits

1. **Efficiency**: Tokens are reused for their full lifetime
2. **Reliability**: Automatic retry on token expiry
3. **User-Friendly**: No manual token management required
4. **Resilient**: Handles edge cases like mid-analysis expiry
5. **Performance**: Avoids unnecessary OAuth requests

## Implementation Details

### Key Functions

#### `get_oauth_token(client_id, client_secret, force_refresh=False)`
- Gets or refreshes OAuth token
- Returns cached token if still valid
- Generates new token only when needed

#### `test_token_validity(access_token)`
- Tests if token is valid
- Sends simple "Hi" message to AI
- Returns True if valid, False if expired

#### `SummarizerWrapper.analyze_full(report_path, callback)`
- Main analysis function
- Automatically handles token expiry
- Retries with fresh token on auth failure

### Error Detection

The system detects token expiry by checking for:
- HTTP status code **401**
- Error messages containing **"Expired"**
- **"AuthenticationError"** exceptions
- Error messages containing **"Token has expired"**

## Console Output Examples

### Using Cached Token
```
Using cached token (valid for 2847 more seconds)
```

### Generating New Token
```
Fetching new OAuth token...
✅ New token obtained (valid for 3600 seconds)
```

### Token Expired During Analysis
```
⚠️  Token expired, getting new token (attempt 1/2)...
Fetching new OAuth token...
✅ New token obtained (valid for 3600 seconds)
Retrying analysis with new token...
```

## Troubleshooting

### Issue: "CLIENT_ID and CLIENT_SECRET not configured"
**Solution**: Update the credentials in `circuit_langchain_summarizer.py`

### Issue: "Failed to get OAuth token"
**Solution**: 
- Check CLIENT_ID and CLIENT_SECRET are correct
- Verify network connectivity to id.cisco.com
- Check if credentials have required permissions

### Issue: Token keeps expiring quickly
**Solution**: This is expected behavior - tokens expire after 1 hour. The system handles this automatically.

## Security Notes

- Tokens are stored in memory only (not on disk)
- Tokens are automatically refreshed as needed
- Each application instance maintains its own token cache
- Multi-user web app: Each process has its own token (shared across users in that process)

## Future Enhancements

Potential improvements:
- [ ] Persistent token storage across application restarts
- [ ] Token sharing across multiple processes
- [ ] Proactive token refresh before expiry
- [ ] Metrics on token usage and refresh frequency

