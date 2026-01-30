import PyPDF2
import docx
import io

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_type == 'docx':
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

def extract_text_from_pdf(file):
    pdf_text = ""
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            pdf_text += page.extract_text()
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return pdf_text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    docx_text = "\n".join([para.text for para in doc.paragraphs])
    return docx_text
