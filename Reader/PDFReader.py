import fitz  # PyMuPDF
from typing import List, Optional
from pathlib import Path

class PDFReader:
    def __init__(self, file_paths, return_full_document: Optional[bool] = False) -> None:
        """
        Khởi tạo PDFReader với một danh sách đường dẫn tệp hoặc một đường dẫn tệp duy nhất.
        """
        # Đảm bảo file_paths luôn là danh sách
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        self.return_full_document = return_full_document

    def read_pdf_document(self, file_path: Path) -> List[str]:
        """
        Đọc tài liệu PDF và trả về nội dung dưới dạng danh sách chuỗi (mỗi trang là một chuỗi).
        """
        pdf_document = fitz.open(str(file_path))
        pages = []

        for page_num in range(pdf_document.page_count):
            page_text = pdf_document.load_page(page_num).get_text()
            pages.append(page_text)

        return pages

    def is_uppercase_title(self, text: str) -> bool:
        """
        Kiểm tra xem văn bản có phải là tiêu đề viết hoa toàn bộ không.
        """
        stripped_text = text.strip()
        return stripped_text.isupper() and len(stripped_text) > 0

    def split_by_format(self, pages: List[str]) -> List[str]:
        """
        Phân chia nội dung PDF thành các phần dựa trên định dạng tiêu đề (viết hoa).
        """
        sections = []
        current_section = []

        for page in pages:
            for line in page.splitlines():
                if self.is_uppercase_title(line):
                    # Lưu phần hiện tại nếu có
                    if current_section:
                        sections.append("\n".join(current_section))
                        current_section = []
                    current_section.append(line)
                else:
                    current_section.append(line)

        # Thêm phần cuối cùng
        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def process_documents(self) -> List['Document']:
        """
        Process all the PDF documents in file_paths and return them as Document objects.
        """
        all_sections = []

        for file_path in self.file_paths:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"File does not exist: {file_path}")
                continue

            pages = self.read_pdf_document(file_path)
            sections = self.split_by_format(pages)

            # Create Document objects from the sections
            documents = [self.Document(content=section) for section in sections]
            all_sections.extend(documents)

        return all_sections

    class Document:
        def __init__(self, content, metadata=None):
            self.page_content = content
            self.text = content  # Thêm thuộc tính 'text' để tương thích
            self.metadata = metadata if metadata is not None else {}

        def __str__(self):
            return f"Document(content={self.page_content[:50]}..., metadata={self.metadata})"

