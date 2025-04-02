import streamlit as st
import requests

# Set app title and layout
st.set_page_config(page_title="Travel Planning Assistant", layout="wide")

# Initialize session state for server selection
if "server_option" not in st.session_state:
    st.session_state.server_option = None

# Server selection page
if st.session_state.server_option is None:
    st.title("🔧 Server Selection")
    server_option = st.selectbox("Choose server:", ["FastAPI", "BentoML"], index=0)
    if st.button("Continue"):
        st.session_state.server_option = server_option
        st.rerun()
else:
    st.title("🌍 Travel Planning Assistant")
    server_urls = {"FastAPI": "http://localhost:8000/query", "BentoML": "http://localhost:3000/query"}
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = []  # Store cleared chat history separately
    if "current_chat_index" not in st.session_state:
        st.session_state.current_chat_index = None  # Track the currently active chat
    
    # Sidebar for saved chat history
    st.sidebar.title("📜 Saved Chats")
    for i, chat in enumerate(st.session_state.saved_chats):
        if st.sidebar.button(f"Chat {i+1}"):
            # Save current chat before switching
            if st.session_state.current_chat_index is not None:
                st.session_state.saved_chats[st.session_state.current_chat_index] = st.session_state.messages.copy()
            st.session_state.messages = chat.copy()
            st.session_state.current_chat_index = i  # Set current chat index
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("How can I help you with your travel plans?"):
        # Add user message to history and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send the prompt to the selected backend server
        try:
            api_url = server_urls[st.session_state.server_option]  # Get selected server URL
            # if (st.session_state.server_option=="FastAPI"):
            response = requests.post(api_url, json={"input": prompt})
            # else:
                # response = requests.post(api_url, json={"input": prompt})  # BentoML format

            
            # Handle the response from the backend API
            if response.status_code == 200:
                assistant_response = response.json()["response"]
            else:
                assistant_response = f"❗ Error: {response.text}"
    
            # Display the assistant's response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
    
            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
        except requests.exceptions.RequestException as e:
            # If the API request fails
            assistant_response = f"❗ API Error: {e}"
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
    
        # Auto-save conversation to the current chat index
        if st.session_state.current_chat_index is not None:
            st.session_state.saved_chats[st.session_state.current_chat_index] = st.session_state.messages.copy()
    
    # Clear chat button but update current chat if modifying existing, otherwise save new chat
    if st.sidebar.button("🧹 New Chat"):
        if st.session_state.messages:
            if st.session_state.current_chat_index is not None:
                st.session_state.saved_chats[st.session_state.current_chat_index] = st.session_state.messages.copy()  # Update existing chat
            else:
                st.session_state.saved_chats.append(st.session_state.messages.copy())  # Save new chat
        st.session_state.messages = []
        st.session_state.current_chat_index = None  # Reset index for new chat
        st.rerun()
