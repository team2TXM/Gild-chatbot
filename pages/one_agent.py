import streamlit as st
import time
import json
from dotenv import load_dotenv
import os

from autogen import ConversableAgent, UserProxyAgent, LLMConfig
from autogen.code_utils import content_str

# Utilities and tools (custom tool to be added soon)
from coding.utils import show_chat_history, display_session_msg, save_messages_to_json, paging
from coding.agenttools import extract_pdf_content, generate_wordcloud_from_pdf, update_market_data_and_show_preview

# Load environment variables
load_dotenv(override=True)

# Constants
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
placeholderstr = "Please input your command"
user_name = "Team02"
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
        ("generate_wordcloud_from_pdf", "Generate a word cloud from the entire PDF.", generate_wordcloud_from_pdf),
        ("fetch_market_data", "Fetch Market data from Yahoo Finance", update_market_data_and_show_preview)
    ]

    register_agent_methods(gemini_agent, user_proxy, methods_to_register)

    def generate_response(prompt):
        chat_result = user_proxy.initiate_chat(
            gemini_agent,
            message=prompt,
        )
        return chat_result.chat_history

    def chat(prompt: str):

        if "summary" in prompt.lower() or "summarize" in prompt.lower():
            from coding.agenttools import extract_pdf_content
            content = extract_pdf_content()
            st.write("### PDF Content Summary:")
            for i, page in enumerate(content, 1):
                st.write(f"**Page {i}**: {page[:500]}")  # Display first 500 characters of each page
            return

        elif "wordcloud" in prompt.lower():
            from coding.agenttools import generate_wordcloud_from_pdf
            image_path = generate_wordcloud_from_pdf()
            st.image(image_path, caption="Word Cloud from PDF")
            return

        elif "market" in prompt.lower() or "market data" in prompt.lower():
            from coding.agenttools import fetch_market_data  # Assuming it's in same file or imported
            df = fetch_market_data()
            if df is not None:
                st.write("### Market Data Preview:")
                st.dataframe(df.head())
            else:
                st.warning("No market data retrieved.")
            return

        response = generate_response(prompt)
        show_chat_history(st_c_chat, response, user_image)

    if prompt := st.chat_input(placeholder=placeholderstr, key="chat_bot"):
        chat(prompt)

if __name__ == "__main__":
    main()