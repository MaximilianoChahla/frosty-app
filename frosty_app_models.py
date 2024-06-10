import re
import streamlit as st
from openai import OpenAI
from PIL import Image
from streamlit_extras.stylable_container import stylable_container
from prompts import get_system_prompt
from langchain_together import ChatTogether

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
    if "error" not in st.session_state:
        st.session_state.error = None 

# Setup Streamlit Appearance
st.set_page_config(page_title="Snowflake Chatbot using Langchain, OpenAI, Streamlit and Snowflake", page_icon="images/favicon.svg")
st.title("☃️ Frosty")

initialize_session_state()

# Sidebar
with st.sidebar:
    st.title("Querying Snowflake Tables using Langchain, OpenAI and Streamlit")
    image = Image.open('images/frosty.png')
    with stylable_container(key="frosty_logo", css_styles="div[data-testid='stImage'] > img {width: 60%; margin: auto; border-radius: 50%;}"):
        st.image(image, caption='Frosty App')
    st.markdown("**Meet Frosty:** Your ultimate financial data companion. With streamlined access to Snowflake's data warehouse, Frosty empowers efficient analysis and informed decision-making. Revolutionize your financial insights today.")
    model = st.selectbox(
        "Which Generative AI model would you like to use?",
        ("gpt-3.5-turbo-0125", "meta-llama/Llama-3-70b-chat-hf", "Snowflake/snowflake-arctic-instruct", "togethercomputer/alpaca-7b", "google/gemma-7b-it"),
        index=0,
        disabled=st.session_state.disabled,
        placeholder="Select a model...",
        on_change=lambda: st.session_state.update(messages=[{"role": "system", "content": get_system_prompt()}], error=None) 
    )
    st.write("You selected:", f"**{model}**")
    with stylable_container(key="clean_button", css_styles="div[data-testid='stButton'] button {width: 100% !important;}"):
        st.button('Clear chat history :fire:', on_click=lambda: st.session_state.update(messages=[{"role": "system", "content": get_system_prompt()}], error=None))

# Initialize the chat messages history
if model == "gpt-3.5-turbo-0125":
    client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
else:
    client = ChatTogether(
        together_api_key = st.secrets.TOGETHER_AI_API_KEY,
        model = model
    )

# Processing chat messages
try:
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "results" in message:
                st.dataframe(message["results"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            if model == "gpt-3.5-turbo-0125":
                for delta in client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True):
                    response += (delta.choices[0].delta.content or "")
                    resp_container.markdown(response)
            else:
                for m in client.stream(st.session_state.messages):
                    response += (m.content)
                    resp_container.markdown(response)
            message = {"role": "assistant", "content": response}
            sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1)
                conn = st.connection("snowflake")
                message["results"] = conn.query(sql)
                st.dataframe(message["results"])
            st.session_state.messages.append(message)
except Exception as e:
    st.session_state.error = str(e)
    st.error(f"An error occurred: {e}")