# utils/audio_utils.py
import io
import uuid
import numpy as np
import soundfile as sf
from pathlib import Path
import librosa

class AudioUtils:
    @staticmethod
    def save_audio(audio_data: bytes, text_preview: str = "") -> str:
        """
        Generate a unique filename for the audio file
        
        Args:
            audio_data: Audio data as bytes
            text_preview: Preview of the text for filename generation
        
        Returns:
            Generated filename
        """
        # Create safe filename from text preview
        safe_text = "".join(c for c in text_preview if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_text = safe_text[:30]  # Limit length
        
        # Generate unique identifier
        unique_id = str(uuid.uuid4())[:8]
        
        # Create filename
        if safe_text:
            filename = f"echoverse_{safe_text}_{unique_id}.wav"
        else:
            filename = f"echoverse_{unique_id}.wav"
        
        # Clean filename
        filename = filename.replace(" ", "_")
        
        return filename
    
    @staticmethod
    def convert_to_mp3(audio_data: bytes) -> bytes:
        """
        Convert audio to MP3 format (placeholder - requires additional libraries)
        
        Args:
            audio_data: Input audio data
        
        Returns:
            MP3 audio data
        """
        # For now, return the original data
        # In production, you would use pydub or similar library
        return audio_data
    
    @staticmethod
    def get_audio_duration(audio_data: bytes) -> float:
        """
        Get duration of audio in seconds
        
        Args:
            audio_data: Audio data as bytes
        
        Returns:
            Duration in seconds
        """
        try:
            buffer = io.BytesIO(audio_data)
            audio, sample_rate = sf.read(buffer)
            return len(audio) / sample_rate
        except Exception:
            return 0.0
    
    @staticmethod
    def validate_audio_format(audio_data: bytes) -> bool:
        """
        Validate if audio data is in correct format
        
        Args:
            audio_data: Audio data to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            buffer = io.BytesIO(audio_data)
            sf.read(buffer)
            return True
        except Exception:
            return False

    @staticmethod
    def adjust_speed(audio_data: bytes, speed: float) -> bytes:
        """
        Adjust the speed of audio data without changing pitch
        
        Args:
            audio_data: Input audio data as bytes
            speed: Speed factor (0.5 = half speed, 2.0 = double speed)
        
        Returns:
            Speed-adjusted audio data as bytes
        """
        try:
            # Load audio from bytes
            buffer = io.BytesIO(audio_data)
            audio, sample_rate = sf.read(buffer)
            
            # Adjust speed using librosa
            audio_stretched = librosa.effects.time_stretch(audio, rate=speed)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(output_buffer, audio_stretched, sample_rate, format='WAV')
            output_buffer.seek(0)
            
            return output_buffer.read()
        except Exception as e:
            print(f"Error adjusting audio speed: {e}")
            # Fallback: return original audio if adjustment fails
            return audio_data