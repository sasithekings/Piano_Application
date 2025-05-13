import streamlit as st
import base64
from io import BytesIO
import numpy as np
from scipy.io.wavfile import write

# Set page title and configuration
st.set_page_config(page_title="Interactive Piano App", layout="wide")

# Add a title and description
st.title("🎹 Interactive Piano App")
st.markdown("Click on the piano keys to play notes!")

# Function to generate a piano note based on frequency
def generate_piano_note(frequency, duration=0.5, sample_rate=44100):
    """
    Generate a piano note with a given frequency.
    
    Args:
        frequency: The frequency of the note in Hz
        duration: Length of the note in seconds
        sample_rate: Audio sample rate
        
    Returns:
        Audio data encoded as base64 string
    """
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate the piano note with harmonics to sound more like a piano
    # Fundamental frequency
    note = 0.7 * np.sin(2 * np.pi * frequency * t)
    # Add harmonics with decreasing amplitude
    note += 0.3 * np.sin(2 * np.pi * 2 * frequency * t)  # 1st harmonic
    note += 0.2 * np.sin(2 * np.pi * 3 * frequency * t)  # 2nd harmonic
    note += 0.1 * np.sin(2 * np.pi * 4 * frequency * t)  # 3rd harmonic
    
    # Apply a simple envelope to make it sound more natural
    envelope = np.exp(-3 * t / duration)
    note = note * envelope
    
    # Convert to 16-bit data
    audio = note * (2**15 - 1) / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    
    # Create a BytesIO object to avoid writing to disk
    buffer = BytesIO()
    write(buffer, sample_rate, audio)
    buffer.seek(0)
    
    # Convert to base64 encoding
    b64 = base64.b64encode(buffer.read()).decode()
    return b64

# Piano note frequencies (C4 to B4)
NOTE_FREQUENCIES = {
    'C': 261.63,  # C4
    'D': 293.66,  # D4
    'E': 329.63,  # E4
    'F': 349.23,  # F4
    'G': 392.00,  # G4
    'A': 440.00,  # A4
    'B': 493.88   # B4
}

# Define colors for the keys
WHITE_KEY_COLOR = "#FFFFFF"
WHITE_KEY_BORDER = "#000000"
BLACK_KEY_COLOR = "#000000"
BLACK_KEY_BORDER = "#000000"
ACTIVE_KEY_COLOR = "#ADD8E6"  # Light blue when key is pressed

# Store the currently playing note (if any)
if 'last_note' not in st.session_state:
    st.session_state.last_note = None

# Function to play a note when a key is clicked
def play_note(note):
    """
    Play a note when a piano key is clicked.
    
    Args:
        note: The note name (e.g., 'C', 'D', etc.)
    """
    st.session_state.last_note = note
    frequency = NOTE_FREQUENCIES[note]
    b64_audio = generate_piano_note(frequency)
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    
# Streamlit doesn't have built-in piano keys, so we'll create custom buttons
# arranged to look like a piano keyboard
st.markdown("### Virtual Piano Keyboard")

# Create two columns - one for the piano keys and one for information
piano_col, info_col = st.columns([3, 1])

with piano_col:
    # Create a container for the piano keyboard
    piano_container = st.container()
    
    # Create a row of white keys with proper spacing for black keys
    white_keys_row = piano_container.columns([1, 1, 1, 1, 1, 1, 1])
    
    # Create white keys
    # Each key is a button with custom styling
    for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
        with white_keys_row[i]:
            key_color = ACTIVE_KEY_COLOR if st.session_state.last_note == note else WHITE_KEY_COLOR
            st.markdown(f"""
                <div style="
                    background-color: {key_color};
                    border: 2px solid {WHITE_KEY_BORDER};
                    border-radius: 0 0 5px 5px;
                    text-align: center;
                    padding: 80px 0 20px 0;
                    margin: 0 2px;
                    cursor: pointer;
                    font-weight: bold;
                " onclick="this.style.backgroundColor='{ACTIVE_KEY_COLOR}'; setTimeout(() => {{this.style.backgroundColor='{WHITE_KEY_COLOR}';}}, 300);">
                    {note}
                </div>
                """, unsafe_allow_html=True)
            
            # Since HTML onclick can't directly call Streamlit functions,
            # we use a button underneath our styled div
            if st.button(f"Play {note}", key=f"btn_{note}", use_container_width=True):
                play_note(note)

with info_col:
    st.markdown("### How to Play")
    st.markdown("""
    1. Click on any piano key to hear its sound
    2. White keys represent the natural notes (C, D, E, F, G, A, B)
    3. Experiment with different combinations to create melodies
    """)
    
    st.markdown("### Currently Playing")
    if st.session_state.last_note:
        st.markdown(f"**Note:** {st.session_state.last_note}")
        st.markdown(f"**Frequency:** {NOTE_FREQUENCIES[st.session_state.last_note]} Hz")
    else:
        st.markdown("No note is currently playing")

# Add some spacing
st.markdown("---")

# Add information about future enhancements
st.markdown("### Future Enhancements")
st.markdown("""
- **Recording Feature**: Record and play back your melodies
- **Piano Lessons**: Learn basic songs step by step
- **Additional Sound Packs**: Try different instrument sounds
- **Black Keys**: Add sharps and flats for more complex music
- **Octave Control**: Play notes in different octaves
""")

# Footer with version information
st.markdown("---")
st.markdown("v1.0 - Simple Piano App | Made with Streamlit")