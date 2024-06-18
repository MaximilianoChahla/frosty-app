import re
import smtplib
import streamlit as st
from openai import OpenAI
from PIL import Image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from streamlit_extras.stylable_container import stylable_container
from prompts_csv import get_system_prompt, get_user_prompt_with_csv_context
from langchain_together import ChatTogether
import pandas as pd
import pandasql as psql

# Initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    st.session_state.setdefault("messages", [{"role": "system", "content": get_system_prompt()}])
    st.session_state.setdefault("disabled", False)
    st.session_state.setdefault("error", None)
    st.session_state.setdefault("email_sent", set())
    st.session_state.setdefault("uploaded_data", None)
    st.session_state.setdefault("user_prompt", "")

# Function to send email to multiple recipients
def send_email(to_addresses, subject, body, attachment_name, attachment_data):
    """Send an email with an attachment to multiple recipients."""
    from_address = st.secrets["EMAIL"]["ADDRESS"]
    from_password = st.secrets["EMAIL"]["PASSWORD"]

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = ", ".join(to_addresses)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Use 'html' instead of 'plain'

    part = MIMEBase('application', "octet-stream")
    part.set_payload(attachment_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_address, from_password)
            for to_address in to_addresses:
                server.sendmail(from_address, to_address, msg.as_string())
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to create email button and send email if clicked
def send_email_button(email_addresses, message, idx, user_prompt):
    """Create an email button to send the results via email."""
    if st.button("Send to email", key=f"send_{idx}"):
        if all(email.strip() for email in email_addresses):
            csv_data = message["results"].to_csv(index=False)
            email_body = f"""
            <html>
            <body>
                <p><strong>User Prompt:</strong></p>
                <p>{user_prompt}</p>
                <br>
                <p>Please find the attached data table.</p>
            </body>
            </html>
            """
            send_email(
                to_addresses=[email.strip() for email in email_addresses],
                subject="Your Requested Data Table",
                body=email_body,
                attachment_name="table_data.csv",
                attachment_data=csv_data
            )
            st.session_state.email_sent.add(idx)
        else:
            st.warning("Please enter valid email addresses.")

# Function to display chat messages
def display_chat_messages():
    """Display chat messages in the Streamlit app."""
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "results" in message:
                st.dataframe(message["results"])
                if idx not in st.session_state.email_sent:
                    send_email_button(email_addresses, message, idx, st.session_state.user_prompt)

# Function to process chat input and generate a response
def process_chat_input(model, client):
    """Process user input and generate a response from the selected AI model."""
    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.session_state.user_prompt = prompt  # Save the user's prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            prompt_container = st.empty()
            prompt_container.markdown(prompt)


    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = generate_response(model, client)
            message = {"role": "assistant", "content": response}

            # Check and handle multiple SQL queries
            handle_sql_queries(response, message)

            st.session_state.messages.append(message)

# Function to generate AI response
def generate_response(model, client):
    """Generate a response from the AI model."""
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
    return response

# Function to handle SQL queries in AI response
def handle_sql_queries(response, message):
    """Handle SQL queries found in the AI response."""
    sql_matches = re.findall(r"```sql\n(.*?)\n```", response, re.DOTALL)
    if len(sql_matches) > 1:
        st.warning("Only one SQL query can be processed at a time. Please refine your request.")
        response = "It looks like you provided multiple SQL queries. Please refine your request to include only one SQL query."
        message["content"] = response
    elif len(sql_matches) == 1:
        execute_sql_query(sql_matches[0], message)

# Function to execute a single SQL query
def execute_sql_query(sql, message):
    """Execute a single SQL query against the uploaded data."""
    if st.session_state.uploaded_data is not None:
        df_name = 'uploaded_data'
        locals()[df_name] = st.session_state.uploaded_data

        sql = replace_table_name_in_query(sql, df_name)

        try:
            query_results = psql.sqldf(sql, locals())
            message["results"] = query_results
            st.dataframe(message["results"])

            # Email sending logic
            if len(st.session_state.messages) not in st.session_state.email_sent:
                send_email_button(email_addresses, message, len(st.session_state.messages), st.session_state.user_prompt)
        except Exception as e:
            st.error(f"Error executing SQL query: {e}")
    else:
        st.error("No CSV file uploaded to query.")

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    """Process and display the uploaded CSV file."""
    if uploaded_file is not None:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV file:")
        st.dataframe(st.session_state.uploaded_data)

        csv_columns = list(st.session_state.uploaded_data.columns)
        csv_context_prompt = get_user_prompt_with_csv_context(csv_columns)

        st.session_state.messages.append({"role": "system", "content": csv_context_prompt})

# Function to replace table names in SQL queries with DataFrame names
def replace_table_name_in_query(query, df_name):
    """Replace table names in SQL query with the DataFrame name."""
    pattern = re.compile(r'\bFROM\s+(\w+)|\bJOIN\s+(\w+)', re.IGNORECASE)
    return pattern.sub(f'FROM {df_name}', query)

# Setup Streamlit Appearance
st.set_page_config(page_title="CSV Chatbot using Langchain, OpenAI and Streamlit", page_icon="images/favicon.svg")
st.title("☃️ Frosty")

initialize_session_state()

# Sidebar
with st.sidebar:
    st.title("Querying CSV files using Langchain, OpenAI and Streamlit")
    image = Image.open('images/frosty.png')
    with stylable_container(key="frosty_logo", css_styles="div[data-testid='stImage'] > img {width: 60%; margin: auto; border-radius: 50%;}"):
        st.image(image, caption='Frosty App')
    st.markdown("**Meet Frosty:** Your ultimate financial data companion. With provided CSV files, Frosty empowers efficient analysis and informed decision-making. Revolutionize your financial insights today.")
    
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

    email_addresses = st.text_area("Enter email addresses (separated by commas):", "").split(',')

    uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=["csv"])
    process_uploaded_file(uploaded_file)

# Initialize the chat client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) if model == "gpt-3.5-turbo-0125" else ChatTogether(
    together_api_key=st.secrets["TOGETHER_AI_API_KEY"], model=model)

# Main logic
try:
    display_chat_messages()
    process_chat_input(model, client)
except Exception as e:
    st.session_state.error = str(e)
    st.error(f"An error occurred: {e}")
