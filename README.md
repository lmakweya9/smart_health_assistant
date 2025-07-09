## README
💊 Health Buddy AI Assistant
Health Buddy is a compassionate and intelligent AI assistant designed to provide general health and wellness information. Built with Streamlit, it leverages Cohere's powerful Large Language Models (LLMs) for conversational responses and OpenAI's Text-to-Speech (TTS) API for an engaging voice experience.

✨ Features
Intelligent Conversations: Powered by Cohere's advanced LLMs to provide informative and human-like responses on various health topics.

Compassionate & Supportive Tone: Designed to be a friendly, understanding, and encouraging companion for your wellness journey.

Text-to-Speech (TTS): Utilizes OpenAI's high-quality TTS to speak out assistant responses for an accessible and interactive experience.

Persistent Chat History: Saves your conversations locally (in chat_history.json) so you can pick up where you left off.

Quick Health Tips: Displays helpful and random health tips to encourage healthy habits.

Clear Disclaimers: Explicitly states that the AI provides general information and is not a substitute for professional medical advice.

⚠️ Important Disclaimer
This assistant provides general information for educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider (doctor, nurse, etc.) for any questions regarding a medical condition. Do not disregard professional medical advice or delay in seeking it because of something you have read or heard from this assistant.

🚀 Technologies Used
Python

Streamlit: For building the interactive web application.

Cohere API: For the Large Language Model (LLM) that powers the conversational AI.

OpenAI API: Specifically for the Text-to-Speech (TTS) capabilities.

python-dotenv: For managing API keys securely in local development.

📦 Setup and Installation (Local Development)
Follow these steps to get Health Buddy running on your local machine:

Prerequisites
Python 3.9 or higher installed on your system.

A Cohere API Key (get one from Cohere Dashboard).

An OpenAI API Key (get one from OpenAI Platform).

Steps

Clone the repository: git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME # Replace with your actual repository name
Create and activate a virtual environment (recommended): python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Create a .env file:
In the root of your project directory, create a file named .env and add your API keys:

COHERE_API_KEY="your_cohere_api_key_here"
OPENAI_API_KEY="your_openai_api_key_here"

Important: Do NOT commit your .env file to GitHub. Add .env to your .gitignore file if it's not already there.

Install dependencies:
The project uses requirements.txt to manage dependencies. Ensure this file is up-to-date. If you followed previous instructions, your requirements.txt should already be correct. To be safe:
pip install openai cohere streamlit python-dotenv
pip freeze > requirements.txt
Verify that openai and cohere are listed in requirements.txt.

▶️ How to Run Locally
Once setup is complete, run the Streamlit app from your terminal: streamlit run app.py

This will open the Health Buddy AI Assistant in your default web browser.

☁️ Deployment to Streamlit Community Cloud
Health Buddy is designed for easy deployment on Streamlit Community Cloud.

Push your code to GitHub:
Ensure your app.py and requirements.txt (with openai, cohere, etc. listed and pywin32 removed) are pushed to a GitHub repository.

Set up API Keys as Secrets:

Go to your Streamlit Community Cloud dashboard.

Click "New app" or select your existing app.

Navigate to "Advanced settings" -> "Secrets".

Add your API keys in TOML format:

Ini, TOML

COHERE_API_KEY="your_cohere_api_key_here"
OPENAI_API_KEY="your_openai_api_key_here"
Replace your_cohere_api_key_here and your_openai_api_key_here with your actual keys.

Specify Python Version (Recommended):
To ensure consistent behavior and avoid potential Python version-related issues, it's highly recommended to specify the Python version for your app.

In the root of your GitHub repository (same level as app.py and requirements.txt), create a file named runtime.txt.

Inside runtime.txt, add a single line with your desired Python version. For example, for Python 3.10:

python-3.10
Commit and push runtime.txt to your GitHub repository.

Deploy your app:

Connect your GitHub repository to Streamlit Cloud.

Select the branch and app.py file.

Click "Deploy!".

🤝 Contributing
Feel free to fork this repository, open issues, or submit pull requests if you have suggestions for improvements or new features!

📄 License
This project is open-source and available under the MIT License.
