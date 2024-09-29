import os
import requests
import json
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
github_token = os.getenv('GITHUB_TOKEN')  # Add GitHub token for pushing code

# Configure the generative AI tool with the Gemini API key
genai.configure(api_key=api_key)

# Set the Streamlit page configuration
st.set_page_config(page_title="Automated Code Generator & Enhancer", layout="wide")

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Function to initialize the Gemini Pro model for code generation
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to generate code based on software requirements
def generate_required_code(requirements, language):
    prompt = f"""
    Based on the following user requirements, generate efficient and optimized {language} code:
    
    Requirements: {requirements}
    
    The generated code should:
    - Be optimized for performance and scalability.
    - Follow best practices and coding standards.
    - Ensure that the code is error-free and maintainable.
    
    Additionally, provide a brief description of the code functionality.
    """
    response = chat.send_message(prompt, stream=True)
    generated_code = ""
    for chunk in response:
        generated_code += chunk.text
    return generated_code

# Function to enhance an existing code snippet
def enhance_code(snippet, language):
    prompt = f"""
    Optimize the following {language} code for performance, readability, and error-free execution:
    
    Code: {snippet}
    
    The enhanced code should:
    - Be optimized for performance.
    - Be free from potential errors or bugs.
    - Follow best practices and coding standards.
    - Be more readable and maintainable.
    
    Provide a brief explanation of the improvements made to the code.
    """
    response = chat.send_message(prompt, stream=True)
    enhanced_code = ""
    for chunk in response:
        enhanced_code += chunk.text
    return enhanced_code

# Function to explain the code
def explain_code(code, language):
    prompt = f"""
    Explain the following {language} code in simple terms:
    
    Code: {code}
    
    The explanation should cover what the code does and why specific design or optimization choices were made.
    """
    response = chat.send_message(prompt, stream=True)
    explanation = ""
    for chunk in response:
        explanation += chunk.text
    return explanation

# Function to push code to GitHub
def push_to_github(repo_name, file_path, content):
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json",
    }
    data = {
        "message": f"Add {file_path}",
        "content": content.encode("utf-8").decode("latin1"),
        "branch": "main",
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response.status_code == 201

# Function to execute and test the generated/enhanced code
def execute_code(snippet, language):
    try:
        if language.lower() == 'python':
            exec_globals = {}
            exec(snippet, exec_globals)
            return str(exec_globals)
        else:
            return "Code execution currently supports Python only."
    except Exception as e:
        return f"Error during execution: {str(e)}"

# Add custom CSS for background and element styling
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfJr4dULiD0zFQui8VbCUvl_uUAyU5YflC5mm41TyVnfidPn_9vTngRxkbB3mcVjp-KM8&usqp=CAU");
        background-size: cover;
        background-position: center;
    }

    textarea, input {
        background-color: black !important;
        color: white !important;
        border: 2px solid #3498db !important;
        border-radius: 10px !important;
        font-size: 16px !important;
    }

    button {
        background-color: transperent !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        cursor: pointer;
    }
    
    button:hover {
        background-color: #2980b9 !important;
    }
    h1, h2, h3, h4 {
        color: white !important;
        text-shadow: 1px 1px 5px black;
    }

    pre {
        background-color: black !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize the Streamlit app
st.header("Automated Code Generator and Enhancer")

# Language selection dropdown
language = st.selectbox("Select programming language:", ["Python", "Java", "C++", "JavaScript", "Go"])

# Action radio button options
action = st.radio("Choose an action:", ("Software Required Code", "Code Enhancing", "Explain Code"))

# Layout adjustments for the different options
if action == "Software Required Code":
    requirements = st.text_area("Enter your software requirements:", key="requirements")
    if st.button("Generate Code"):
        if requirements:
            generated_code = generate_required_code(requirements, language)
            st.session_state["chat_history"].append(("You", requirements))
            st.subheader(f"Generated {language} Code:")
            st.code(generated_code, language=language.lower())
            st.session_state["chat_history"].append(("Bot", generated_code))

elif action == "Code Enhancing":
    code_snippet = st.text_area(f"Paste your {language} code to enhance:", key="snippet")
    if st.button("Enhance Code"):
        if code_snippet:
            enhanced_code = enhance_code(code_snippet, language)
            st.session_state["chat_history"].append(("You", code_snippet))
            st.subheader(f"Enhanced {language} Code:")
            st.code(enhanced_code, language=language.lower())
            st.session_state["chat_history"].append(("Bot", enhanced_code))

            # Option to test the code
            if st.button("Test Code (Python Only)"):
                execution_result = execute_code(enhanced_code, language)
                st.subheader("Execution Result:")
                st.write(execution_result)

elif action == "Explain Code":
    code_to_explain = st.text_area(f"Paste your {language} code for explanation:", key="explain_snippet")
    if st.button("Explain Code"):
        if code_to_explain:
            explanation = explain_code(code_to_explain, language)
            st.subheader(f"Explanation of {language} Code:")
            st.write(explanation)

# GitHub integration for code pushing
st.subheader("GitHub Integration")
repo_name = st.text_input("Enter your GitHub repository name (username/repo):")
file_path = st.text_input("Enter the file path (e.g., src/main.py):")
if st.button("Push to GitHub"):
    if repo_name and file_path and 'Bot' in st.session_state["chat_history"][-1]:
        latest_code = st.session_state["chat_history"].last()[1]
        success = push_to_github(repo_name, file_path, latest_code)
        if success:
            st.success("Code pushed to GitHub successfully!")
        else:
            st.error("Failed to push code to GitHub.")

# Collaborative link generator
st.subheader("Collaborative Coding")
if st.button("Generate Collaborative Work Link"):
    if repo_name and file_path:
        collaboration_link = generate_collaboration_link(repo_name, file_path)
        st.success("Collaborative link generated successfully!")
        st.markdown(f"[Click here to collaborate]({collaboration_link})", unsafe_allow_html=True)
