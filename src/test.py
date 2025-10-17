import streamlit as st

st.title("My Main App Page")
st.write("Here is the main content of my application.")

# 1. Use columns to place the popover button on the right
# This creates an invisible layout: 80% space | 20% button
_left, col_right = st.columns([0.8, 0.2]) 

with col_right:
    # 2. Create the popover button
    with st.popover("💬 Chat"):
        # 3. This is the content *inside* the floating popover
        st.header("Chatbot")
        
        # Example chat history
        with st.chat_message("assistant"):
            st.write("Hello! How can I help you?")
        
        with st.chat_message("user"):
            st.write("I need help with floating elements!")

        # Chat input box at the bottom of the popover
        prompt = st.chat_input("Say something...")
        
        if prompt:
            # This is where your app logic would go
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                st.write(f"You said: {prompt}")