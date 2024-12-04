import pandas as pd
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, sections):
        """
        Khởi tạo đối tượng DocumentProcessor với danh sách các đối tượng Document.

        Args:
            sections (list of Document): Danh sách các đối tượng Document cần xử lý.
        """
        self.sections = sections

    def process_documents(self):
        """
        Chia các đối tượng Document thành các phần nhỏ hơn và tạo các đối tượng Document mới.

        Returns:
            list of Document: Danh sách các đối tượng Document đại diện cho các phần nhỏ của tài liệu.
        """
        chunks = []
        chunk_size = 1000  # Kích thước tối đa của mỗi đoạn văn bản

        for doc in self.sections:
            section_text = doc.page_content
            # Chia nhỏ phần văn bản thành các đoạn nhỏ hơn
            while len(section_text) > chunk_size:
                # Tìm vị trí của khoảng trắng gần nhất trong kích thước đoạn văn bản
                split_pos = section_text.rfind(' ', 0, chunk_size)
                if split_pos == -1:
                    split_pos = chunk_size
                chunk_text = section_text[:split_pos].strip()
                section_text = section_text[split_pos:].strip()
                new_doc = Document(page_content=chunk_text)
                chunks.append(new_doc)
            # Thêm đoạn văn bản còn lại (nếu có)
            if section_text:
                new_doc = Document(page_content=section_text)
                chunks.append(new_doc)

        return chunks

    def save_chunks_to_excel(self, file_path):
        """
        Lưu các đoạn văn bản đã chia nhỏ vào file Excel.

        Args:
            file_path (str): Đường dẫn tới file Excel.
        """
        # Xử lý các Document và chia thành các phần nhỏ
        chunks = self.process_documents()

        # Tạo danh sách các đoạn văn bản từ các đối tượng Document
        chunk_texts = [chunk.page_content for chunk in chunks]

        # Sử dụng pandas để lưu danh sách các đoạn văn bản vào file Excel
        df = pd.DataFrame({'Chunks': chunk_texts})
        df.to_excel(file_path, index=False)


