# chunk_text_with_page_tracking

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter 

# Assuming text_with_page_markers is obtained using extract_text_with_page_markers()
def chunk_text_with_page_tracking(
    text,
    chunk_size,
    chunk_overlap,
):
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )
    
    chunks = text_splitter.split_text(text)
    chunk_page_mapping = []
    
    for chunk in chunks:
        # Find the pages in the chunk by looking for the page markers
        start_page = None
        end_page = None

        flag_first_line = 1
        for line in chunk.splitlines():
            if "[[PAGE" in line:   # The notation '[[PAGE' originates from the splitting function, not from the document.
                page_num = int(line.split("[[PAGE ")[1].split("]]")[0])
                if start_page is None:
                    if flag_first_line == 1:
                        start_page = page_num
                    else:
                        # If it starts in the middle of the page, select start_page as the previous page.
                        start_page = page_num - 1
                end_page = page_num
            flag_first_line = 0

        # If the string "[[PAGE " is not found, it means there was no page change.
        if start_page is None:
            start_page = end_page_aux
            end_page = end_page_aux
        end_page_aux = end_page
        
        chunk_page_mapping.append({
            "chunk": chunk,
            "start_page": start_page,
            "end_page": end_page
        })
        
    return chunk_page_mapping