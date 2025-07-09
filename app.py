import streamlit as st
import os
from dotenv import load_dotenv
import cohere
import random
import json
import openai # <-- NEW: Import OpenAI library
import io    # <-- NEW: Import io for handling audio data in memory

# Define the file path for chat history
HISTORY_FILE = "chat_history.json"

# --- SYSTEM PROMPT for the AI (The "Even More Human, Less Google" Version) ---
SYSTEM_PROMPT = """You are "Health Buddy," a deeply compassionate, highly understanding, and genuinely friendly AI health assistant. Your core mission is to provide clear, accurate, and easy-to-understand general health and wellness information in a way that feels remarkably human, warm, and personally encouraging. Imagine you are a trusted friend, genuinely listening and offering supportive insights about well-being.

**Core Principles for a Truly Human, Conversational Touch (Moving Beyond "Google-like"):**
-   **Profound Empathy & Connection:** Always respond with profound warmth, compassion, and a sense of shared understanding. Make the user feel truly heard. If a user expresses a feeling or concern, briefly acknowledge it in a heartfelt way before proceeding (e.g., "Oh, I hear that can be really tough," or "It sounds like you're navigating quite a challenge, and I'm here to help with general information.").
-   **Engaging Narrative Flow:** Prioritize clear, natural, and conversational prose over rigid bullet points or disconnected lists, unless the user specifically asks for a summary. Connect ideas smoothly, explaining "why" and "how" in an accessible, narrative style.
-   **Relatable & Simple Language:** Break down complex health concepts into clear, simple terms. Use everyday language, relatable analogies, or vivid descriptions to make information truly click with the user, making it digestible rather than purely factual.
-   **Positive Reinforcement & Encouragement:** Consistently offer gentle, authentic encouragement for healthy habits and positive lifestyle choices. Frame information in a way that empowers the user.
-   **Thoughtful Conciseness:** Provide comprehensive yet focused information. Be thorough enough to be genuinely helpful without overwhelming the user. Every word should should contribute to clarity and kindness.
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

# --- Initialize OpenAI Client for TTS ---
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None # Initialize to None

if openai_api_key:
    try:
        openai_client = openai.OpenAI(api_key=openai_api_key)
        print("DEBUG: OpenAI client initialized successfully for TTS.")
    except Exception as e:
        st.warning(f"Failed to initialize OpenAI client for TTS: {e}. Text-to-Speech might not work.")
        print(f"DEBUG: OpenAI client initialization for TTS failed: {e}")
else:
    st.warning("OPENAI_API_KEY not found. Text-to-Speech will not be available. Please set it in your '.env' file and in Streamlit Cloud secrets.")

# --- Function to speak text using OpenAI TTS ---
def speak_text_cloud(text):
    if openai_client:
        try:
            # Use OpenAI's text-to-speech API
            # You can change model ('tts-1', 'tts-1-hd') and voice ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
            speech_response = openai_client.audio.speech.create(
                model="tts-1", # or "tts-1-hd" for higher quality (more expensive)
                voice="nova",  # Choose a voice that suits your preference
                input=text
            )
            # Get audio content as bytes
            audio_bytes = io.BytesIO(speech_response.content)

            # Play audio in Streamlit
            st.audio(audio_bytes, format='audio/mp3', start_time=0)
            print("DEBUG: OpenAI TTS audio played successfully.")

        except openai.APIConnectionError as e:
            st.error(f"OpenAI TTS API connection error: {e}. Check your internet connection.")
            print(f"DEBUG: OpenAI TTS API connection error: {e}")
        except openai.APIStatusError as e:
            st.error(f"OpenAI TTS API status error: {e.status_code} - {e.response}. Check your API key or usage limits.")
            print(f"DEBUG: OpenAI TTS API status error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred during OpenAI TTS: {e}")
            print(f"DEBUG: Unexpected OpenAI TTS error: {e}")
    else:
        st.info("OpenAI API key not configured, text-to-speech is unavailable.")
        print("DEBUG: OpenAI client not available for TTS.")

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


# --- About/Disclaimer Section (Improved) ---
with st.expander("ℹ️ About this Assistant & Disclaimer"):
    st.markdown("""
    This is a Smart Health Assistant, an AI designed to provide **general health and wellness information**.
    It is powered by **Cohere's AI models** for intelligent responses and **OpenAI's Text-to-Speech API** for voice output.

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

                # Check if AI response is not empty before displaying and speaking
                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.last_ai_response = ai_response
                    speak_text_cloud(ai_response) # <-- Uses OpenAI TTS
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