import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import pdfplumber
import nltk
import uuid

# Load environment variables and api key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


# Step 1: PDF parsing
def extract_text_from_pdf(pdf_file):
    texts_by_page = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Handle potential encoding issues by ignoring problematic characters
            page_text = page.extract_text()
            if page_text:
                texts_by_page.append(page_text.encode('utf-8', errors='ignore').decode('utf-8'))
    return texts_by_page

# Step 2: NLTK tokenization setup (if needed for future processing)
nltk.download('punkt')

# Step 3: Define LLM interaction for scrutinizing text
def scrutinize_text(llm_chain, text, page_number):
    inputs = {
        "text": text,
        "page_number": page_number
    }
    return llm_chain.invoke(inputs)

# Step 3.5: Define the `edit_text` function to apply corrections
def edit_text(llm, text, corrections):
    # Define a prompt to apply the corrections to the text
    prompt = f"""
    You are a meticulous editor. Here are some corrections that need to be applied:
    {corrections}
    Note: for unsourced statements of fact, add [citation_needed] at the end of the offending sentence.
    Text:
    {text}

    Please return the corrected version of the text.
    """
    # Send the prompt to the LLM and return the result
    return llm.run(prompt)

# Step 4: Process PDF file and generate error report
def analyze_pdf_for_errors(pdf_file):
    # Parse the PDF into text per page
    texts_by_page = extract_text_from_pdf(pdf_file)

    # Initialize the Langchain prompt template
    prompt_template = PromptTemplate(
        template="""
        You are a meticulous editor. Carefully scrutinize this document for:
        - typos
        - unsourced statements of fact
        - overwritten or inelegant passages.

        Text:
        {text}

        Please return a bulleted list of errors you found on page {page_number}, specifying what's wrong with each line.
        """, 
        input_variables=["text", "page_number"]
    )
    
    # Initialize LLM
    llm = OpenAI(openai_api_key=api_key)
    chain = prompt_template | llm  # Use the recommended prompt|LLM syntax

    error_report = []
    
    for page_num, text in enumerate(texts_by_page, start=1):
        result = scrutinize_text(chain, text, page_num)
        if result:
            error_report.append(f"Page {page_num}:\n{result}")
    
    return "\n".join(error_report), texts_by_page  # Returning both the report and the texts by page

# Step 5: Function to apply edits based on the error report
def make_edits(llm, texts_by_page, error_report):
    corrected_pages = []
    for page_num, page_text in enumerate(texts_by_page, start=1):
        page_errors = [error for error in error_report if f"Page {page_num}" in error]
        if page_errors:
            corrections = "\n".join(page_errors)
            corrected_text = edit_text(llm, page_text, corrections)
            corrected_pages.append(corrected_text)
        else:
            corrected_pages.append(page_text)  # No corrections, keep the original text
    return corrected_pages

# Step 6: Write the corrected text back into a new .txt file
def save_corrected_txt(corrected_texts, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        for page_num, corrected_text in enumerate(corrected_texts, start=1):
            file.write(f"Page {page_num}:\n{corrected_text}\n\n")
    print(f"Corrected text saved to {output_path}")

# Step 7: Main program loop
if __name__ == "__main__":
    pdf_path = input('Please specify the path to your PDF file (e.g., pdfs/example.pdf): ')
    
    # Analyze the PDF for errors
    report, texts_by_page = analyze_pdf_for_errors(pdf_path)
    
    print("Errors Found:")
    print(report)
    
    # Loop to ensure valid user input
    implement_changes = input('Would you like me to implement these suggestions? (y/n): ').lower()
    while implement_changes not in ['y', 'n']:
        implement_changes = input('Invalid input. Please enter "y" for yes or "n" for no: ').lower()
    
    # Apply changes if the user chooses 'y'
    if implement_changes == 'y':
        llm = OpenAI(openai_api_key=api_key)  # Initialize LLM for making edits
        corrected_texts = make_edits(llm, texts_by_page, report)
        
        print("Edits applied. Here are the corrected texts per page:")
        for page_num, corrected_text in enumerate(corrected_texts, start=1):
            print(f"Page {page_num}:\n{corrected_text}")
        
        # Create directory for corrected text files if it doesn't exist
        os.makedirs('./corrected_texts', exist_ok=True)
        
        # Save the corrected text file to the specified directory
        unique_filename = f"corrected_document_{uuid.uuid4()}.txt"
        corrected_txt_path = os.path.join('./corrected_texts', unique_filename)
        save_corrected_txt(corrected_texts, corrected_txt_path)
    else:
        print("No changes were made.")