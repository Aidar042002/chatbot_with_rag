import os
from docling.document_converter import DocumentConverter

converter = DocumentConverter()


def pdf_to_md(pdf_path: str, output_path: str) -> str:
    try:
        result = converter.convert(pdf_path)
        markdown_content = result.document.export_to_markdown()

        output_file = os.path.join(output_path, os.path.basename(pdf_path).replace('.pdf', '.md'))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"PDF конвертирован: {output_file}")
        return output_file
    except Exception as e:
        print(f"Ошибка конвертации PDF: {e}")
        return None