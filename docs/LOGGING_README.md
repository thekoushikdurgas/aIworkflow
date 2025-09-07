# GenAI Dashboard Logging System

## Overview

The GenAI Dashboard now includes a comprehensive logging system that captures application events, user interactions, API requests, errors, and performance metrics. All logs are saved to the `output/logs/` directory.

## Log Files

### Main Log Files

1. **`genai_dashboard.log`** - Main application log (rotating, max 10MB, 5 backups)
   - Contains INFO level and above messages
   - Includes all application events, API calls, and user actions

2. **`errors.log`** - Error-only log (rotating, max 5MB, 3 backups)
   - Contains only ERROR and CRITICAL level messages
   - Includes full stack traces and error context

3. **`daily_YYYYMMDD.log`** - Daily log file
   - Contains all DEBUG level and above messages for the current day
   - Creates a new file each day

4. **`chat_interactions.log`** - Chat-specific interactions
   - Records all user-AI chat exchanges
   - Includes model information and metadata

### Log Format

```
TIMESTAMP | LOGGER_NAME | LEVEL | MODULE:FUNCTION:LINE | MESSAGE
```

Example:
```
2024-01-15 14:30:25 | genai_dashboard.chat | INFO | chat_page:send_message:245 | Sending message - Length: 42 chars, Files: 0
```

## Logging Features

### 1. User Action Tracking

- Page navigation
- Message sending
- File uploads
- Configuration changes
- Chat session management

### 2. API Request Monitoring

- Model requests and responses
- Token usage tracking
- Response times
- Error rates

### 3. Performance Metrics

- Page render times
- API response times
- File processing times
- Overall operation durations

### 4. Error Handling

- Detailed error context
- Stack traces
- User data (anonymized)
- Recovery suggestions

### 5. Chat Interaction Logging

- Separate log for chat conversations
- Model and configuration tracking
- Message metadata

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General application events
- **WARNING**: Potential issues or deprecated features
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Serious errors that may cause application failure

## Configuration

The logging system is automatically initialized when the application starts. No additional configuration is required.

### Key Features

- **Automatic rotation**: Log files rotate when they reach size limits
- **Colored console output**: Different colors for different log levels
- **Exception handling**: Automatic logging of uncaught exceptions
- **Performance tracking**: Built-in timing for operations
- **Context preservation**: Rich context information with errors

## Usage Examples

### In Application Code

```python
from utils.logger_config import get_logger, log_user_action, log_performance

logger = get_logger('my_module')

# Basic logging
logger.info("User started new chat session")
logger.error("Failed to process uploaded file")

# User action logging
log_user_action("send_message", {"message_length": 150, "model": "gemini-2.5-flash"})

# Performance logging
start_time = time.time()
# ... some operation ...
duration = time.time() - start_time
log_performance("image_generation", duration, {"model": "imagen-4.0", "images": 2})
```

### Chat Interaction Logging

Chat interactions are automatically logged when messages are added to the chat history. The system captures:

- User message content (truncated for privacy)
- AI response content (truncated)
- Model used
- Response metadata (tokens, timing, etc.)

## Log Analysis

### Common Log Queries

1. **Find all errors in the last hour:**
   ```bash
   grep "$(date -d '1 hour ago' +'%Y-%m-%d %H')" output/logs/errors.log
   ```

2. **Check API performance:**
   ```bash
   grep "PERFORMANCE.*api" output/logs/genai_dashboard.log
   ```

3. **Monitor user actions:**
   ```bash
   grep "USER_ACTION" output/logs/genai_dashboard.log
   ```

4. **Chat interaction summary:**
   ```bash
   grep "CHAT |" output/logs/chat_interactions.log | tail -20
   ```

### Log Monitoring

The logging system provides rich information for:

- **Debugging**: Detailed error traces and context
- **Performance Monitoring**: Response times and bottlenecks
- **Usage Analytics**: User behavior and feature adoption
- **Security**: Authentication and access patterns
- **Compliance**: Audit trail of all actions

## Privacy and Security

- User message content is truncated in logs (first 200 characters)
- Sensitive information like API keys are never logged
- File content is not logged, only metadata
- Error logs include sanitized context information

## Maintenance

- Log files automatically rotate to prevent disk space issues
- Old log files are compressed and archived
- Default retention: 5 main log files, 3 error log files
- Daily logs are kept indefinitely (manual cleanup required)

## Troubleshooting

### Common Issues

1. **Logs not appearing**: Check file permissions in `output/logs/` directory
2. **High disk usage**: Configure log rotation settings in `logger_config.py`
3. **Missing chat logs**: Ensure chat interactions are going through `add_message_to_chat()`

### Log File Locations

All logs are stored in: `output/logs/`

- Main logs: `genai_dashboard.log`, `genai_dashboard.log.1`, etc.
- Error logs: `errors.log`, `errors.log.1`, etc.
- Daily logs: `daily_20240115.log`, etc.
- Chat logs: `chat_interactions.log`

This logging system provides comprehensive monitoring and debugging capabilities for the GenAI Dashboard application while maintaining user privacy and system performance.
