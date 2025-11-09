import streamlit as st
import requests
import json
import uuid  # Used to generate a unique conversation_id for the session

# --- Configuration ---
CHATBASE_API_URL = "https://www.chatbase.co/api/v1/chat"

# Page config
st.set_page_config(
    page_title="Chatbase AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Title and description
st.title("Chatbase AI Chatbot")
st.caption("Built with Streamlit | Integrated with Chatbase")

# Sidebar with info
# Sidebar with info
with st.sidebar:
    st.header("About")
    st.write("""
    **Credit: Hemant Tyagi**
    
    This project connects Streamlit to **Chatbase** using its REST API.
    
    **Tech Stack:**
    - Streamlit (Frontend)
    - Chatbase (Backend AI server)
    - Python
    - `requests` library for API communication
    """)
    st.markdown("---")
    # REMOVE OR COMMENT OUT THIS LINE below:
    # st.write(f"Chatbot ID: `{st.secrets['CHATBOT_ID']}`") 
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize session state variables
if "messages" not in st.session_state:
    # Chatbase API requires a list of all prior messages with 'role' and 'content'
    st.session_state.messages = []

# Generate a unique conversation ID for this session (Chatbase tracks conversation history)
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Display chat history (only assistant and user messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to get response from Chatbase API
def get_chatbase_response(messages, conversation_id):
    """Sends messages history to the Chatbase API and returns the bot's response."""
    
    # Payload structure required by Chatbase
    payload = {
        "messages": messages,
        "chatbotId": st.secrets["CHATBOT_ID"],
        "conversationId": conversation_id,
        "stream": False,
        "temperature": 0.7 # Optional: control creativity
    }
    
    headers = {
        "Authorization": f"Bearer {st.secrets['CHATBASE_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(CHATBASE_API_URL, json=payload, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the Chatbase API.")
        st.error(f"Error details: {e}")
        st.info("Please check your API key, Chatbot ID, and network connection.")
        return None

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history for both display and API call
    user_message_obj = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message_obj)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass the *entire* message history to maintain context
            api_response = get_chatbase_response(st.session_state.messages, st.session_state.conversation_id)
            
            if api_response and "text" in api_response:
                response_text = api_response["text"]
                
                # Display response
                st.markdown(response_text)
                
                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
            elif api_response and "detail" in api_response:
                st.error(f"API Error: {api_response['detail']}")

# Footer
st.markdown("---")
st.caption(f"Conversation ID: {st.session_state.conversation_id[:8]}...")
