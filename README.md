# Frosty CSV Chatbot

Frosty is an interactive chatbot built using Streamlit, LangChain, Together AI, and pandas. It allows users to upload CSV files and interactively query them using natural language. Frosty leverages large language models to convert user prompts into SQL queries, execute them on the uploaded data, and display the results. Additionally, users can send the query results to specified email addresses directly from the app.

[Frosty App](https://frosty-csv.streamlit.app/)

## Table of Contents

   - [Features](#features)
   - [Demo](#demo)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
   - [Project Structure](#project-structure)
   - [Usage](#usage)
   - [Customization](#customization)
   - [Contributing](#contributing)
   - [License](#license)
   - [Acknowledgments](#acknowledgments)
   - [Contact](#contact)

## Features

- **Natural Language Querying:** Ask questions in plain English, and Frosty will generate and execute the corresponding SQL queries on your CSV data.
- **CSV File Upload:** Upload your own CSV files for analysis.
- **Multiple AI Models:** Choose from different AI models provided by Together AI.
- **Email Results:** Send query results via email to multiple recipients directly from the app.
- **Interactive Chat Interface:** Engage in a conversational interface with the assistant.
- **State Preservation:** The assistant retains context across interactions, even when switching AI models.

## Demo

[Frosty App](https://frosty-csv.streamlit.app/)

## Prerequisites

- Python 3.7 or higher
- Together AI API Key (for accessing AI models)
- Email account credentials (for sending emails via SMTP)
- Streamlit account (optional, for deployment)

## Installation

1. **Clone the Repository**

		git clone https://github.com/your-username/frosty-csv-chatbot.git
		cd frosty-csv-chatbot

2. **Create a Virtual Environment**

		python -m venv venv
		source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install Dependencies**

		pip install -r requirements.txt

	**Contents of requirements.txt:**

	    streamlit
	    pandas
	    pandasql
	    Pillow
	    streamlit-extras
	    langchain-together

## Configuration

1. **Setup Secrets**

	Create a `.streamlit` directory in the root of your project if it doesn't exist:

		mkdir .streamlit

	Create a `secrets.toml` file inside the `.streamlit` directory:

		touch .streamlit/secrets.toml

	Add the following to `secrets.toml`:

		[EMAIL]
		ADDRESS = "your_email@example.com"
		PASSWORD = "your_email_password"

		[TOGETHER_AI]
		TOGETHER_AI_API_KEY= "your_together_ai_api_key"

	Replace placeholder values with your actual credentials.
	
2. **Email Configuration**

- Ensure that your email provider supports SMTP and that you have enabled SMTP access.
- For Gmail users, you may need to enable Less Secure Apps or use an App Password if you have 2FA enabled.

## Project Structure
```
frosty-csv-chatbot/
├── images/
│   └── frosty.png
├── frosty_csv.py
├── prompts_csv.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```
- `frosty_csv.py`: Main Streamlit app script.
- `prompts_csv.py`: Contains prompt templates for the assistant.
- `images/`: Directory containing images used in the app.
- `requirements.txt`: Lists all Python dependencies.
- `.streamlit/secrets.toml`: Contains secret keys and credentials.

## Usage

1. **Run the Streamlit App**

		streamlit run frosty_csv.py

2. **Interact with Frosty**
- **Upload a CSV File:** Use the file uploader in the sidebar to upload your CSV file.
- **Select an AI Model:** Choose your preferred AI model from the dropdown.
- **Enter Email Addresses:** Provide email addresses to send query results.
- **Ask Questions:** Use the chat input to ask questions about your data.
- **Send Results via Email:** Click the "Send to email" button to email the results.

## Customization

### Modifying Prompts

`prompts_csv.py` contains functions that generate prompts for the assistant.

	# prompts_csv.py

	def get_system_prompt():
	    return "You are Frosty, an assistant that helps users query their CSV files."

	def get_user_prompt_with_csv_context(csv_columns):
	    return f"The CSV file has the following columns: {', '.join(csv_columns)}."

Customize these functions to change how the assistant interacts.

### Changing AI Models

The app uses Together AI models. Update the model list in frosty_csv.py if needed.

	model = st.selectbox(
	    "Which Generative AI model would you like to use?",
	    (
	        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
	        "google/gemma-2-27b-it",
	        "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
	    ),
	    index=0,
	    disabled=st.session_state.disabled,
	    placeholder="Select a model...",
	)

### Updating Email Functionality

The email sending function uses SMTP. Modify the `send_email` function in `frosty_csv.py` to change the email template or to use a different email service.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

	Click the "Fork" button at the top right corner of the repository page.

2. **Clone Your Fork**

		git clone https://github.com/your-username/frosty-csv-chatbot.git

3. **Create a New Branch**

		git checkout -b feature/your-feature-name

4. **Make Changes and Commit**
		
		git add .
		git commit -m "Add your commit message"

5. **Push to Your Fork**

	    git push origin feature/your-feature-name

6. **Submit a Pull Request**
	
	Go to the original repository and click on "Pull Requests" to submit your PR.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Streamlit for the interactive web app framework.
- LangChain and Together AI for AI model integration.
- pandas and pandasql for data manipulation and SQL querying.
- Pillow for image handling.
- Streamlit Extras for additional Streamlit components.

## Contact

For any questions or suggestions, please open an issue or contact maxichahla@gmail.com.

Enjoy using Frosty for your data analysis tasks!