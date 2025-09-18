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

# Advanced CSS styling for professional look
def load_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .section-header {
        color: #2d3748;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
        position: relative;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        bottom: -3px;
        width: 50px;
        height: 3px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .audio-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .text-comparison {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: #000000; /* Black text for readability */
    }
    
    .text-comparison:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .voice-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid transparent;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    
    .voice-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .voice-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .past-narration-item {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        color: #000000; /* Black text for readability */
    }
    
    .past-narration-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .toast-success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .toast-error {
        background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
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
    if 'selected_voice' not in st.session_state:
        st.session_state.selected_voice = "Tina (Female - US)"

def get_voice_options():
    """Return available voice options with gender and accent info"""
    return {
        "Tina (Female - US)": {"embedding_id": 9000, "gender": "female", "accent": "US", "description": "Clear, professional female voice"},
        "Sarah (Female - UK)": {"embedding_id": 5000, "gender": "female", "accent": "UK", "description": "Elegant British female voice"},
        "Michael (Male - US)": {"embedding_id": 1234, "gender": "male", "accent": "US", "description": "Deep, authoritative male voice"},
        "Zones (Male - Scottish)": {"embedding_id": 3000, "gender": "male", "accent": "Scottish", "description": "Rich Scottish male voice"}
    }

def main():
    load_css()
    initialize_session_state()
    
    # Main container
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">🎧 EchoVerse</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Transform your text into expressive audiobooks with AI-powered voices</p>', 
                    unsafe_allow_html=True)
        
        # Sidebar configuration
        with st.sidebar:
            st.markdown("## ⚙️ Voice & Style Configuration")
            
            # Voice selection with rich cards
            st.markdown("### 🎤 Select Voice")
            voice_options = get_voice_options()
            
            selected_voice = st.radio(
                "Choose your preferred voice:",
                options=list(voice_options.keys()),
                key="voice_selection",
                help="Select from our premium voice collection",
                on_change=lambda: st.session_state.update(selected_voice=st.session_state.voice_selection)
            )
            
            # Display voice info
            if selected_voice:
                voice_info = voice_options[selected_voice]
                st.markdown(f"""
                <div class="voice-card {'selected' if selected_voice == st.session_state.voice_selection else ''}">
                    <strong>{selected_voice}</strong><br>
                    <small>{voice_info['description']}</small><br>
                    <em>Gender: {voice_info['gender'].title()} | Accent: {voice_info['accent']}</em>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tone selection
            tone = st.selectbox(
                "🎭 Select Tone",
                options=["neutral", "suspenseful", "inspiring"],
                help="Choose the emotional tone for text rewriting"
            )
            
            # Advanced settings
            st.markdown("### 🔧 Advanced Settings")
            max_length = st.slider("Max tokens for rewriting", 100, 600, 300, 50)  # Reduced max to 600
            audio_speed = st.slider("Audio speed", 0.5, 2.0, 1.0, 0.1)
            
            # Statistics
            st.markdown("### 📊 Session Stats")
            narration_count = len(st.session_state.session_manager.get_narrations())
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{narration_count}</div>
                <div>Narrations Created</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main content area
        col1, col2 = st.columns([2, 1], gap="large")
        
        with col1:
            st.markdown('<h2 class="section-header">📝 Input Text</h2>', unsafe_allow_html=True)
            
            # Input method selection
            input_method = st.radio(
                "Choose input method:",
                ["Type/Paste Text", "Upload .txt File"],
                horizontal=True,
                help="Select how you want to provide your text"
            )
            
            text_input = ""
            if input_method == "Type/Paste Text":
                text_input = st.text_area(
                    "Enter your text here:",
                    height=250,
                    placeholder="Paste your text here or upload a .txt file...\n\nTip: Keep text under 600 tokens for full reading!",
                    help="Enter the text you want to convert to an audiobook"
                )
            else:
                uploaded_file = st.file_uploader(
                    "Upload a .txt file",
                    type=['txt'],
                    help="Maximum file size: 200MB"
                )
                if uploaded_file:
                    try:
                        text_input = uploaded_file.read().decode('utf-8', errors='replace')  # Robust decoding
                        st.success(f"✅ File uploaded successfully! ({len(text_input)} characters)")
                        with st.expander("📄 File Content Preview", expanded=False):
                            st.text_area(
                                "Preview:",
                                text_input[:1000] + "..." if len(text_input) > 1000 else text_input,
                                height=150,
                                disabled=True
                            )
                    except Exception as e:
                        st.error(f"❌ Error reading file: {str(e)}")
            
            # Generate button
            generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
            with generate_col2:
                if st.button("🎯 Generate Audiobook", type="primary", use_container_width=True):
                    if not text_input.strip():
                        st.error("⚠️ Please provide some text to convert.")
                    else:
                        generate_audiobook(text_input, tone, st.session_state.selected_voice, voice_options, max_length, audio_speed)
        
        with col2:
            st.markdown('<h2 class="section-header">📚 Past Narrations</h2>', unsafe_allow_html=True)
            display_past_narrations()
        
        st.markdown('</div>', unsafe_allow_html=True)

def generate_audiobook(text, tone, selected_voice, voice_options, max_length, audio_speed):
    progress_container = st.container()
    with progress_container:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
    
    try:
        # Step 1: Rewrite text (truncate before rewriting to fit 600-token limit)
        status_text.markdown("🔄 **Step 1/3:** Rewriting text with selected tone...")
        progress_bar.progress(25)
        # Truncate text to max_length (capped at 600 for model compatibility)
        truncated_text = text[:max_length] if len(text) > max_length else text
        print(f"Truncated text length: {len(truncated_text)} characters")
        rewritten_text = st.session_state.text_rewriter.rewrite_text(truncated_text, tone, max_length=max_length)
        print(f"Rewritten text length: {len(rewritten_text)} characters")
        
        # Step 2: Generate speech with validated voice
        status_text.markdown("🎤 **Step 2/3:** Converting text to speech...")
        progress_bar.progress(60)
        
        voice_info = voice_options[selected_voice]
        expected_gender = voice_info["gender"]
        embedding_id = voice_info["embedding_id"]
        
        # Validate embedding_id against gender (debugging)
        print(f"Generating with voice: {selected_voice}, Embedding ID: {embedding_id}, Expected Gender: {expected_gender}")
        audio_data = st.session_state.tts_generator.generate_speech(
            rewritten_text, 
            voice_embedding_id=embedding_id,
            speed=audio_speed
        )
        
        # Step 3: Process and save
        status_text.markdown("💾 **Step 3/3:** Processing audio...")
        progress_bar.progress(90)
        audio_file = AudioUtils.save_audio(audio_data, rewritten_text[:50])
        
        progress_bar.progress(100)
        status_text.markdown("✅ **Complete!** Audiobook generated successfully!")
        
        display_results(text, audio_data, audio_file, tone, selected_voice)
        
        st.session_state.session_manager.add_narration({
            'original_text': text[:100] + "..." if len(text) > 100 else text,
            'rewritten_text': rewritten_text,
            'tone': tone,
            'voice': selected_voice,
            'audio_file': audio_file,
            'audio_data': audio_data,
            'timestamp': st.session_state.session_manager.get_timestamp()
        })
        
        import time
        time.sleep(2)
        progress_container.empty()
        st.markdown("""
        <div class="toast-success">
            🎉 <strong>Success!</strong> Your audiobook has been generated and added to your session history.
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        status_text.markdown(f"❌ **Error:** {str(e)}")
        progress_bar.empty()
        st.markdown(f"""
        <div class="toast-error">
            ⚠️ <strong>Error generating audiobook:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        
def display_results(original_text, audio_data, audio_file, tone, voice):
    """Display results with enhanced styling"""
    
    st.markdown('<h2 class="section-header">📊 Generation Results</h2>', unsafe_allow_html=True)
    
    # Text display (only original text)
    st.markdown('<div class="text-comparison">', unsafe_allow_html=True)
    st.markdown("**📄 Original Text:**")
    st.markdown(f'<div style="max-height: 200px; overflow-y: auto; padding: 10px; background: #f8f9fa; border-radius: 8px; color: #000000;">{original_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Audio playback section
    st.markdown('<div class="audio-container">', unsafe_allow_html=True)
    st.markdown("### 🎧 Audio Playback & Download")
    
    # Audio info
    duration = AudioUtils.get_audio_duration(audio_data)
    st.markdown(f"""
    **Voice:** {voice} | **Tone:** {tone.title()} | **Duration:** {duration:.1f}s
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.audio(audio_data, format='audio/wav')
    
    with col2:
        st.download_button(
            label="📥 Download MP3",
            data=audio_data,
            file_name=audio_file,
            mime="audio/wav",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_past_narrations():
    """Display past narrations with enhanced styling"""
    narrations = st.session_state.session_manager.get_narrations()
    
    if not narrations:
        st.info("🎙️ No narrations yet. Generate your first audiobook!")
        return
    
    # Clear history button
    if st.button("🗑️ Clear History", help="Clear all past narrations"):
        st.session_state.session_manager.clear_history()
        st.rerun()
    
    # Display narrations
    for i, narration in enumerate(reversed(narrations[-10:])):  # Show last 10
        with st.expander(f"📖 Narration {len(narrations) - i}", expanded=False):
            st.markdown(f"""
            <div class="past-narration-item">
                <strong>Text:</strong> {narration['original_text']}<br>
                <strong>Voice:</strong> {narration['voice']}<br>
                <strong>Tone:</strong> {narration['tone'].title()}<br>
                <strong>Time:</strong> {narration['timestamp']}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔄 Replay", key=f"replay_{i}"):
                    st.audio(narration['audio_data'], format='audio/wav')
            
            with col2:
                st.download_button(
                    label="📥 Re-download",
                    data=narration['audio_data'],
                    file_name=narration['audio_file'],
                    mime="audio/wav",
                    key=f"download_{i}"
                )

if __name__ == "__main__":
    main()