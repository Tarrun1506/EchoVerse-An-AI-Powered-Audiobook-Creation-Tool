# app.py (updated)
import streamlit as st
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from models.text_rewriter import TextRewriter
from models.tts_generator import TTSGenerator
from utils.audio_utils import AudioUtils
from utils.session_manager import SessionManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="EchoVerse - AI Audiobook Creator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a professional look
def load_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .section-header {
        color: #495057;
        font-size: 1.6rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
        position: relative;
    }
    
    .section-header:after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #6e8efb, #a777e3);
    }
    
    .audio-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    
    .text-comparison {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
    }
    
    .text-comparison:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
        padding: 1.5rem 1rem;
    }
    
    .stSelectbox, .stSlider, .stRadio {
        margin-bottom: 1.5rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(106, 142, 251, 0.4);
    }
    
    .history-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #6e8efb;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #6e8efb;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .progress-bar {
        height: 8px;
        border-radius: 4px;
        background: #e9ecef;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6e8efb, #a777e3);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'narrations' not in st.session_state:
        st.session_state.narrations = []
    if 'text_rewriter' not in st.session_state:
        st.session_state.text_rewriter = TextRewriter()
    if 'tts_generator' not in st.session_state:
        st.session_state.tts_generator = TTSGenerator()
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()

def main():
    load_css()
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🎧 EchoVerse</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your text into expressive audiobooks with AI</p>', 
                unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Tone selection
        tone = st.selectbox(
            "🎭 Select Tone",
            options=["neutral", "suspenseful", "inspiring", "cheerful", "serious", "melancholic"],
            help="Choose the tone for text rewriting"
        )
        
        # Voice selection (gender)
        voice_gender = st.selectbox(
            "🗣️ Voice Gender",
            options=["Male", "Female"],
            help="Choose the voice gender for narration"
        )
        
        # Voice model selection
        voice_model = st.selectbox(
            "🎤 Select Voice Model",
            options=[
                "microsoft/speecht5_tts",
                "suno/bark-small",
                "facebook/mms-tts-eng"
            ],
            help="Choose the text-to-speech model"
        )
        
        # Audio speed control (for playback only)
        audio_speed = st.slider("Audio speed", 0.5, 2.0, 1.0, 0.1, help="Adjust the playback speed of the audio")
        
        # Add some metrics
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">' + str(len(st.session_state.narrations)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Narrations</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">' + str(sum(len(narration.get('original_text', '')) for narration in st.session_state.narrations)) + '</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Characters</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="section-header">📝 Input Text</h2>', unsafe_allow_html=True)
        
        # Text input options
        input_method = st.radio(
            "Choose input method:",
            ["Type/Paste Text", "Upload .txt File"],
            horizontal=True
        )
        
        text_input = ""
        if input_method == "Type/Paste Text":
            text_input = st.text_area(
                "Enter your text here:",
                height=250,
                placeholder="Paste your text here or upload a .txt file...",
                label_visibility="collapsed"
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a .txt file",
                type=['txt'],
                help="Maximum file size: 200MB"
            )
            if uploaded_file:
                try:
                    text_input = uploaded_file.read().decode('utf-8')
                    st.success(f"✅ File uploaded successfully! ({len(text_input)} characters)")
                    st.text_area("File content preview:", text_input[:500] + "..." if len(text_input) > 500 else text_input, height=150)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Character count
        if text_input:
            st.caption(f"Character count: {len(text_input)}")
        
        # Generate button
        if st.button("🎯 Generate Audiobook", type="primary", use_container_width=True):
            if not text_input.strip():
                st.error("Please provide some text to convert.")
            else:
                generate_audiobook(text_input, tone, voice_model, voice_gender, audio_speed)
    
    with col2:
        st.markdown('<h2 class="section-header">📚 Recent Narrations</h2>', unsafe_allow_html=True)
        display_past_narrations()

def generate_audiobook(text, tone, voice_model, voice_gender, audio_speed):
    """Generate audiobook from text"""
    
    # Create a container for the progress
    progress_container = st.container()
    
    with progress_container:
        # Progress tracking with custom UI
        st.markdown("### Generating your audiobook...")
        
        # Custom progress bar
        progress_bar = st.empty()
        progress_bar.markdown("""
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        """, unsafe_allow_html=True)
        
        status_text = st.empty()
        
        try:
            # Step 1: Rewrite text with selected tone
            status_text.text("🔄 Rewriting text with selected tone...")
            progress_bar.markdown("""
            <div class="progress-bar">
                <div class="progress-fill" style="width: 25%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            rewritten_text = st.session_state.text_rewriter.rewrite_text(
                text, tone, max_length=300  # Fixed max_length instead of UI control
            )
            
            # Step 2: Generate speech
            status_text.text("🎤 Converting text to speech...")
            progress_bar.markdown("""
            <div class="progress-bar">
                <div class="progress-fill" style="width: 50%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate speech with the selected voice gender
            audio_data = st.session_state.tts_generator.generate_speech(
                rewritten_text, voice_model, voice_gender=voice_gender.lower()
            )
            
            # Step 3: Process and save
            status_text.text("💾 Processing audio...")
            progress_bar.markdown("""
            <div class="progress-bar">
                <div class="progress-fill" style="width: 75%"></div>
            </div>
            """, unsafe_allow_html=True)
            
            audio_file = AudioUtils.save_audio(audio_data, rewritten_text[:50])
            
            progress_bar.markdown("""
            <div class="progress-bar">
                <div class="progress-fill" style="width: 100%"></div>
            </div>
            """, unsafe_allow_html=True)
            status_text.text("✅ Audiobook generated successfully!")
            
            # Display results
            display_results(text, rewritten_text, audio_data, audio_file, tone, voice_model, voice_gender, audio_speed)
            
            # Save to session history
            st.session_state.session_manager.add_narration({
                'original_text': text[:100] + "..." if len(text) > 100 else text,
                'rewritten_text': rewritten_text,
                'tone': tone,
                'voice_model': voice_model,
                'voice_gender': voice_gender,
                'audio_file': audio_file,
                'audio_data': audio_data,
                'timestamp': st.session_state.session_manager.get_timestamp()
            })
            
            # Clear progress indicators after a brief delay
            st.session_state.auto_clear_progress = True
            
        except Exception as e:
            st.error(f"Error generating audiobook: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def display_results(original_text, rewritten_text, audio_data, audio_file, tone, voice_model, voice_gender, audio_speed):
    """Display the generated audiobook results"""
    
    st.markdown('<h2 class="section-header">📊 Results</h2>', unsafe_allow_html=True)
    
    # Text comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="text-comparison">', unsafe_allow_html=True)
        st.markdown("**Original Text:**")
        st.write(original_text)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="text-comparison">', unsafe_allow_html=True)
        st.markdown(f"**Rewritten Text ({tone.title()} tone):**")
        st.write(rewritten_text)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Audio playback and download
    st.markdown('<div class="audio-container">', unsafe_allow_html=True)
    st.markdown("### 🎧 Audio Playback")
    
    # Apply speed adjustment to the audio for playback only
    speed_adjusted_audio = AudioUtils.adjust_speed(audio_data, audio_speed)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.audio(speed_adjusted_audio, format='audio/wav')
    
    with col2:
        st.download_button(
            label="📥 Download MP3",
            data=audio_data,  # Original audio without speed adjustment
            file_name=audio_file,
            mime="audio/wav",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Generate Again", use_container_width=True):
            st.experimental_rerun()
    
    st.markdown(f"**Model used:** {voice_model} ({voice_gender})")
    st.markdown('</div>', unsafe_allow_html=True)

def display_past_narrations():
    """Display past narrations from session"""
    narrations = st.session_state.session_manager.get_narrations()
    
    if not narrations:
        st.info("No narrations yet. Generate your first audiobook!")
        return
    
    for i, narration in enumerate(reversed(narrations[-5:])):  # Show last 5
        st.markdown(f'<div class="history-item">', unsafe_allow_html=True)
        st.markdown(f"**{narration['original_text']}**")
        st.markdown(f"*{narration['tone'].title()} tone • {narration['voice_gender']} • {narration['timestamp']}*")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🔊 Play", key=f"play_{i}"):
                st.audio(narration['audio_data'], format='audio/wav')
        with col2:
            st.download_button(
                label="📥 Download",
                data=narration['audio_data'],
                file_name=narration['audio_file'],
                mime="audio/wav",
                key=f"download_{i}"
            )
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()