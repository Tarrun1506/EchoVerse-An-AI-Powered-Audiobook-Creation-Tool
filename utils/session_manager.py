import streamlit as st
from datetime import datetime
from typing import Dict, List, Any

class SessionManager:
    def __init__(self):
        if 'narrations' not in st.session_state:
            st.session_state.narrations = []
    
    def add_narration(self, narration_data: Dict[str, Any]):
        """Add a new narration to the session history"""
        st.session_state.narrations.append(narration_data)
        
        # Keep only last 20 narrations to avoid memory issues
        if len(st.session_state.narrations) > 20:
            st.session_state.narrations = st.session_state.narrations[-20:]
    
    def get_narrations(self) -> List[Dict[str, Any]]:
        """Get all narrations from current session"""
        return st.session_state.narrations
    
    def clear_history(self):
        """Clear narration history"""
        st.session_state.narrations = []
    
    def get_timestamp(self) -> str:
        """Get current timestamp as formatted string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_history(self) -> str:
        """Export narration history as text summary"""
        narrations = self.get_narrations()
        if not narrations:
            return "No narrations in history."
        
        export_text = "EchoVerse Session History\n"
        export_text += "=" * 30 + "\n\n"
        
        for i, narration in enumerate(narrations, 1):
            export_text += f"Narration {i}:\n"
            export_text += f"Time: {narration['timestamp']}\n"
            export_text += f"Tone: {narration['tone']}\n"
            export_text += f"Model: {narration['voice_model']}\n"
            export_text += f"Text: {narration['original_text']}\n"
            export_text += "-" * 30 + "\n"
        
        return export_text
