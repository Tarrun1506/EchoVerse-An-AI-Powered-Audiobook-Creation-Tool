# models/tts_generator.py
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import numpy as np
import soundfile as sf
import io
import os
from datasets import load_dataset
from huggingface_hub import hf_hub_download
import zipfile
from dotenv import load_dotenv

load_dotenv()

class TTSGenerator:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self._initialize_model()
        
    def _initialize_model(self):
        try:
            model_name = "microsoft/speecht5_tts"
            self.processor = SpeechT5Processor.from_pretrained(model_name)
            self.model = SpeechT5ForTextToSpeech.from_pretrained(model_name)
            self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
            # Load speaker embeddings for both male and female voices
            self.speaker_embeddings = self._load_speaker_embeddings()
        except Exception as e:
            print(f"Error initializing SpeechT5 model: {e}")
            raise
    
    def _load_speaker_embeddings(self) -> dict:
        """Load speaker embeddings for both male and female voices."""
        embeddings = {}
        
        try:
            # Try to load from the dataset
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            
            # Select different speakers for male and female voices
            # These indices are examples - you might need to adjust based on the dataset
            embeddings['male'] = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
            embeddings['female'] = torch.tensor(embeddings_dataset[9000]["xvector"]).unsqueeze(0)
            
        except Exception:
            try:
                # Fallback: download the zip and extract embeddings
                zip_path = hf_hub_download(
                    repo_id="Matthijs/cmu-arctic-xvectors",
                    filename="spkrec-xvect.zip",
                    repo_type="dataset",
                )
                
                with zipfile.ZipFile(zip_path, "r") as zf:
                    npy_files = sorted([name for name in zf.namelist() if name.endswith(".npy")])
                    
                    # Use different files for male and female voices
                    male_index = 7306 if len(npy_files) > 7306 else 0
                    female_index = 9000 if len(npy_files) > 9000 else (1 if len(npy_files) > 1 else 0)
                    
                    # Load male voice embedding
                    data = zf.read(npy_files[male_index])
                    male_xvector = np.load(io.BytesIO(data))
                    embeddings['male'] = torch.tensor(male_xvector).unsqueeze(0)
                    
                    # Load female voice embedding
                    data = zf.read(npy_files[female_index])
                    female_xvector = np.load(io.BytesIO(data))
                    embeddings['female'] = torch.tensor(female_xvector).unsqueeze(0)
                    
            except Exception as inner_e:
                print(f"Falling back to random speaker embeddings due to error: {inner_e}")
                # Final fallback: random embeddings with correct dimension
                embeddings['male'] = torch.randn(1, 512)
                embeddings['female'] = torch.randn(1, 512)
        
        return embeddings
        
    def generate_speech(self, text: str, voice_model: str = "microsoft/speecht5_tts", 
                       voice_gender: str = "female", speed: float = 1.0) -> bytes:
        try:
            if len(text) > 1000:
                text = text[:1000] + "..."
                
            inputs = self.processor(text=text, return_tensors="pt")
            
            # Get the appropriate speaker embedding based on gender
            speaker_embedding = self.speaker_embeddings.get(voice_gender, self.speaker_embeddings['female'])
            
            speech = self.model.generate_speech(
                inputs["input_ids"], 
                speaker_embedding, 
                vocoder=self.vocoder
            )
            
            speech = speech.numpy()
            return self._audio_to_bytes(speech, sample_rate=16000)
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return self._generate_fallback(text)
        
    def _audio_to_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        if audio.dtype != np.int16:
            audio = (audio * 32767).astype(np.int16)
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()
    
    def _generate_fallback(self, text: str) -> bytes:
        duration = len(text) * 0.1
        sample_rate = 16000
        samples = int(duration * sample_rate)
        t = np.linspace(0, duration, samples)
        audio = 0.1 * np.sin(2 * np.pi * 440 * t)
        return self._audio_to_bytes(audio, sample_rate)