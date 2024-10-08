### Research Friend
Research friend is a simple research assistant tool built with langchain that takes a pdf, proofreads, identifies potential unsourced claims of fact, and points out unclear language. It then prints out a bulleted list of these issues along with the page number. You are then given the option for the model to incorporate corrections for these errors into a new document and save the corrected text to /corrected_texts (as a .txt in case further editing is needed)

It's a more scalable and efficient way of detecting errors since it will work with a pdf of any length and the prompt has been optimized. It's less copy and paste than using the ChatGPT app.

Note: unsourced claims of fact will  have  a [citation needed] comment inserted next to them

## Starting steps 
Make sure you place your pdfs in /pdf directory. 
One sample pdf with mistakes is included as an example.
## Prerequisites

Before running the tool, ensure that the following software is installed:

1. **Python 3.8+**: Install the latest version of Python from [here](https://www.python.org/downloads/).
2. **OpenAI API Key**: You need an API key from OpenAI to use their LLM models. Sign up for an API key at [OpenAI](https://beta.openai.com/signup/).
3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
## Setup Instructions

Follow the steps below to get the tool running on your local machine.

# Create a virtual environment
```bash
python -m venv venv
```

# Activate the virtual environment
# On macOS/Linux:
```bash
source venv/bin/activate
```
# On Windows:
```bash
venv\Scripts\activate
```

Create a .env file in the root of the project directory to store your OPENAI_API_KEY

(support for other models forthcoming)
## Run the script
```bash
python main.py
```

Run the main script to parse a PDF, generate error corrections, and save the corrected document.
You will be prompted to enter the path to your pdf, e.g pdf/sample1.pdf
After the edit suggestions are generated, you will be asked if you wish to have these changes performed by the model 
type y for yes . The edited text will be output to /corrected_texts and given a unique id.
Type n to terminate the script. 
