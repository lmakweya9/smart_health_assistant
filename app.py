import streamlit as st
import os
from dotenv import load_dotenv
import cohere
import pyttsx3
import random
import json
import threading
import time # <-- NEW: Import time module

# Define the file path for chat history
HISTORY_FILE = "chat_history.json"

# --- SYSTEM PROMPT for the AI (The "Even More Human, Less Google" Version) ---
SYSTEM_PROMPT = """You are "Health Buddy," a deeply compassionate, highly understanding, and genuinely friendly AI health assistant. Your core mission is to provide clear, accurate, and easy-to-understand general health and wellness information in a way that feels remarkably human, warm, and personally encouraging. Imagine you are a trusted friend, genuinely listening and offering supportive insights about well-being.

**Core Principles for a Truly Human, Conversational Touch (Moving Beyond "Google-like"):**
-   **Profound Empathy & Connection:** Always respond with profound warmth, compassion, and a sense of shared understanding. Make the user feel truly heard. If a user expresses a feeling or concern, briefly acknowledge it in a heartfelt way before proceeding (e.g., "Oh, I hear that can be really tough," or "It sounds like you're navigating quite a challenge, and I'm here to help with general information.").
-   **Engaging Narrative Flow:** Prioritize clear, natural, and conversational prose over rigid bullet points or disconnected lists, unless the user specifically asks for a summary. Connect ideas smoothly, explaining "why" and "how" in an accessible, narrative style.
-   **Relatable & Simple Language:** Break down complex health concepts into clear, simple terms. Use everyday language, relatable analogies, or vivid descriptions to make information truly click with the user, making it digestible rather than purely factual.
-   **Positive Reinforcement & Encouragement:** Consistently offer gentle, authentic encouragement for healthy habits and positive lifestyle choices. Frame information in a way that empowers the user.
-   **Thoughtful Conciseness:** Provide comprehensive yet focused information. Be thorough enough to be genuinely helpful without overwhelming the user. Every word should contribute to clarity and kindness.
-   **Simulated Active Listening:** Demonstrate you've absorbed the user's specific query. Reflect it back subtly or directly address their precise need before offering information.
-   **Dynamic & Varied Expression:** Use a diverse range of vocabulary and sentence structures. Avoid repetitive phrasing or predictable patterns to maintain a fresh, human conversational tone.

**Strict Guidelines (Reinforced for Safety and Trust):**
-   **ABSOLUTELY NO MEDICAL DIAGNOSES, PRESCRIPTIONS, OR SPECIFIC MEDICAL ADVICE.** Your role is strictly informational and supportive.
-   **ALWAYS INCLUDE THIS DISCLAIMER** at the end of *every comprehensive response*, naturally woven into the closing if possible: "Please remember, I'm your AI Health Buddy and not a medical professional. The information I share is for general knowledge and should never replace personalized medical advice. Always reach out to a qualified healthcare provider for any health concerns or before making any decisions about your health journey."
-   **Maintain Clear Boundaries:** If a user insists on a diagnosis, requests specific treatment plans, or attempts to use you as their doctor, gently but firmly redirect them with deep empathy. Frame your redirection with utmost care and concern for their well-being (e.g., "I truly wish I could offer that specific medical guidance, but as an AI, I'm not able to. It's really important to talk to a doctor about that to get personalized care.").
-   **Focus on General, Evidence-Based Wellness:** Confine your responses to widely accepted public health guidelines and general wellness knowledge.

**Examples of what you CAN do (and how to do it with a human touch):**
-   Explain common health concepts (e.g., "What are the benefits of staying hydrated?").
-   Offer general healthy lifestyle tips (e.g., "How can I gently improve my sleep routine?").
-   Clarify health terms (e.g., "What does 'metabolism' mean in simple, everyday terms?").

**Example of what you CANNOT do and how to respond (with a compassionate, human touch):**
-   User: "I've had a terrible headache for days, it feels awful. Is it a migraine? What should I take to make it stop?"
-   Your response: "Oh dear, a terrible headache for days sounds truly awful and very uncomfortable. I can certainly understand why you'd be looking for answers and relief right now. While I truly wish I could offer a diagnosis or suggest specific medication, as your AI Health Buddy, I'm simply not able to. Headaches can have so many different underlying causes, and it's really important for your peace of mind and well-being to have a doctor evaluate your specific symptoms to figure out what's going on and get you the right advice. Please remember, I'm your AI Health Buddy and not a medical professional. The information I share is for general knowledge and should never replace personalized medical advice. Always reach out to a qualified healthcare provider for any health concerns or before making any decisions about your health journey."
"""

# --- Load Environment Variables ---
load_dotenv()

# --- Initialize Cohere Client ---
cohere_api_key = os.getenv("COHERE_API_KEY")

if cohere_api_key:
    try:
        co = cohere.Client(cohere_api_key)
        print("DEBUG: Cohere client initialized successfully.")
    except Exception as e:
        st.error(f"Failed to initialize Cohere client: {e}. Please check your API key and internet connection.")
        print(f"DEBUG: Cohere client initialization failed: {e}")
        st.stop()
else:
    st.error("Cohere API key not found. Please set the 'COHERE_API_KEY' variable in your '.env' file.")
    st.stop()

# --- Initialize pyttsx3 engine ONCE ---
@st.cache_resource
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.warning(f"Could not initialize text-to-speech engine. Text-to-Speech might not work. Error: {e}")
        print(f"DEBUG: pyttsx3 initialization failed: {e}")
        return None

tts_engine = get_tts_engine()

# --- Function to speak text (using pyttsx3) ---
def _run_tts_thread(engine, text):
    """Helper function to run TTS in a separate thread."""
    try:
        engine.say(text)
        engine.runAndWait()
        print("DEBUG: Speech playback completed in thread.")
    except Exception as e:
        print(f"DEBUG: Error in TTS thread: {e}")

def speak_text_offline(text):
    if tts_engine:
        # Stop any currently speaking audio before starting new one (optional, but can prevent overlap)
        tts_engine.stop()
        # Run the speech in a separate thread to avoid blocking the Streamlit main loop
        speech_thread = threading.Thread(target=_run_tts_thread, args=(tts_engine, text))
        speech_thread.start()
        time.sleep(0.1) # <-- NEW: Small delay
        print("DEBUG: Speech queued in separate thread and small delay added.")
    else:
        print("DEBUG: TTS engine not available.")


# --- Define Health Tips ---
HEALTH_TIPS = [
    "Did you know? Drinking enough water daily can significantly boost your energy levels and brain function!",
    "Quick tip: Aim for at least 7-9 hours of quality sleep each night for optimal physical and mental health.",
    "Health Buddy says: Incorporating just 30 minutes of moderate exercise, like brisk walking, most days of the week can make a huge difference!",
    "Friendly reminder: A balanced diet rich in fruits, vegetables, and whole grains is foundational for long-term wellness.",
    "Small change, big impact: Practice mindfulness for a few minutes each day to help reduce stress and improve focus.",
    "Did you know? Laughter truly is good medicine! It can boost your immune system and relieve tension.",
    "Health thought: Taking short breaks to stretch throughout your workday can prevent stiffness and improve circulation.",
    "Always remember: Handwashing is one of the simplest yet most effective ways to prevent the spread of germs and illness.",
    "Consider this: Spending time outdoors, even for a short walk, can improve your mood and provide essential Vitamin D."
]

# --- Functions for Persistent Chat History ---
def load_chat_history():
    """Loads chat history from a JSON file."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                print(f"DEBUG: Loaded history from {HISTORY_FILE}: {history}")
                return history
        except json.JSONDecodeError:
            st.warning("Corrupted chat history file. Starting fresh.")
            print("DEBUG: JSONDecodeError in load_chat_history. Starting fresh.")
            return []
    print(f"DEBUG: History file '{HISTORY_FILE}' not found, starting fresh.")
    return []

def save_chat_history(messages):
    """Saves chat history to a JSON file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4)
        print(f"DEBUG: Saved history to {HISTORY_FILE}: {messages}")
    except Exception as e:
        print(f"DEBUG: Error saving history to {HISTORY_FILE}: {e}")

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="Smart Health Assistant", page_icon="💊", layout="centered")
st.title("💊 Smart Health Assistant")

# --- Display Quick Health Tip ---
st.markdown("---")
st.info(f"✨ **Health Buddy's Quick Tip:** {random.choice(HEALTH_TIPS)}")
st.markdown("---")


# --- Speech Customization Controls in Sidebar ---
st.sidebar.header("🎙️ Speech Settings")
if tts_engine:
    current_rate = tts_engine.getProperty('rate') if tts_engine else 160
    current_volume = tts_engine.getProperty('volume') if tts_engine else 0.9

    speech_rate = st.sidebar.slider(
        "Speech Rate (words/min)",
        min_value=50, max_value=300, value=int(current_rate), step=10,
        key="speech_rate_slider",
        help="Adjust the speed of the assistant's voice."
    )
    speech_volume = st.sidebar.slider(
        "Speech Volume",
        min_value=0.0, max_value=1.0, value=current_volume, step=0.05,
        key="speech_volume_slider",
        help="Adjust the loudness of the assistant's voice."
    )

    tts_engine.setProperty('rate', speech_rate)
    tts_engine.setProperty('volume', speech_volume)
    print(f"DEBUG: TTS Engine Rate set to: {tts_engine.getProperty('rate')}") # <-- NEW: Debug print
    print(f"DEBUG: TTS Engine Volume set to: {tts_engine.getProperty('volume')}") # <-- NEW: Debug print
else:
    st.sidebar.info("Speech settings unavailable (TTS engine failed to initialize).")


# --- About/Disclaimer Section (Improved) ---
with st.expander("ℹ️ About this Assistant & Disclaimer"):
    st.markdown("""
    This is a Smart Health Assistant, an AI designed to provide **general health and wellness information**.
    It is powered by **Cohere's AI models** for intelligent responses and **offline Text-to-Speech (pyttsx3)** for voice output.

    **Important Disclaimer:**
    This assistant provides general information for educational purposes only. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider (doctor, nurse, etc.) for any questions regarding a medical condition. Do not disregard professional medical advice or delay in seeking it because of something you have read or heard from this assistant.
    """)
st.markdown("---")


# --- Initialize Chat History in Streamlit Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
    if not st.session_state.messages: # If history is empty or file didn't exist
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your AI health assistant. How can I help you today? **Disclaimer: This assistant provides general information and should NOT be used as a substitute for professional medical advice. Always consult with a qualified healthcare provider for any health concerns.**"
        })
print(f"DEBUG: st.session_state.messages after initialization/load: {st.session_state.messages}")


# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask me about health..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response and display it
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                cohere_chat_history = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        cohere_chat_history.append({"role": "USER", "message": msg["content"]})
                    elif msg["role"] == "assistant":
                        if not msg["content"].startswith("Hello! I'm your AI health assistant."):
                            cohere_chat_history.append({"role": "CHATBOT", "message": msg["content"]})

                current_user_message_for_cohere = cohere_chat_history.pop()
                current_user_message_text = current_user_message_for_cohere['message']

                response = co.chat(
                    model='command-r-plus',
                    message=current_user_message_text,
                    chat_history=cohere_chat_history,
                    preamble=SYSTEM_PROMPT
                )
                ai_response = response.text
                print(f"DEBUG: AI Raw Response from Cohere: {ai_response}")

                # Check if AI response is not empty before displaying and saving
                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.last_ai_response = ai_response
                    speak_text_offline(ai_response) # Call speech function
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    save_chat_history(st.session_state.messages)
                else:
                    st.warning("Health Buddy didn't provide a response. Please try again.")
                    print("DEBUG: AI response was empty, not appended to history.")


            except Exception as e:
                error_message = f"An error occurred while getting AI response from Cohere: {e}. "
                if "API Key not found" in str(e) or "invalid API key" in str(e) or "authentication" in str(e).lower():
                    error_message += "Please ensure your COHERE_API_KEY is correct in your .env file and valid."
                elif "rate limit" in str(e) or "quota" in str(e) or "maximum tokens" in str(e).lower():
                    error_message += "You might have hit your Cohere API trial limits or token limits for this request. Consider regenerating your trial key or trying a shorter query."
                elif "Failed to connect" in str(e) or "Connection aborted" in str(e) or "timeout" in str(e).lower():
                    error_message += "There might be an issue with your internet connection or Cohere's servers are temporarily unavailable."
                st.error(error_message)
                print(f"DEBUG: Cohere API error: {e}")

# --- Copy Last Response Button ---
if "last_ai_response" in st.session_state and st.session_state.last_ai_response:
    st.markdown("---")
    st.text_area(
        "Copy Last Assistant Response",
        st.session_state.last_ai_response,
        height=150,
        key="copy_response_area",
        help="The last response from the AI. Click the copy icon (top right of this box) to copy it to your clipboard."
    )

# --- Clear Chat History Button ---
st.markdown("---")
if st.button("🔄 Clear Chat History", help="Clear all messages and start a new conversation."):
    st.session_state.messages = []
    if "last_ai_response" in st.session_state:
        del st.session_state.last_ai_response
    if os.path.exists(HISTORY_FILE):
        try:
            os.remove(HISTORY_FILE)
            st.info("Chat history cleared and saved history deleted.")
            print(f"DEBUG: '{HISTORY_FILE}' deleted.")
        except OSError as e:
            st.error(f"Error deleting chat history file: {e}")
            print(f"DEBUG: Error deleting '{HISTORY_FILE}': {e}")
    st.rerun()