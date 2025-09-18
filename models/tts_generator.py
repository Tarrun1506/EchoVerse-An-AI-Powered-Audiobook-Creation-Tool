from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import numpy as np
import soundfile as sf
import io
import os
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

class TTSGenerator:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self._initialize_model()
        self._load_speaker_embeddings()
        
    def _initialize_model(self):
        """Initialize SpeechT5 model components"""
        try:
            model_name = "microsoft/speecht5_tts"
            self.processor = SpeechT5Processor.from_pretrained(model_name)
            self.model = SpeechT5ForTextToSpeech.from_pretrained(model_name)
            self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        except Exception as e:
            print(f"Error initializing SpeechT5 model: {e}")
            raise
    
    def _load_speaker_embeddings(self):
        """Load different speaker embeddings for voice variety"""
        try:
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            
            # Define speaker embeddings for different voices
            # Based on CMU ARCTIC dataset speakers: bdl (US male), slt (US female), 
            # jmk (Canadian male), awb (Scottish male), rms (US male), clb (US female), ksp (Indian male)
            self.speaker_embeddings = {
                7306: torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0),  # Female - US (slt)
                5000: torch.tensor(embeddings_dataset[5000]["xvector"]).unsqueeze(0),  # Female - UK style
                1234: torch.tensor(embeddings_dataset[1234]["xvector"]).unsqueeze(0),  # Male - US (bdl)
                3000: torch.tensor(embeddings_dataset[3000]["xvector"]).unsqueeze(0),  # Male - Scottish (awb)
            }
        except Exception as e:
            print(f"Error loading speaker embeddings: {e}")
            # Fallback to default embedding
            self.speaker_embeddings = {
                7306: torch.randn(1, 512),  # Default female
                1234: torch.randn(1, 512),  # Default male
            }
    
    def generate_speech(self, text: str, voice_embedding_id: int = 7306, speed: float = 1.0) -> bytes:
        """
        Generate speech using specified voice embedding
        
        Args:
            text: Text to convert to speech
            voice_embedding_id: ID of the voice embedding to use
            speed: Audio playback speed multiplier
        
        Returns:
            Audio data as bytes
        """
        try:
            # Truncate text if too long
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            # Get speaker embedding
            speaker_embedding = self.speaker_embeddings.get(voice_embedding_id, self.speaker_embeddings[7306])
            
            # Process input
            inputs = self.processor(text=text, return_tensors="pt")
            
            # Generate speech
            speech = self.model.generate_speech(
                inputs["input_ids"], 
                speaker_embedding, 
                vocoder=self.vocoder
            )
            
            # Apply speed modification
            if speed != 1.0:
                speech = self._modify_speed(speech.numpy(), speed)
            else:
                speech = speech.numpy()
            
            return self._audio_to_bytes(speech, sample_rate=16000)
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return self._generate_fallback(text)
    
    def _modify_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Modify audio playback speed"""
        try:
            import librosa
            return librosa.effects.time_stretch(audio, rate=speed)
        except ImportError:
            # Simple resampling if librosa not available
            indices = np.round(np.arange(0, len(audio), speed)).astype(int)
            indices = indices[indices < len(audio)]
            return audio[indices]
    
    def _audio_to_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        """Convert audio array to bytes"""
        # Ensure audio is in the right format
        if audio.dtype != np.int16:
            audio = (audio * 32767).astype(np.int16)
        
        # Create bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()
    
    def _generate_fallback(self, text: str) -> bytes:
        """Generate a simple fallback audio"""
        duration = len(text) * 0.1
        sample_rate = 16000
        samples = int(duration * sample_rate)
        t = np.linspace(0, duration, samples)
        audio = 0.1 * np.sin(2 * np.pi * 440 * t)
        return self._audio_to_bytes(audio, sample_rate)
    
    def get_available_voices(self):
        """Return information about available voices"""
        return {
            7306: {"name": "Emma", "gender": "female", "accent": "US", "description": "Clear, professional female voice"},
            5000: {"name": "Sarah", "gender": "female", "accent": "UK", "description": "Elegant British female voice"},
            1234: {"name": "James", "gender": "male", "accent": "US", "description": "Deep, authoritative male voice"},
            3000: {"name": "David", "gender": "male", "accent": "Scottish", "description": "Rich Scottish male voice"}
        }
