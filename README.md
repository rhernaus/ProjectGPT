# Project Manager with GPT-4

This application uses GPT-4, a state-of-the-art language model by OpenAI, to simulate a project manager who can provide expert answers to your questions across various fields.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Credits](#credits)

## Features

- Classify user input questions and select the top 3 most relevant Subject Matter Experts (SMEs) to provide answers.
- Consult with the selected SMEs to get their responses.
- Resolve and present the best answer from the SMEs.

## Requirements

- Python 3.6 or later
- OpenAI API key
- Streamlit
- Python-dotenv

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/rhernaus/ProjectGPT.git
   cd ProjectGPT
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:

   ```
   streamlit run app.py
   ```

2. Open the provided URL in your web browser.

3. Enter your question in the text area and click "Get Answers".

4. The app will display the selected Subject Matter Experts, their responses, and the best answer for your question.

## Credits

This application is built using:

- [OpenAI GPT-4](https://beta.openai.com/docs/models/gpt-4) for generating expert responses.
- [Streamlit](https://www.streamlit.io/) for creating the web interface.
