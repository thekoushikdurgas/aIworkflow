# 🔧 Configuration Guide

This guide explains how to configure the Google GenAI Streamlit Agent for your specific needs.

## 🌟 Quick Setup

### Option 1: Gemini Developer API (Recommended for getting started)

1. **Get an API Key**
   - Visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
   - Sign in with your Google account
   - Create an API key
   - Copy the key

2. **Set Environment Variable**

   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

   Or on Windows:

   ```cmd
   set GOOGLE_API_KEY=your-api-key-here
   ```

3. **Run the Application**

   ```bash
   streamlit run app.py
   ```

### Option 2: Vertex AI (For enterprise/production use)

1. **Set up Google Cloud Project**
   - Create a Google Cloud project
   - Enable the Vertex AI API
   - Set up authentication

2. **Set Environment Variables**

   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="us-central1"
   ```

3. **Authenticate**

   ```bash
   gcloud auth application-default login
   ```

## 📋 Environment Variables Reference

### Required Variables

#### For Gemini Developer API

```bash
GOOGLE_API_KEY=your-api-key          # Primary API key variable
GEMINI_API_KEY=your-api-key          # Alternative variable name
```

#### For Vertex AI

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json  # Optional
```

### Optional Variables

#### Application Behavior

```bash
GOOGLE_GENAI_USE_VERTEXAI=true      # Force Vertex AI mode
DEBUG_MODE=false                     # Enable debug logging
DEFAULT_MODEL=gemini-2.5-flash      # Default model selection
AUTO_SAVE_CHATS=true                # Enable auto-save
```

#### Performance & Limits

```bash
REQUEST_TIMEOUT=60                   # Request timeout (seconds)
RETRY_ATTEMPTS=3                    # Retry failed requests
RATE_LIMIT_RPM=60                   # Rate limit (requests/minute)
MAX_FILE_SIZE_MB=100                # Max file upload size
```

## 🎯 Model Configuration

### Available Models

#### **Text Generation Models**

- `gemini-2.5-pro` - Most capable, best for complex reasoning
- `gemini-2.5-flash` - Balanced performance and speed  
- `gemini-2.5-flash-lite` - Fast and cost-effective
- `gemini-2.0-flash` - Latest stable model
- `gemini-1.5-flash` - Previous generation (deprecated)
- `gemini-1.5-pro` - Previous generation (deprecated)

#### **Image Generation Models**

- `imagen-4.0-fast-generate-001` - Fast image generation
- `imagen-4.0-generate-001` - Standard quality
- `imagen-4.0-ultra-generate-001` - Highest quality
- `imagen-3-generate-001` - Previous generation

#### **Video Generation Models**

- `veo-3.0-fast-generate-preview` - Fast video generation
- `veo-3.0-generate-preview` - High-quality videos
- `veo-2-generate-preview` - Previous generation

#### **Text-to-Speech Models**

- `gemini-2.5-flash-preview-tts` - Fast TTS
- `gemini-2.5-pro-preview-tts` - High-quality TTS

### Model Selection Guide

#### **For General Chat & Content Creation**

```
Model: gemini-2.5-flash
Temperature: 0.7
Top-P: 0.95
Top-K: 40
```

#### **For Complex Analysis & Reasoning**

```
Model: gemini-2.5-pro
Temperature: 0.3
Thinking Budget: 1000-5000
Top-P: 0.9
```

#### **For High-Volume Simple Tasks**

```
Model: gemini-2.5-flash-lite
Temperature: 0.5
Max Tokens: 1024
```

#### **For Creative Writing**

```
Model: gemini-2.5-flash
Temperature: 0.9
Top-P: 0.95
Top-K: 60
```

## ⚙️ Advanced Configuration

### Function Calling Setup

1. **Enable Function Calling**
   - Go to Model Configuration
   - Check "Enable Function Calling"
   - Add your custom functions

2. **Create Custom Functions**

   ```python
   def get_weather(location: str) -> str:
       """Get weather for a location"""
       # Your implementation
       return weather_data
   ```

3. **Function Schema Example**

   ```json
   {
     "name": "get_weather",
     "description": "Get current weather",
     "parameters": {
       "type": "object",
       "properties": {
         "location": {
           "type": "string",
           "description": "City name"
         }
       },
       "required": ["location"]
     }
   }
   ```

### Structured Outputs

1. **JSON Schema Example**

   ```json
   {
     "type": "object",
     "properties": {
       "summary": {"type": "string"},
       "sentiment": {
         "type": "string",
         "enum": ["positive", "negative", "neutral"]
       },
       "key_points": {
         "type": "array",
         "items": {"type": "string"}
       }
     },
     "required": ["summary", "sentiment"]
   }
   ```

2. **Pydantic Model Example**

   ```python
   from pydantic import BaseModel
   from typing import List
   
   class AnalysisResult(BaseModel):
       summary: str
       sentiment: str
       key_points: List[str]
       confidence: float
   ```

### Safety Settings

Configure content filtering for different use cases:

#### **Permissive (Development/Testing)**

```
Hate Speech: Block Only High
Dangerous Content: Block Only High  
Harassment: Block Only High
Sexually Explicit: Block Only High
```

#### **Balanced (General Use)**

```
Hate Speech: Block Medium and Above
Dangerous Content: Block Medium and Above
Harassment: Block Medium and Above
Sexually Explicit: Block Medium and Above
```

#### **Strict (Educational/Enterprise)**

```
Hate Speech: Block Low and Above
Dangerous Content: Block Low and Above
Harassment: Block Low and Above
Sexually Explicit: Block Low and Above
```

## 🔒 Security Configuration

### API Key Security

1. **Never commit API keys to version control**

   ```bash
   # Add to .gitignore
   .env
   *.key
   secrets/
   ```

2. **Use environment variables**

   ```bash
   # Good
   export GOOGLE_API_KEY="your-key"
   
   # Bad - hardcoded in code
   api_key = "your-key"  # Don't do this!
   ```

3. **Rotate keys regularly**
   - Generate new keys monthly
   - Revoke old keys immediately
   - Monitor usage for anomalies

### Vertex AI Security

1. **Use IAM roles**

   ```bash
   # Grant minimal required permissions
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:SA_EMAIL" \
     --role="roles/aiplatform.user"
   ```

2. **Service Account Best Practices**
   - Create dedicated service accounts
   - Use workload identity when possible
   - Regularly audit permissions

### Network Security

1. **Restrict API access**

   ```bash
   # Configure firewall rules
   # Use VPC if needed
   # Monitor API usage
   ```

2. **Use HTTPS only**
   - All API calls are encrypted
   - Verify SSL certificates
   - Use secure headers

## 📊 Performance Optimization

### Cost Optimization

1. **Choose the right model**
   - Use Lite models for simple tasks
   - Use Pro models only when needed
   - Monitor token usage

2. **Enable caching**

   ```bash
   ENABLE_CACHING=true
   CACHE_TTL_HOURS=1
   ```

3. **Optimize prompts**
   - Be specific and concise
   - Use system instructions effectively
   - Avoid redundant context

### Speed Optimization

1. **Enable streaming**

   ```bash
   ENABLE_STREAMING=true
   ```

2. **Adjust thinking budget**

   ```bash
   # Lower for faster responses
   DEFAULT_THINKING_BUDGET=0
   
   # Higher for better quality
   DEFAULT_THINKING_BUDGET=2000
   ```

3. **Use faster models**
   - Flash models for speed
   - Lite models for high volume

### Memory Optimization

1. **Manage file uploads**

   ```bash
   MAX_FILE_SIZE_MB=50
   ```

2. **Clean up sessions**

   ```bash
   SESSION_TIMEOUT_MINUTES=30
   ```

3. **Limit concurrent operations**

   ```bash
   MAX_CONCURRENT_SESSIONS=5
   ```

## 🛠️ Development Configuration

### Debug Mode

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_DEBUG_LOGGING=true
```

### Testing Configuration

```bash
MOCK_API_RESPONSES=true
ENABLE_HOT_RELOAD=true
ENABLE_PROFILING=true
```

### Production Configuration

```bash
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_SECURITY_FEATURES=true
ENABLE_CACHING=true
REQUEST_TIMEOUT=30
```

## 🌍 Regional Configuration

### US Regions

```bash
GOOGLE_CLOUD_LOCATION=us-central1  # Iowa
GOOGLE_CLOUD_LOCATION=us-east1     # South Carolina
GOOGLE_CLOUD_LOCATION=us-west1     # Oregon
```

### Europe Regions

```bash
GOOGLE_CLOUD_LOCATION=europe-west1  # Belgium
GOOGLE_CLOUD_LOCATION=europe-west4  # Netherlands
```

### Asia Regions

```bash
GOOGLE_CLOUD_LOCATION=asia-southeast1  # Singapore
GOOGLE_CLOUD_LOCATION=asia-northeast1  # Tokyo
```

## 🔄 Migration & Backup

### Export Configuration

1. Go to Model Configuration
2. Click "Export Config"
3. Save the JSON file

### Import Configuration

1. Go to Model Configuration
2. Click "Import Config"
3. Upload your JSON file

### Backup Chat History

1. Go to Chat History
2. Click "Export All Sessions"
3. Save the JSON file

## 🆘 Troubleshooting

### Common Configuration Issues

#### **API Key Not Working**

```bash
# Check if key is set
echo $GOOGLE_API_KEY

# Test with curl
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

#### **Vertex AI Authentication Failed**

```bash
# Check authentication
gcloud auth list

# Test API access
gcloud ai models list --region=us-central1
```

#### **Model Not Available**

```bash
# List available models
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

### Performance Issues

1. **Slow responses**
   - Use faster models (Flash vs Pro)
   - Reduce thinking budget
   - Enable streaming

2. **High costs**
   - Use Lite models
   - Enable caching
   - Optimize prompts

3. **Rate limiting**
   - Reduce request frequency
   - Use batch processing
   - Upgrade quota

## 📞 Support

For configuration help:

1. Check the [troubleshooting section](README.md#troubleshooting)
2. Review [Google's documentation](https://ai.google.dev/gemini-api/docs)
3. Check the [community forums](https://discuss.ai.google.dev/)

---

*Happy configuring! 🚀*
