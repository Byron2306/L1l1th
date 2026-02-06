from pathlib import Path
import zipfile, re

def extract_docx_text(path: Path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
    text = re.sub(r'<w:tab/>', '\t', xml)
    text = re.sub(r'</w:p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text

files = [
    Path(r'C:\Users\User\Desktop\Marker\Rubric-1.docx'),
    Path(r'C:\Users\User\Desktop\Marker\Rubric2.docx'),
    Path(r'C:\Users\User\Desktop\Marker\UTEW221_Assignment2_Template_2025.docx'),
    Path(r'C:\Users\User\Desktop\Marker\Individual Assignment 1.docx'),
]
for f in files:
    text = extract_docx_text(f)
    out = f.with_suffix('.txt')
    out.write_text(text, encoding='utf-8')
    print('Wrote', out)
