import streamlit as st
import time
import json
from dotenv import load_dotenv
import os

from autogen import ConversableAgent, UserProxyAgent, LLMConfig
from autogen.code_utils import content_str

# Utilities and tools (custom tool to be added soon)
from coding.utils import show_chat_history, display_session_msg, save_messages_to_json, paging
from coding.agenttools import extract_pdf_content, load_pdf

# At the start of your Streamlit app, load the PDF document
pdf_path = "/workspaces/Gild-chatbot/data/uk_conflict_timeline.pdf"  # Adjust the path as needed
doc = load_pdf(pdf_path)  # This is the PDF document object

# Now `doc` is available for extracting content from the PDF


# Load environment variables
load_dotenv(override=True)

# Constants
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
placeholderstr = "Please input your command"
user_name = "Fernando"
user_image = "https://www.w3schools.com/howto/img_avatar.png"

# Gemini LLM config
llm_config_gemini = LLMConfig(
    api_type="google",
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
)

def stream_data(stream_str):
    for word in stream_str.split(" "):
        yield word + " "
        time.sleep(0.05)

def save_lang():
    st.session_state['lang_setting'] = st.session_state.get("language_select")

def main():
    st.set_page_config(
        page_title='K-Assistant - The Residemy Agent',
        layout='wide',
        initial_sidebar_state='auto',
        menu_items={
            'Get Help': 'https://streamlit.io/',
            'Report a bug': 'https://github.com',
            'About': 'About your application: **0.20.3.9**'
        },
        page_icon="img/favicon.ico"
    )

    st.title(f"💬 {user_name}'s Chatbot")

    with st.sidebar:
        paging()
        selected_lang = st.selectbox("Language", ["English", "繁體中文"], index=0, on_change=save_lang, key="language_select")
        lang_setting = st.session_state.get('lang_setting', selected_lang)
        st.session_state['lang_setting'] = lang_setting

        with st.container(border=True):
            st.image(user_image)

    st_c_chat = st.container(border=True)
    display_session_msg(st_c_chat, user_image)

    # System instruction for the Gemini agent
    system_instruction = f"""You are a helpful assistant. Use the registered tools to complete tasks. 
    Always finish with '##ALL DONE##'. Respond in {lang_setting}.
    """

    # Instantiate the Gemini agent
    with llm_config_gemini:
        gemini_agent = ConversableAgent(
            name="Gemini_Agent",
            system_message=system_instruction,
        )

    # Set up user proxy
    user_proxy = UserProxyAgent(
        "user_proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda x: content_str(x.get("content")).find("##ALL DONE##") >= 0,
    )

    # Register tools
    def register_agent_methods(agent, proxy, methods):
        for name, description, func in methods:
            agent.register_for_llm(name=name, description=description)(func)
            proxy.register_for_execution(name=name)(func)

    methods_to_register = [
    ("extract_pdf_content", "Extracts text (and tables) from a hardcoded PDF file.", extract_pdf_content),
    ]

    register_agent_methods(gemini_agent, user_proxy, methods_to_register)

    def generate_response(prompt):
        chat_result = user_proxy.initiate_chat(
            gemini_agent,
            message=prompt,
        )
        return chat_result.chat_history

    def chat(prompt: str):
        try:
            # Try to convert the user input to an integer (page number)
            page_number = int(prompt.strip())
            
            # Check if the page number is valid
            paginated_content = extract_pdf_content(doc)  # Get content from the PDF
            
            # If the page exists in the content, show it
            if 0 < page_number <= len(paginated_content):
                content_to_show = paginated_content[page_number - 1]  # List is 0-indexed, so we subtract 1
                show_chat_history(st_c_chat, content_to_show, user_image)
            else:
                show_chat_history(st_c_chat, f"Sorry, the document has only {len(paginated_content)} pages. Please request a valid page number.", user_image)
        except ValueError:
            # If the input isn't a valid page number
            show_chat_history(st_c_chat, "Please enter a valid page number.", user_image)


    if prompt := st.chat_input(placeholder="Please enter the page number you want to view.", key="chat_bot"):
        chat(prompt)

if __name__ == "__main__":
    main()
