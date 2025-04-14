# extract_text_with_page_markers

from PyPDF2 import PdfReader
def extract_text_with_page_markers(pdf_path):
    '''
    Extract text from a pdf file.
    Add page number in the extraction.
    '''
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text_with_page_markers = []
        for i in range(len(reader.pages)):
            page = reader.pages[i].extract_text()
            # Add page marker
            text_with_page_markers.append(f"[[PAGE {i + 1}]]\n{page}")
    return '\n'.join(text_with_page_markers)