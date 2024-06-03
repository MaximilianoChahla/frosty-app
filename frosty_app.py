import re
import streamlit as st
from openai import OpenAI
from PIL import Image
from prompts import get_system_prompt
from streamlit_extras.stylable_container import stylable_container

# ######################################
# DEFINE METHODS
# ######################################

def init_chat_history():
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# ######################################
# SETUP STREAMLIT APPEARANCE
# ######################################

# Config webpage title and icon
st.set_page_config(
    page_title = "Snowflake Chatbot using Langchain, OpenAI, Streamlit and Snowflake",
    page_icon = "images/favicon.svg"
)

# Config title for the main webpage container
st.title("☃️ Frosty")

# Add a left sidebar
with st.sidebar:
    st.title("Querying Snowflake Tables using Langchain, OpenAI and Streamlit")

    # Add style to the Frosty logo
    image = Image.open('images/frosty.png')
    with stylable_container(
        key="frosty_logo",
        css_styles="""
            div[data-testid="stImage"] > img {
                width: 60%;
                margin: auto;
                border-radius: 50%;
            }
        """
    ):
        st.image(image, caption = 'Frosty App')

    # Add a description about the Frosty App
    st.markdown(
        """
        **Meet Frosty:** Your ultimate financial data companion. With streamlined access to Snowflake's data warehouse, Frosty empowers efficient analysis and informed decision-making. Revolutionize your financial insights today.
    """
    )

    # Add style to the Clean chat button
    with stylable_container(
        key="clean_button",
        css_styles="""
            div[data-testid="stButton"] button {
                width: 100% !important;
            }
        """
    ):
        st.button('Clean chat :fire:', on_click = init_chat_history)

# ######################################
# OPENAI LOGIC
# ######################################

# Initialize the chat messages history
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = ""
        resp_container = st.empty()
        
        for delta in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += (delta.choices[0].delta.content or "")
            resp_container.markdown(response)
        
        message = {"role": "assistant", "content": response}
        
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        
        if sql_match:
            sql = sql_match.group(1)
            conn = st.connection("snowflake")
            message["results"] = conn.query(sql)
            st.dataframe(message["results"])
        
        st.session_state.messages.append(message)