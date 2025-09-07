Skip to main content
Google AI for Developers
Search
/

English
Sign in
Gemini API docs
API Reference
Cookbook
Community

Gemini 2.5 Flash Image (aka Nano Banana) is now available in the Gemini API! Learn more
Home
Gemini API
Gemini API docs
Was this helpful?

Send feedbackGemini models

2.5 Pro

Our most powerful thinking model with maximum response accuracy and state-of-the-art performance

Input audio, images, video, and text, get text responses
Tackle difficult problems, analyze large databases, and more
Best for complex coding, reasoning, and multimodal understanding
2.5 Flash

Our best model in terms of price-performance, offering well-rounded capabilities.

Input audio, images, video, and text, and get text responses
Model thinks as needed; or, you can configure a thinking budget
Best for low latency, high volume tasks that require thinking
2.5 Flash-Lite

A Gemini 2.5 Flash model optimized for cost efficiency and low latency.

Input audio, images, video, and text, and get text responses
Most cost-efficient model supporting high throughput
Best for real time, low latency use cases
Note: Gemini 2.5 Pro and 2.5 Flash come with thinking on by default. If you're migrating from a non-thinking model such as 2.0 Pro or Flash, we recommend you to review the Thinking guide first.
Model variants
The Gemini API offers different models that are optimized for specific use cases. Here's a brief overview of Gemini variants that are available:

Model variant Input(s) Output Optimized for
Gemini 2.5 Pro
gemini-2.5-pro Audio, images, videos, text, and PDF Text Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more
Gemini 2.5 Flash
gemini-2.5-flash Audio, images, videos, and text Text Adaptive thinking, cost efficiency
Gemini 2.5 Flash-Lite
gemini-2.5-flash-lite Text, image, video, audio Text Most cost-efficient model supporting high throughput
Gemini 2.5 Flash Live
gemini-live-2.5-flash-preview Audio, video, and text Text, audio Low-latency bidirectional voice and video interactions
Gemini 2.5 Flash Native Audio
gemini-2.5-flash-preview-native-audio-dialog &
gemini-2.5-flash-exp-native-audio-thinking-dialog Audio, videos, and text Text and audio, interleaved High quality, natural conversational audio outputs, with or without thinking
Gemini 2.5 Flash Image Preview
gemini-2.5-flash-image-preview Images and text Images and text Precise, conversational image generation and editing
Gemini 2.5 Flash Preview TTS
gemini-2.5-flash-preview-tts Text Audio Low latency, controllable, single- and multi-speaker text-to-speech audio generation
Gemini 2.5 Pro Preview TTS
gemini-2.5-pro-preview-tts Text Audio Low latency, controllable, single- and multi-speaker text-to-speech audio generation
Gemini 2.0 Flash
gemini-2.0-flash Audio, images, videos, and text Text Next generation features, speed, and realtime streaming.
Gemini 2.0 Flash Preview Image Generation
gemini-2.0-flash-preview-image-generation Audio, images, videos, and text Text, images Conversational image generation and editing
Gemini 2.0 Flash-Lite
gemini-2.0-flash-lite Audio, images, videos, and text Text Cost efficiency and low latency
Gemini 2.0 Flash Live
gemini-2.0-flash-live-001 Audio, video, and text Text, audio Low-latency bidirectional voice and video interactions
Gemini 1.5 Flash
gemini-1.5-flash Audio, images, videos, and text Text Fast and versatile performance across a diverse variety of tasks
Deprecated
Gemini 1.5 Flash-8B
gemini-1.5-flash-8b Audio, images, videos, and text Text High volume and lower intelligence tasks
Deprecated
Gemini 1.5 Pro
gemini-1.5-pro Audio, images, videos, and text Text Complex reasoning tasks requiring more intelligence
Deprecated
You can view the rate limits for each model on the rate limits page.

Gemini 2.5 Pro
Gemini 2.5 Pro is our state-of-the-art thinking model, capable of reasoning over complex problems in code, math, and STEM, as well as analyzing large datasets, codebases, and documents using long context.

Try in Google AI Studio

Model details
Property Description
Model code gemini-2.5-pro
Supported data types
Inputs

Audio, images, video, text, and PDF

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

65,536

Capabilities
Structured outputs

Supported

Caching

Supported

Function calling

Supported

Code execution

Supported

Search grounding

Supported

Image generation

Not supported

Audio generation

Not supported

Live API

Not supported

Thinking

Supported

Batch Mode

Supported

URL Context

Supported

Versions
Read the model version patterns for more details.
Stable: gemini-2.5-pro
Latest update June 2025
Knowledge cutoff January 2025
Gemini 2.5 Flash
Our best model in terms of price-performance, offering well-rounded capabilities. 2.5 Flash is best for large scale processing, low-latency, high volume tasks that require thinking, and agentic use cases.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-flash
Supported data types
Inputs

Text, images, video, audio

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

65,536

Capabilities
Audio generation

Not supported

Caching

Supported

Code execution

Supported

Function calling

Supported

Image generation

Not supported

Search grounding

Supported

Structured outputs

Supported

Thinking

Supported

Batch Mode

Supported

URL Context

Supported

Versions
Read the model version patterns for more details.
Stable: gemini-2.5-flash
Preview: gemini-2.5-flash-preview-05-20
Latest update June 2025
Knowledge cutoff January 2025
Gemini 2.5 Flash-Lite
A Gemini 2.5 Flash model optimized for cost-efficiency and high throughput.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-flash-lite
Supported data types
Inputs

Text, image, video, audio, PDF

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

65,536

Capabilities
Structured outputs

Supported

Caching

Supported

Function calling

Supported

Code execution

Supported

URL Context

Supported

Search grounding

Supported

Image generation

Not supported

Audio generation

Not supported

Live API

Not supported

Thinking

Supported

Batch mode

Supported

URL Context

Supported

Versions
Read the model version patterns for more details.
Stable: gemini-2.5-flash-lite
Preview: gemini-2.5-flash-lite-06-17
Latest update July 2025
Knowledge cutoff January 2025
Gemini 2.5 Flash Live
The Gemini 2.5 Flash Live model works with the Live API to enable low-latency bidirectional voice and video interactions with Gemini. The model can process text, audio, and video input, and it can provide text and audio output.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-live-2.5-flash-preview
Supported data types
Inputs

Audio, video, and text

Output

Text, and audio

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Capabilities
Structured outputs

Supported

Tuning

Not supported

Function calling

Supported

Code execution

Supported

Search

Supported

Image generation

Not supported

Audio generation

Supported

Thinking

Not supported

Batch Mode

Not supported

URL context

Supported

Versions
Read the model version patterns for more details.
Preview: gemini-live-2.5-flash-preview
Latest update June 2025
Knowledge cutoff January 2025
Gemini 2.5 Flash Native Audio
Our native audio dialog models, with and without thinking, available through the Live API. These models provide interactive and unstructured conversational experiences, with style and control prompting.

Try native audio in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-flash-preview-native-audio-dialog &
models/gemini-2.5-flash-exp-native-audio-thinking-dialog
Supported data types
Inputs

Audio, video, text

Output

Audio and text

Token limits[*]
Input token limit

128,000

Output token limit

8,000

Capabilities
Audio generation

Supported

Caching

Not supported

Code execution

Not supported

Function calling

Supported

Image generation

Not supported

Search grounding

Supported

Structured outputs

Not supported

Thinking

Supported

Batch Mode

Not supported

Tuning

Not supported

Versions
Read the model version patterns for more details.
Preview: gemini-2.5-flash-preview-05-20
Experimental: gemini-2.5-flash-exp-native-audio-thinking-dialog
Latest update May 2025
Knowledge cutoff January 2025
Gemini 2.5 Flash Image Preview
Gemini 2.5 Flash Image Preview is our latest, fastest, and most efficient natively multimodal model that lets you generate and edit images conversationally.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-flash-image-preview
Supported data types
Inputs

Images and text

Output

Images and text

Token limits[*]
Input token limit

32,768

Output token limit

32,768

Capabilities
Structured outputs

Supported

Caching

Supported

Tuning

Not supported

Function calling

Not supported

Code execution

Not Supported

Search

Not Supported

Image generation

Supported

Audio generation

Not supported

Live API

Not Supported

Thinking

Not Supported

Batch Mode

Supported

Versions
Read the model version patterns for more details.
Preview: gemini-2.5-flash-image-preview
Latest update August 2025
Knowledge cutoff June 2025
Gemini 2.5 Flash Preview Text-to-Speech
Gemini 2.5 Flash Preview TTS is our price-performant text-to-speech model, delivering high control and transparency for structured workflows like podcast generation, audiobooks, customer support, and more. Gemini 2.5 Flash rate limits are more restricted since it is an experimental / preview model.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-flash-preview-tts
Supported data types
Inputs

Text

Output

Audio

Token limits[*]
Input token limit

8,000

Output token limit

16,000

Capabilities
Structured outputs

Not supported

Caching

Not supported

Tuning

Not supported

Function calling

Not supported

Code execution

Not supported

Search

Not supported

Audio generation

Supported

Live API

Not supported

Thinking

Not supported

Batch Mode

Supported

Versions
Read the model version patterns for more details.
gemini-2.5-flash-preview-tts
Latest update May 2025
Gemini 2.5 Pro Preview Text-to-Speech
Gemini 2.5 Pro Preview TTS is our most powerful text-to-speech model, delivering high control and transparency for structured workflows like podcast generation, audiobooks, customer support, and more. Gemini 2.5 Pro rate limits are more restricted since it is an experimental / preview model.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.5-pro-preview-tts
Supported data types
Inputs

Text

Output

Audio

Token limits[*]
Input token limit

8,000

Output token limit

16,000

Capabilities
Structured outputs

Not supported

Caching

Not supported

Tuning

Not supported

Function calling

Not supported

Code execution

Not supported

Search

Not supported

Audio generation

Supported

Live API

Not supported

Thinking

Not supported

Batch Mode

Supported

Versions
Read the model version patterns for more details.
gemini-2.5-pro-preview-tts
Latest update May 2025
Gemini 2.0 Flash
Gemini 2.0 Flash delivers next-gen features and improved capabilities, including superior speed, native tool use, and a 1M token context window.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.0-flash
Supported data types
Inputs

Audio, images, video, and text

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Capabilities
Structured outputs

Supported

Caching

Supported

Tuning

Not supported

Function calling

Supported

Code execution

Supported

Search

Supported

Image generation

Not supported

Audio generation

Not supported

Live API

Supported

Thinking

Experimental

Batch Mode

Supported

Versions
Read the model version patterns for more details.
Latest: gemini-2.0-flash
Stable: gemini-2.0-flash-001
Experimental: gemini-2.0-flash-exp
Latest update February 2025
Knowledge cutoff August 2024
Gemini 2.0 Flash Preview Image Generation
Gemini 2.0 Flash Preview Image Generation delivers improved image generation features, including generating and editing images conversationally.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.0-flash-preview-image-generation
Supported data types
Inputs

Audio, images, video, and text

Output

Text and images

Token limits[*]
Input token limit

32,000

Output token limit

8,192

Capabilities
Structured outputs

Supported

Caching

Supported

Tuning

Not supported

Function calling

Not supported

Code execution

Not Supported

Search

Not Supported

Image generation

Supported

Audio generation

Not supported

Live API

Not Supported

Thinking

Not Supported

Batch Mode

Supported

Versions
Read the model version patterns for more details.
Preview: gemini-2.0-flash-preview-image-generation
gemini-2.0-flash-preview-image-generation is not currently supported in a number of countries in Europe, Middle East & Africa

Latest update May 2025
Knowledge cutoff August 2024
Gemini 2.0 Flash-Lite
A Gemini 2.0 Flash model optimized for cost efficiency and low latency.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.0-flash-lite
Supported data types
Inputs

Audio, images, video, and text

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Capabilities
Structured outputs

Supported

Caching

Supported

Tuning

Not supported

Function calling

Supported

Code execution

Not supported

Search

Not supported

Image generation

Not supported

Audio generation

Not supported

Live API

Not supported

Batch API

Supported

Versions
Read the model version patterns for more details.
Latest: gemini-2.0-flash-lite
Stable: gemini-2.0-flash-lite-001
Latest update February 2025
Knowledge cutoff August 2024
Gemini 2.0 Flash Live
The Gemini 2.0 Flash Live model works with the Live API to enable low-latency bidirectional voice and video interactions with Gemini. The model can process text, audio, and video input, and it can provide text and audio output.

Try in Google AI Studio

Model details
Property Description
Model code models/gemini-2.0-flash-live-001
Supported data types
Inputs

Audio, video, and text

Output

Text, and audio

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Capabilities
Structured outputs

Supported

Tuning

Not supported

Function calling

Supported

Code execution

Supported

Search

Supported

Image generation

Not supported

Audio generation

Supported

Thinking

Not supported

Batch Mode

Not supported

URL context

Supported

Versions
Read the model version patterns for more details.
Preview: gemini-2.0-flash-live-001
Latest update April 2025
Knowledge cutoff August 2024
Gemini 1.5 Flash
Gemini 1.5 Flash is a fast and versatile multimodal model for scaling across diverse tasks.

Model details
Property Description
Model code models/gemini-1.5-flash
Supported data types
Inputs

Audio, images, video, and text

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Audio/visual specs
Maximum number of images per prompt

3,600

Maximum video length

1 hour

Maximum audio length

Approximately 9.5 hours

Capabilities
System instructions

Supported

JSON mode

Supported

JSON schema

Supported

Adjustable safety settings

Supported

Caching

Supported

Tuning

Supported

Function calling

Supported

Code execution

Supported

Live API

Not supported

Versions
Read the model version patterns for more details.
Latest: gemini-1.5-flash-latest
Latest stable: gemini-1.5-flash
Stable:
gemini-1.5-flash-001
gemini-1.5-flash-002
Deprecation date September 2025
Latest update September 2024
Gemini 1.5 Flash-8B
Gemini 1.5 Flash-8B is a small model designed for lower intelligence tasks.

Model details
Property Description
Model code models/gemini-1.5-flash-8b
Supported data types
Inputs

Audio, images, video, and text

Output

Text

Token limits[*]
Input token limit

1,048,576

Output token limit

8,192

Audio/visual specs
Maximum number of images per prompt

3,600

Maximum video length

1 hour

Maximum audio length

Approximately 9.5 hours

Capabilities
System instructions

Supported

JSON mode

Supported

JSON schema

Supported

Adjustable safety settings

Supported

Caching

Supported

Tuning

Supported

Function calling

Supported

Code execution

Supported

Live API

Not supported

Versions
Read the model version patterns for more details.
Latest: gemini-1.5-flash-8b-latest
Latest stable: gemini-1.5-flash-8b
Stable:
gemini-1.5-flash-8b-001
Deprecation date September 2025
Latest update October 2024
Gemini 1.5 Pro
Try Gemini 2.5 Pro Preview, our most advanced Gemini model to date.

Gemini 1.5 Pro is a mid-size multimodal model that is optimized for a wide-range of reasoning tasks. 1.5 Pro can process large amounts of data at once, including 2 hours of video, 19 hours of audio, codebases with 60,000 lines of code, or 2,000 pages of text.

Model details
Property Description
Model code models/gemini-1.5-pro
Supported data types
Inputs

Audio, images, video, and text

Output

Text

Token limits[*]
Input token limit

2,097,152

Output token limit

8,192

Audio/visual specs
Maximum number of images per prompt

7,200

Maximum video length

2 hours

Maximum audio length

Approximately 19 hours

Capabilities
System instructions

Supported

JSON mode

Supported

JSON schema

Supported

Adjustable safety settings

Supported

Caching

Supported

Tuning

Not supported

Function calling

Supported

Code execution

Supported

Live API

Not supported

Versions
Read the model version patterns for more details.
Latest: gemini-1.5-pro-latest
Latest stable: gemini-1.5-pro
Stable:
gemini-1.5-pro-001
gemini-1.5-pro-002
Deprecation date September 2025
Latest update September 2024
See the examples to explore the capabilities of these model variations.

[*] A token is equivalent to about 4 characters for Gemini models. 100 tokens are about 60-80 English words.

Model version name patterns
Gemini models are available in either stable, preview, or experimental versions. In your code, you can use one of the following model name formats to specify which model and version you want to use.

Latest stable
Points to the most recent stable version released for the specified model generation and variation.

To specify the latest stable version, use the following pattern: <model>-<generation>-<variation>. For example, gemini-2.0-flash.

Stable
Points to a specific stable model. Stable models usually don't change. Most production apps should use a specific stable model.

To specify a stable version, use the following pattern: <model>-<generation>-<variation>-<version>. For example, gemini-2.0-flash-001.

Preview
Points to a preview model which may not be suitable for production use, come with more restrictive rate limits, but may have billing enabled.

To specify a preview version, use the following pattern: <model>-<generation>-<variation>-<version>. For example, gemini-2.5-pro-preview-06-05.

Preview models are not stable and availability of model endpoints is subject to change.

Experimental
Points to an experimental model which may not be suitable for production use and come with more restrictive rate limits. We release experimental models to gather feedback and get our latest updates into the hands of developers quickly.

To specify an experimental version, use the following pattern: <model>-<generation>-<variation>-<version>. For example, gemini-2.0-pro-exp-02-05.

Experimental models are not stable and availability of model endpoints is subject to change.

Experimental models
In addition to stable models, the Gemini API offers experimental models which may not be suitable for production use and come with more restrictive rate limits.

We release experimental models to gather feedback, get our latest updates into the hands of developers quickly, and highlight the pace of innovation happening at Google. What we learn from experimental launches informs how we release models more widely. An experimental model can be swapped for another without prior notice. We don't guarantee that an experimental model will become a stable model in the future.

Previous experimental models
As new versions or stable releases become available, we remove and replace experimental models. You can find the previous experimental models we released in the following section along with the replacement version:

Model code Base model Replacement version
gemini-embedding-exp-03-07 Gemini Embedding gemini-embedding-001
gemini-2.5-flash-preview-04-17 Gemini 2.5 Flash gemini-2.5-flash-preview-05-20
gemini-2.0-flash-exp-image-generation Gemini 2.0 Flash gemini-2.0-flash-preview-image-generation
gemini-2.5-pro-preview-06-05 Gemini 2.5 Pro gemini-2.5-pro
gemini-2.5-pro-preview-05-06 Gemini 2.5 Pro gemini-2.5-pro
gemini-2.5-pro-preview-03-25 Gemini 2.5 Pro gemini-2.5-pro
gemini-2.0-flash-thinking-exp-01-21 Gemini 2.5 Flash gemini-2.5-flash-preview-04-17
gemini-2.0-pro-exp-02-05 Gemini 2.0 Pro Experimental gemini-2.5-pro-preview-03-25
gemini-2.0-flash-exp Gemini 2.0 Flash gemini-2.0-flash
gemini-exp-1206 Gemini 2.0 Pro gemini-2.0-pro-exp-02-05
gemini-2.0-flash-thinking-exp-1219 Gemini 2.0 Flash Thinking gemini-2.0-flash-thinking-exp-01-21
gemini-exp-1121 Gemini gemini-exp-1206
gemini-exp-1114 Gemini gemini-exp-1206
gemini-1.5-pro-exp-0827 Gemini 1.5 Pro gemini-exp-1206
gemini-1.5-pro-exp-0801 Gemini 1.5 Pro gemini-exp-1206
gemini-1.5-flash-8b-exp-0924 Gemini 1.5 Flash-8B gemini-1.5-flash-8b
gemini-1.5-flash-8b-exp-0827 Gemini 1.5 Flash-8B gemini-1.5-flash-8b
Supported languages
Gemini models are trained to work with the following languages:

Arabic (ar)
Bengali (bn)
Bulgarian (bg)
Chinese simplified and traditional (zh)
Croatian (hr)
Czech (cs)
Danish (da)
Dutch (nl)
English (en)
Estonian (et)
Finnish (fi)
French (fr)
German (de)
Greek (el)
Hebrew (iw)
Hindi (hi)
Hungarian (hu)
Indonesian (id)
Italian (it)
Japanese (ja)
Korean (ko)
Latvian (lv)
Lithuanian (lt)
Norwegian (no)
Polish (pl)
Portuguese (pt)
Romanian (ro)
Russian (ru)
Serbian (sr)
Slovak (sk)
Slovenian (sl)
Spanish (es)
Swahili (sw)
Swedish (sv)
Thai (th)
Turkish (tr)
Ukrainian (uk)
Vietnamese (vi)
Was this helpful?

Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2025-09-02 UTC.

Terms
Privacy

English
