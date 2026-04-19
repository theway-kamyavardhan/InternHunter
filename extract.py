import fitz
import sys

def extract():
    doc = fitz.open('kamyavardhan-dave-resume.pdf')
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open('master_resume.md', 'w') as f:
        f.write("# Master Resume\n\n")
        f.write(text)

if __name__ == "__main__":
    extract()
