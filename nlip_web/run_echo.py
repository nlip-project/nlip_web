from __future__ import annotations
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from nlip_web.genai import StatefulGenAI
from nlip_web.env import read_digits, read_string
import base64
import json

# Store chat sessions
sessions = {}

class NLIPMessage(BaseModel):
    messagetype: str
    format: str
    subformat: Optional[str] = None
    content: str
    label: Optional[str] = None
    submessages: Optional[List[dict]] = None
    session_id: Optional[str] = "default"
    images: Optional[List[str]] = None  # Base64 encoded images
    audio: Optional[List[str]] = None   # Base64 encoded audio
    files: Optional[List[dict]] = None  # Other file attachments
    audio_metadata: Optional[List[dict]] = None  # Audio file metadata

def build() -> FastAPI:
    app = FastAPI(title="NLIP Chat", version="0.1.0")
    
    # Read configuration
    model = read_string("CHAT_MODEL", "llama3.2:3b")
    host = read_string("CHAT_HOST", "localhost")
    port = read_digits("CHAT_PORT", 11434)
    
    # Serve /static from repo's static/ dir
    project_root = Path(__file__).resolve().parent.parent
    static_dir = project_root / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/")
    def home():
        return RedirectResponse(url="/static/index.html")
    
    @app.post("/nlip/")
    async def nlip_endpoint(msg: NLIPMessage):
        session_id = msg.session_id or "default"
        
        # Create session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = StatefulGenAI(host, port, model)
        
        chat_server = sessions[session_id]
        
        # Debug logging
        print(f"Received message: content='{msg.content}', images={len(msg.images) if msg.images else 0}, audio={len(msg.audio) if msg.audio else 0}, files={len(msg.files) if msg.files else 0}")
        
        # Handle multimodal content
        if msg.images and len(msg.images) > 0:
            # Process images with vision model
            try:
                # Use the vision model for image processing
                vision_model = "llava:7b"  # You have this installed!
                vision_server = StatefulGenAI(host, port, vision_model)
                
                # Process each image
                image_descriptions = []
                for i, image_data in enumerate(msg.images):
                    # Remove data URL prefix if present
                    if image_data.startswith('data:'):
                        image_data = image_data.split(',')[1]
                    
                    # Use the vision model to describe the image
                    vision_prompt = f"Describe this image in detail. What do you see?"
                    image_desc = vision_server.server.generate_with_image(vision_prompt, [image_data])
                    image_descriptions.append(f"Image {i+1}: {image_desc}")
                
                # Combine user text with image descriptions
                enhanced_content = f"{msg.content}\n\nImage Analysis:\n" + "\n".join(image_descriptions)
                response = chat_server.chat(enhanced_content)
            except Exception as e:
                # Fallback to text-only if vision processing fails
                enhanced_content = f"{msg.content}\n\n[Note: {len(msg.images)} image(s) were received but vision processing failed: {str(e)}]"
                response = chat_server.chat(enhanced_content)
        elif msg.audio and len(msg.audio) > 0:
            # Process audio files
            try:
                # Check file size to prevent timeouts (limit to 5MB)
                total_size = sum(len(audio_data) for audio_data in msg.audio)
                if total_size > 5 * 1024 * 1024:  # 5MB limit
                    enhanced_content = f"{msg.content}\n\n[Note: Audio file too large ({total_size//1024//1024}MB). Please use files under 5MB for processing.]"
                else:
                    # Provide intelligent analysis based on the audio file metadata
                    audio_files_info = []
                    if msg.audio_metadata:
                        for audio_meta in msg.audio_metadata:
                            duration_estimate = "unknown duration"
                            if audio_meta.get('size', 0) > 0:
                                # Rough estimate: 1MB ≈ 1 minute for typical audio
                                estimated_minutes = (audio_meta['size'] / (1024 * 1024)) * 1.0
                                duration_estimate = f"~{estimated_minutes:.1f} minutes"
                            
                            audio_files_info.append(f"- **{audio_meta.get('name', 'Unknown')}**: {audio_meta.get('size', 0)//1024}KB, {duration_estimate}")
                    
                    audio_info = f"Audio file received: {len(msg.audio)} file(s), total size: {total_size//1024}KB"
                    
                    # Create a more intelligent prompt for the AI
                    enhanced_content = f"""I've received an audio file for analysis. Here's what I can tell you about it:

{audio_info}

**File Details:**
{chr(10).join(audio_files_info) if audio_files_info else "No metadata available"}

Since I can't directly process the audio content, I can help you analyze it in other ways:

1. **File Analysis**: The audio file appears to be {total_size//1024}KB in size, which suggests it's a {'short clip' if total_size < 500*1024 else 'medium-length recording' if total_size < 2*1024*1024 else 'longer recording'}.

2. **Content Prediction**: Based on the file size and format, this could be:
   - Music (if it's a song or instrumental piece)
   - Speech (conversation, lecture, or podcast)
   - Sound effects or ambient audio
   - A mix of different audio types

3. **Analysis Questions**: To help you better, could you tell me:
   - What type of audio content is this?
   - What are you hoping to learn from it?
   - Is there something specific you'd like me to help you understand about the audio?

Please provide more context about what you'd like me to analyze, and I'll do my best to help you understand the audio content!"""
                    
                response = chat_server.chat(enhanced_content)
            except Exception as e:
                enhanced_content = f"{msg.content}\n\n[Note: {len(msg.audio)} audio file(s) were received but processing failed: {str(e)}]"
                response = chat_server.chat(enhanced_content)
        elif msg.files and len(msg.files) > 0:
            # For now, we'll just mention that files were received
            enhanced_content = f"{msg.content}\n\n[Note: {len(msg.files)} file(s) were attached but cannot be processed in this demo version]"
            response = chat_server.chat(enhanced_content)
        else:
            # Regular text chat
            response = chat_server.chat(msg.content)
        
        # Ensure we always return a response
        if not response:
            response = "I received your message but couldn't generate a response. Please try again."
        
        print(f"Returning response: {response[:100]}...")
        
        return {
            "messagetype": "text",
            "format": "text",
            "content": response
        }
    
    return app