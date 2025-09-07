# 🤖 Streamlit GenAI Agent

A comprehensive AI agent built with Streamlit and Google's GenAI SDK, supporting multimodal conversations, media generation, and advanced AI capabilities.

## ✨ Features

- **🗣️ Multimodal Chat**: Text, images, audio, video, and PDF support
- **🎨 Media Generation**: Create images with Imagen and videos with Veo
- **🔧 Function Calling**: Custom tools and function integration
- **⚙️ Advanced Configuration**: Model parameters, safety settings, thinking budgets
- **📝 Session Management**: Save and restore chat conversations
- **🎯 Model Selection**: Choose from Gemini 2.5 Pro, Flash, Flash-Lite, and more
- **📊 Usage Tracking**: Monitor tokens, costs, and performance
- **🔍 Search Grounding**: Integrate Google Search for up-to-date information

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google GenAI API key or Vertex AI access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamlit_genai_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

### Environment Setup

#### Option 1: Gemini Developer API (Recommended for getting started)

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

#### Option 2: Vertex AI (For enterprise/production)

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
gcloud auth application-default login
```

## 📚 Usage Guide

### Basic Chat
1. Launch the app and go to the **Chat** page
2. Select your preferred model (gemini-2.5-flash recommended for general use)
3. Start chatting with text, upload images, or attach files

### Media Generation
1. Go to the **Media Studio** page
2. Choose between Image Generation (Imagen) or Video Generation (Veo)
3. Provide prompts and configure settings
4. Generate and download your media

### Function Calling
1. Visit the **Tool Workshop** page
2. Add custom functions or use predefined tools
3. Enable function calling in your chat configuration
4. The AI will automatically call functions when needed

### Model Configuration
1. Open the **Model Config** page
2. Adjust parameters like temperature, thinking budget, safety settings
3. Save configurations for different use cases
4. Apply configurations to your chat sessions

## 🏗️ Architecture

```
streamlit_genai_agent/
├── main.py                     # Main Streamlit app
├── config/                     # Configuration files
├── src/
│   ├── core/                   # Core business logic
│   ├── ui/                     # User interface components
│   ├── utils/                  # Utility functions
│   └── data/                   # Data models and schemas
├── assets/                     # Static assets
├── output/                     # Generated files and logs
└── tests/                      # Test suite
```

## 🔧 Configuration

The app supports extensive configuration options:

- **Model Parameters**: Temperature, Top-P, Top-K, Max Tokens
- **Thinking Budgets**: Control reasoning depth for Gemini 2.5 models
- **Safety Settings**: Configure content filtering levels
- **Performance**: Request timeouts, retry attempts, rate limits
- **File Handling**: Upload size limits, supported formats

See the **Model Config** page in the app for detailed options.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🆘 Support

- Check the in-app help sections
- Review Google's [Gemini API documentation](https://ai.google.dev/gemini-api/docs)
- Visit the [community forums](https://discuss.ai.google.dev/)

## 🚨 Important Notes

- **API Costs**: Video generation with Veo can be expensive. Check pricing before use.
- **Rate Limits**: Free tier has usage limits. Upgrade for higher quotas.
- **Privacy**: Your conversations are not stored by Google when using the API directly.
- **Model Updates**: Some experimental models may change or be discontinued.

---

*Built with ❤️ using Streamlit and Google's GenAI SDK*
