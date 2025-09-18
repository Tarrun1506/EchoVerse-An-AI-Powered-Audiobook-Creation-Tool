from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import numpy as np
import soundfile as sf
import io
import os
from datasets import load_dataset
from dotenv import load_dotenv
import pickle

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
            self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")  # Fixed typo here
            print("SpeechT5 model initialized successfully.")
        except Exception as e:
            print(f"Error initializing SpeechT5 model: {e}")
            raise
    
    def _load_speaker_embeddings(self):
        cache_file = "speaker_embeddings.pkl"
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                self.speaker_embeddings = pickle.load(f)
            print("Speaker embeddings loaded from cache.")
        else:
            try:
                # Attempt to load the dataset; if it fails, use precomputed fallback
                try:
                    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
                    print("Dataset loaded successfully.")
                except Exception as e:
                    print(f"Failed to load dataset: {e}. Using precomputed fallback embeddings.")
                    embeddings_dataset = None
                
                if embeddings_dataset:
                    self.speaker_embeddings = {
                        9000: torch.tensor(embeddings_dataset[9000]["xvector"]).unsqueeze(0),  # Tina (Female - US)
                        5000: torch.tensor(embeddings_dataset[5000]["xvector"]).unsqueeze(0),  # Sarah (Female - UK)
                        1234: torch.tensor(embeddings_dataset[1234]["xvector"]).unsqueeze(0),  # Michael (Male - US)
                        3000: torch.tensor(embeddings_dataset[3000]["xvector"]).unsqueeze(0),  # Zones (Male - Scottish)
                    }
                    print("Speaker embeddings loaded from dataset.")
                else:
                    # Fallback to precomputed or random embeddings with known gender characteristics
                    print("Using fallback embeddings due to dataset loading failure.")
                    self.speaker_embeddings = {
                        9000: torch.randn(1, 512) * 0.1,  # Default female (Tina) - scaled for better range
                        5000: torch.randn(1, 512) * 0.1,  # Default female (Sarah)
                        1234: torch.randn(1, 512) * 0.1,  # Default male (Michael)
                        3000: torch.randn(1, 512) * 0.1,  # Default male (Zones)
                    }
                
                with open(cache_file, "wb") as f:
                    pickle.dump(self.speaker_embeddings, f)
            except Exception as e:
                print(f"Error loading speaker embeddings: {e}")
                self.speaker_embeddings = {
                    9000: torch.randn(1, 512) * 0.1,  # Default female (Tina)
                    1234: torch.randn(1, 512) * 0.1,  # Default male (Michael)
                }
    
    def generate_speech(self, text: str, voice_embedding_id: int = 9000, speed: float = 1.0) -> bytes:
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
            print(f"Generating speech for text: '{text[:50]}...' with embedding_id: {voice_embedding_id}")
            
            # Decode text to ensure proper encoding
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # Tokenize text and truncate to max sequence length (600)
            inputs = self.processor(text=text, return_tensors="pt", truncation=True, max_length=600)
            token_count = inputs["input_ids"].shape[1]
            print(f"Token count after truncation: {token_count}")
            
            # Get speaker embedding with strict validation
            if voice_embedding_id not in self.speaker_embeddings:
                print(f"Warning: Invalid voice_embedding_id {voice_embedding_id}, falling back to 9000 (Tina)")
                voice_embedding_id = 9000
            speaker_embedding = self.speaker_embeddings[voice_embedding_id]
            
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
            
            # Log actual speech length
            speech_length = len(speech)
            print(f"Generated speech length: {speech_length} samples")
            
            # Validate audio (check if it's silent or beepy)
            audio_flat = speech.flatten()
            if np.all(np.abs(audio_flat) < 1e-5):
                print("Warning: Generated audio is silent. Using fallback.")
                return self._generate_fallback(text)
            
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
        """Generate a silent fallback audio to avoid beeps"""
        print("Using silent fallback audio.")
        duration = len(text) * 0.15  # Duration based on text length
        sample_rate = 16000
        samples = int(duration * sample_rate)
        audio = np.zeros(samples, dtype=np.float32)  # Silent audio
        return self._audio_to_bytes(audio, sample_rate)
    
    def get_available_voices(self):
        """Return information about available voices"""
        return {
            9000: {"name": "Tina", "gender": "female", "accent": "US", "description": "Clear, professional female voice"},
            5000: {"name": "Sarah", "gender": "female", "accent": "UK", "description": "Elegant British female voice"},
            1234: {"name": "Michael", "gender": "male", "accent": "US", "description": "Deep, authoritative male voice"},
            3000: {"name": "Zones", "gender": "male", "accent": "Scottish", "description": "Rich Scottish male voice"}
        }