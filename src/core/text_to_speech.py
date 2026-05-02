"""
Text-to-Speech Module for Part 2
Chuyển đổi text thành audio để người dùng nghe
"""

from typing import Optional
import os
import io
import wave
import tempfile

class TextToSpeechGenerator:
    """Generate speech audio từ text"""
    
    def __init__(self, provider: str = "pyttsx3"):
        """
        Initialize TTS provider
        
        Args:
            provider: 'pyttsx3' (offline), 'google', hoặc 'azure'
        """
        self.provider = provider
        self.engine = None
        
        if provider == "pyttsx3":
            self._init_pyttsx3()
    
    def _init_pyttsx3(self) -> None:
        """Initialize pyttsx3 (offline, không cần API key)"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            # Set properties - faster speech for quicker generation
            self.engine.setProperty('rate', 150)  # Speed (150 is reasonable for clarity)
            self.engine.setProperty('volume', 0.9)  # Volume
            print("✓ pyttsx3 TTS initialized")
        except Exception as e:
            print(f"⚠ pyttsx3 initialization failed: {e}")
            raise
    
    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text để chuyển thành speech
            output_file: Nếu None, return bytes; nếu có path, save file
        
        Returns:
            Audio data as bytes (nếu output_file is None)
        """
        if self.provider == "pyttsx3":
            return self._tts_pyttsx3(text, output_file)
    
    def _tts_pyttsx3(self, text: str, output_file: Optional[str]) -> bytes:
        """Generate speech using pyttsx3"""
        if output_file is None:
            # Save to temporary file, then read as bytes
            # Use tempfile for cross-platform compatibility
            fd, temp_file = tempfile.mkstemp(suffix='.wav', text=False)
            os.close(fd)  # Close the file descriptor
            
            try:
                self.engine.save_to_file(text, temp_file)
                self.engine.runAndWait()
                
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
                
                return audio_data
            finally:
                # Ensure cleanup
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        else:
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            return ""