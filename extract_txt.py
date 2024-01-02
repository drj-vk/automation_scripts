#%%

import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text

# Example usage
file_path = 'genai_metyis.pdf'
extracted_text = extract_text_from_pdf(file_path)
print(extracted_text)

#%%
extracted_text

# %%
import pytesseract
import pdf2image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(file_path):
    # Convert PDF to a list of images
    pages = pdf2image.convert_from_path(file_path, 500)

    # Process each page
    text = ''
    for page in pages:
        text += pytesseract.image_to_string(page) + '\n'

    return text

# Example usage
file_path = 'genai_metyis.pdf'
extracted_text = extract_text_from_pdf(file_path)
print(extracted_text)
# %%
