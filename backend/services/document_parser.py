import io
import re

class DocumentParserService:
    @staticmethod
    def parse_plain_text(text_content: str) -> str:
        """Clean and normalize plain text input."""
        if not text_content:
            return ""
        # Remove unusual control characters while keeping whitespace
        text = re.sub(r'[\r\n]+', '\n', text_content)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF file bytes using PyMuPDF (fitz) or fallback."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            for page in doc:
                extracted_pages.append(page.get_text())
            text = "\n".join(extracted_pages)
            return DocumentParserService.parse_plain_text(text)
        except Exception as e:
            # Basic fallback text extraction if fitz is unavailable or fails
            try:
                # Simple regex filter for ASCII text inside PDF bytes
                raw = file_bytes.decode('latin-1', errors='ignore')
                strings = re.findall(r'\(([^\(\)]+)\)', raw)
                extracted = " ".join(strings)
                return DocumentParserService.parse_plain_text(extracted)
            except Exception:
                raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        """Extract text from DOCX file bytes using python-docx."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            full_text.append(cell.text)
            text = "\n".join(full_text)
            return DocumentParserService.parse_plain_text(text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")
