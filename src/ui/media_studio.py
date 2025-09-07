"""
Media studio interface for image and video generation.
"""

import streamlit as st
import json
from config.settings import AppSettings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Constants for error handling
MEDIA_ERROR_KEYWORDS = ["MediaFileStorageError", "Bad filename"]

class MediaStudioInterface:
    """Media generation interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        
    def render(self):
        """Render the media studio interface."""
        
        st.markdown("# 🎨 Media Studio")
        st.markdown("Generate images and videos using AI models.")
        
        # Media type selection
        media_type = st.radio(
            "Select Media Type",
            ["🖼️ Image Generation", "🎬 Video Generation"],
            horizontal=True
        )
        
        if media_type == "🖼️ Image Generation":
            self._render_image_generation()
        else:
            self._render_video_generation()
    
    def _render_image_generation(self):
        """Render image generation interface."""
        
        st.markdown("## 🖼️ Image Generation")
        
        # Get JSON config
        json_config = getattr(self.settings, '_json_config', {})
        media_config = json_config.get('media', {})
        
        # Image generation settings
        try:
            current_settings = json.loads(media_config.get('image_generation_settings', '{}'))
        except:
            current_settings = {}
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Prompt input
            prompt = st.text_area(
                "🎨 Image Prompt",
                placeholder="A beautiful sunset over mountains with vibrant colors...",
                height=100,
                help="Describe the image you want to generate"
            )
            
            # Advanced settings
            with st.expander("⚙️ Advanced Settings", expanded=False):
                
                col1_adv, col2_adv = st.columns(2)
                
                with col1_adv:
                    model = st.selectbox(
                        "Model",
                        ["imagen-4.0-fast-generate-001", "imagen-4.0-generate-001", "imagen-4.0-ultra-generate-001"],
                        index=0
                    )
                    
                    num_images = st.slider(
                        "Number of Images",
                        min_value=1,
                        max_value=4,
                        value=current_settings.get('number_of_images', 1)
                    )
                
                with col2_adv:
                    aspect_ratio = st.selectbox(
                        "Aspect Ratio",
                        ["1:1", "3:4", "4:3", "9:16", "16:9"],
                        index=0
                    )
                    
                    person_generation = st.selectbox(
                        "Person Generation",
                        ["ALLOW_ADULT", "DONT_ALLOW", "ALLOW_ALL"],
                        index=0
                    )
        
        with col2:
            # Model info
            st.markdown("### 📊 Model Info")
            
            model_info = {
                "imagen-4.0-fast-generate-001": {"name": "Imagen 4.0 Fast", "cost": "$0.02/image", "speed": "Fast"},
                "imagen-4.0-generate-001": {"name": "Imagen 4.0 Standard", "cost": "$0.04/image", "speed": "Medium"},
                "imagen-4.0-ultra-generate-001": {"name": "Imagen 4.0 Ultra", "cost": "$0.06/image", "speed": "Slow"}
            }
            
            info = model_info.get(model, {})
            st.info(f"**{info.get('name', 'Unknown')}**")
            st.caption(f"💰 Cost: {info.get('cost', 'Unknown')}")
            st.caption(f"⚡ Speed: {info.get('speed', 'Unknown')}")
            
            # Estimated cost
            estimated_cost = num_images * float(info.get('cost', '$0.02/image').replace('$', '').replace('/image', ''))
            st.warning(f"💰 Estimated Cost: ${estimated_cost:.2f}")
        
        # Generate button
        if st.button("🎨 Generate Images", type="primary", disabled=not prompt):
            if prompt:
                with st.spinner("🎨 Generating images..."):
                    # Mock image generation
                    import time
                    time.sleep(3)
                    
                    st.success(f"✅ Generated {num_images} image(s)!")
                    
                    # Mock display of generated images
                    for i in range(num_images):
                        st.image(
                            "https://via.placeholder.com/512x512/FF6B6B/FFFFFF?text=Generated+Image+" + str(i+1),
                            caption=f"Generated Image {i+1}",
                            width=200
                        )
                    
                    st.info("🔄 In a real implementation, this would use Google's Imagen models to generate actual images.")
        
        # Generated images history
        st.markdown("---")
        st.markdown("### 📁 Recent Generations")
        
        generated_images = json_config.get('media', {}).get('generated_images', [])
        
        if generated_images:
            st.info(f"Found {len(generated_images)} previously generated images")
        else:
            st.info("No images generated yet. Create your first image above!")
    
    def _render_video_generation(self):
        """Render video generation interface."""
        
        st.markdown("## 🎬 Video Generation")
        
        st.warning("⚠️ **Important:** Video generation can be expensive ($0.15-$0.40 per second). Check pricing before proceeding.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Video prompt
            prompt = st.text_area(
                "🎬 Video Prompt",
                placeholder="A cat playing with a ball of yarn in slow motion...",
                height=100,
                help="Describe the video you want to generate"
            )
            
            # Video settings
            with st.expander("⚙️ Video Settings", expanded=True):
                
                col1_vid, col2_vid = st.columns(2)
                
                with col1_vid:
                    model = st.selectbox(
                        "Model",
                        ["veo-3.0-fast-generate-preview", "veo-3.0-generate-preview"],
                        index=0
                    )
                    
                    duration = st.slider(
                        "Duration (seconds)",
                        min_value=5,
                        max_value=8,
                        value=8
                    )
                
                with col2_vid:
                    aspect_ratio = st.selectbox(
                        "Aspect Ratio",
                        ["16:9", "9:16"],
                        index=0
                    )
                    
                    person_generation = st.selectbox(
                        "Person Generation",
                        ["dont_allow", "allow_adult"],
                        index=0
                    )
            
            # Optional image input
            try:
                uploaded_image = st.file_uploader(
                    "🖼️ Starting Image (Optional)",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload an image to use as the first frame"
                )
                
                if uploaded_image:
                    st.info(f"📎 Image uploaded: {uploaded_image.name}")
            except Exception as e:
                if any(keyword in str(e) for keyword in MEDIA_ERROR_KEYWORDS):
                    st.warning("⚠️ Previous image no longer available. Please upload a new one.")
                    logger.warning(f"Media file error in image upload: {str(e)}")
                    uploaded_image = None
                else:
                    st.error(f"Error with image upload: {str(e)}")
                    logger.error(f"Error in image upload: {str(e)}")
                    uploaded_image = None
        
        with col2:
            # Model info
            st.markdown("### 📊 Model Info")
            
            model_info = {
                "veo-3.0-fast-generate-preview": {"name": "Veo 3.0 Fast", "cost": "$0.15/second", "speed": "Fast"},
                "veo-3.0-generate-preview": {"name": "Veo 3.0 Standard", "cost": "$0.40/second", "speed": "Slow"}
            }
            
            info = model_info.get(model, {})
            st.info(f"**{info.get('name', 'Unknown')}**")
            st.caption(f"💰 Cost: {info.get('cost', 'Unknown')}")
            st.caption(f"⚡ Speed: {info.get('speed', 'Unknown')}")
            
            # Estimated cost
            cost_per_second = float(info.get('cost', '$0.15/second').replace('$', '').replace('/second', ''))
            estimated_cost = duration * cost_per_second
            
            st.error(f"💰 **Estimated Cost: ${estimated_cost:.2f}**")
            
            # Duration info
            st.warning(f"📹 Video Length: {duration} seconds")
        
        # Generate button
        if st.button("🎬 Generate Video", type="primary", disabled=not prompt):
            if prompt:
                # Cost confirmation
                if estimated_cost > 2.0:
                    st.error(f"⚠️ High cost detected: ${estimated_cost:.2f}")
                    if not st.checkbox("I understand the cost and want to proceed"):
                        st.stop()
                
                with st.spinner("🎬 Generating video... This may take several minutes."):
                    # Mock video generation
                    import time
                    time.sleep(5)
                    
                    st.success(f"✅ Generated {duration}-second video!")
                    
                    # Mock video display
                    st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
                    
                    st.info("🔄 In a real implementation, this would use Google's Veo models to generate actual videos.")
        
        # Generated videos history
        st.markdown("---")
        st.markdown("### 📁 Recent Generations")
        
        json_config = getattr(self.settings, '_json_config', {})
        generated_videos = json_config.get('media', {}).get('generated_videos', [])
        
        if generated_videos:
            st.info(f"Found {len(generated_videos)} previously generated videos")
        else:
            st.info("No videos generated yet. Create your first video above!")
